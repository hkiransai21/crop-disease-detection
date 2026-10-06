"""CPU latency, throughput, and accuracy benchmarking comparing FP32 vs INT8 ONNX models."""
import os
import sys
import time
import json
import platform
import argparse
from pathlib import Path
from typing import Dict, Any, List

import yaml
import numpy as np
import onnxruntime as ort
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm

from ml.src.datasets import PlantVillageDataset
from ml.src.transforms import get_eval_transforms


def measure_latency_and_accuracy(
    model_path: Path,
    dataset: PlantVillageDataset,
    num_warmup: int = 10,
    num_runs: int = 100
) -> Dict[str, Any]:
    """Measure single-image CPU inference latency (median, p95) and full test-split accuracy."""
    print(f"\nBenchmarking {model_path.name}...")
    
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    
    # 1. Latency Measurement (single image)
    dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
    
    # Warmup
    for _ in range(num_warmup):
        _ = session.run(None, {input_name: dummy_input})
        
    latencies_ms = []
    for _ in range(num_runs):
        t0 = time.perf_counter()
        _ = session.run(None, {input_name: dummy_input})
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)
        
    latencies_ms = np.array(latencies_ms)
    median_latency = float(np.median(latencies_ms))
    mean_latency = float(np.mean(latencies_ms))
    p95_latency = float(np.percentile(latencies_ms, 95))
    p99_latency = float(np.percentile(latencies_ms, 99))
    
    # 2. Test-set Accuracy & F1 measurement
    print(f"Evaluating accuracy on full test set ({len(dataset)} samples)...")
    from torch.utils.data import DataLoader
    test_loader = DataLoader(dataset, batch_size=64, shuffle=False, num_workers=2)
    all_preds = []
    all_targets = []
    
    for images, targets in tqdm(test_loader, desc=f"Eval {model_path.name}"):
        input_np = images.numpy()
        logits = session.run(None, {input_name: input_np})[0]
        preds = np.argmax(logits, axis=1)
        all_preds.extend(preds)
        all_targets.extend(targets.numpy())
        
    acc = float(accuracy_score(all_targets, all_preds))
    macro_f1 = float(f1_score(all_targets, all_preds, average="macro", zero_division=0))
    
    file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    
    return {
        "model_file": model_path.name,
        "file_size_mb": round(file_size_mb, 2),
        "test_accuracy": round(acc, 4),
        "test_macro_f1": round(macro_f1, 4),
        "num_runs": num_runs,
        "latency_median_ms": round(median_latency, 2),
        "latency_mean_ms": round(mean_latency, 2),
        "latency_p95_ms": round(p95_latency, 2),
        "latency_p99_ms": round(p99_latency, 2),
        "throughput_fps": round(1000.0 / median_latency, 1)
    }


def run_benchmark(config_path: str = "ml/configs/train_config.yaml", num_runs: int = 100) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    fp32_path = Path(config["artifacts"]["onnx_model_path"])
    int8_path = Path(config["artifacts"]["quantized_model_path"])
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    image_size = config["data"]["image_size"]
    test_dataset = PlantVillageDataset(
        config["data"]["manifest_path"],
        split="test",
        transform=get_eval_transforms(image_size)
    )
    
    fp32_res = measure_latency_and_accuracy(fp32_path, test_dataset, num_runs=num_runs)
    int8_res = measure_latency_and_accuracy(int8_path, test_dataset, num_runs=num_runs)
    
    acc_diff = fp32_res["test_accuracy"] - int8_res["test_accuracy"]
    speedup = fp32_res["latency_median_ms"] / int8_res["latency_median_ms"] if int8_res["latency_median_ms"] > 0 else 1.0
    
    benchmark_data = {
        "hardware": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count()
        },
        "fp32_model": fp32_res,
        "int8_model": int8_res,
        "comparison": {
            "accuracy_drop": round(acc_diff, 4),
            "latency_speedup_factor": round(speedup, 2),
            "size_reduction_pct": round((1.0 - (int8_res["file_size_mb"] / fp32_res["file_size_mb"])) * 100, 2),
            "recommendation": "Ship INT8 quantized model for CPU production deployment." if acc_diff < 0.01 else "Ship FP32 model due to quantization accuracy drop."
        }
    }
    
    with open(reports_dir / "benchmark_report.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)
        
    print(f"\n================ BENCHMARK RESULTS ================")
    print(f"FP32: {fp32_res['file_size_mb']} MB | Median Latency: {fp32_res['latency_median_ms']} ms | Acc: {fp32_res['test_accuracy']*100:.2f}%")
    print(f"INT8: {int8_res['file_size_mb']} MB | Median Latency: {int8_res['latency_median_ms']} ms | Acc: {int8_res['test_accuracy']*100:.2f}%")
    print(f"Speedup: {speedup:.2f}x | Accuracy Drop: {acc_diff*100:.2f}%")
    print(f"===================================================\n")
    return benchmark_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    parser.add_argument("--runs", type=int, default=100)
    args = parser.parse_args()
    run_benchmark(args.config, num_runs=args.runs)

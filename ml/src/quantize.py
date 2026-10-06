"""Dynamic INT8 Quantization of ONNX model for high-efficiency CPU edge deployment."""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

import yaml
from onnxruntime.quantization import quantize_dynamic, QuantType


def run_quantization(config_path: str = "ml/configs/train_config.yaml") -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    onnx_fp32_path = Path(config["artifacts"]["onnx_model_path"])
    onnx_int8_path = Path(config["artifacts"]["quantized_model_path"])
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not onnx_fp32_path.exists():
        raise FileNotFoundError(f"FP32 ONNX model not found at {onnx_fp32_path}. Run export_onnx.py first.")

    print(f"Applying Dynamic INT8 Quantization: {onnx_fp32_path} -> {onnx_int8_path}...")
    quantize_dynamic(
        model_input=str(onnx_fp32_path),
        model_output=str(onnx_int8_path),
        weight_type=QuantType.QInt8
    )

    fp32_size_mb = os.path.getsize(onnx_fp32_path) / (1024 * 1024)
    int8_size_mb = os.path.getsize(onnx_int8_path) / (1024 * 1024)
    compression_ratio = fp32_size_mb / int8_size_mb if int8_size_mb > 0 else 1.0

    print(f"FP32 Model Size: {fp32_size_mb:.2f} MB")
    print(f"INT8 Model Size: {int8_size_mb:.2f} MB ({compression_ratio:.2f}x compression)")

    quant_report = {
        "fp32_path": str(onnx_fp32_path),
        "fp32_size_mb": round(fp32_size_mb, 2),
        "int8_path": str(onnx_int8_path),
        "int8_size_mb": round(int8_size_mb, 2),
        "compression_ratio": round(compression_ratio, 2)
    }

    with open(reports_dir / "quantization_report.json", "w") as f:
        json.dump(quant_report, f, indent=2)

    return quant_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    run_quantization(args.config)

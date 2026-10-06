"""Export PyTorch model to ONNX and verify numerical parity."""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

import yaml
import numpy as np
import torch
import onnx
import onnxruntime as ort

from ml.src.train import create_model


def export_to_onnx(config_path: str = "ml/configs/train_config.yaml") -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    best_model_path = Path(config["artifacts"]["best_model_path"])
    onnx_model_path = Path(config["artifacts"]["onnx_model_path"])
    onnx_model_path.parent.mkdir(parents=True, exist_ok=True)
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not best_model_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at {best_model_path}")

    checkpoint = torch.load(best_model_path, map_location="cpu")
    classes = checkpoint["classes"]
    num_classes = len(classes)

    model = create_model(
        model_name=config["model"]["architecture"],
        num_classes=num_classes,
        pretrained=False
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    image_size = config["data"]["image_size"]
    dummy_input = torch.randn(1, 3, image_size, image_size, dtype=torch.float32)

    print(f"Exporting model to ONNX: {onnx_model_path}...")
    torch.onnx.export(
        model,
        dummy_input,
        str(onnx_model_path),
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "logits": {0: "batch_size"}
        },
        dynamo=False
    )

    # Check ONNX model validity
    onnx_model = onnx.load(str(onnx_model_path))
    onnx.checker.check_model(onnx_model)
    print("ONNX model structure checked successfully.")

    # Numerical Parity Verification on test batch
    print("Verifying numerical parity between PyTorch and ONNX Runtime...")
    test_batch = torch.randn(8, 3, image_size, image_size, dtype=torch.float32)

    with torch.no_grad():
        torch_logits = model(test_batch).numpy()
        torch_probs = torch.softmax(torch.from_numpy(torch_logits), dim=1).numpy()

    ort_session = ort.InferenceSession(str(onnx_model_path), providers=["CPUExecutionProvider"])
    ort_inputs = {ort_session.get_inputs()[0].name: test_batch.numpy()}
    ort_logits = ort_session.run(None, ort_inputs)[0]
    
    # Calculate Softmax for ORT
    exp_ort = np.exp(ort_logits - np.max(ort_logits, axis=1, keepdims=True))
    ort_probs = exp_ort / np.sum(exp_ort, axis=1, keepdims=True)

    max_logit_diff = float(np.max(np.abs(torch_logits - ort_logits)))
    mean_logit_diff = float(np.mean(np.abs(torch_logits - ort_logits)))
    max_prob_diff = float(np.max(np.abs(torch_probs - ort_probs)))

    print(f"Parity Check Results:")
    print(f"  Max Logit Difference: {max_logit_diff:.6e}")
    print(f"  Mean Logit Difference: {mean_logit_diff:.6e}")
    print(f"  Max Probability Difference: {max_prob_diff:.6e}")

    assert max_prob_diff < 1e-4, f"Parity mismatch: max prob diff {max_prob_diff} exceeds threshold 1e-4!"
    print("Numerical parity test PASSED.")

    onnx_size_mb = os.path.getsize(onnx_model_path) / (1024 * 1024)
    parity_report = {
        "onnx_model_path": str(onnx_model_path),
        "onnx_file_size_mb": round(onnx_size_mb, 2),
        "max_logit_difference": max_logit_diff,
        "mean_logit_difference": mean_logit_diff,
        "max_probability_difference": max_prob_diff,
        "parity_verified": True
    }

    with open(reports_dir / "onnx_parity_report.json", "w") as f:
        json.dump(parity_report, f, indent=2)

    return parity_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    export_to_onnx(args.config)

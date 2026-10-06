"""Model calibration using Expected Calibration Error (ECE), Reliability Diagrams, and Temperature Scaling."""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Tuple, Dict, Any

import yaml
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from ml.src.datasets import PlantVillageDataset
from ml.src.transforms import get_eval_transforms
from ml.src.train import create_model, get_device


class TemperatureScaler(nn.Module):
    """Learns a single temperature parameter T to calibrate softmax probabilities via NLL loss on validation set."""
    def __init__(self):
        super().__init__()
        self.log_temperature = nn.Parameter(torch.zeros(1))  # T = exp(0) = 1.0

    @property
    def temperature(self) -> torch.Tensor:
        return torch.exp(self.log_temperature)

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        return logits / self.temperature

    def fit(self, logits: torch.Tensor, labels: torch.Tensor, lr: float = 0.05, max_iter: int = 100) -> float:
        optimizer = torch.optim.LBFGS([self.log_temperature], lr=lr, max_iter=max_iter)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            scaled_logits = self.forward(logits)
            loss = criterion(scaled_logits, labels)
            loss.backward()
            return loss

        optimizer.step(eval_loss)
        return float(self.temperature.item())


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Compute Expected Calibration Error (ECE) and bin statistics."""
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    ece = 0.0
    bin_accs = []
    bin_confs = []
    bin_counts = []

    n_samples = len(labels)

    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
            bin_accs.append(accuracy_in_bin)
            bin_confs.append(avg_confidence_in_bin)
            bin_counts.append(int(np.sum(in_bin)))
        else:
            bin_accs.append(0.0)
            bin_confs.append((bin_lower + bin_upper) / 2)
            bin_counts.append(0)

    return float(ece), np.array(bin_accs), np.array(bin_confs), np.array(bin_counts)


def plot_reliability_diagram(
    bin_accs_uncal: np.ndarray,
    bin_confs_uncal: np.ndarray,
    ece_uncal: float,
    bin_accs_cal: np.ndarray,
    bin_confs_cal: np.ndarray,
    ece_cal: float,
    output_path: Path
):
    """Plot before vs after temperature scaling reliability diagram."""
    n_bins = len(bin_accs_uncal)
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Uncalibrated
    ax1.plot([0, 1], [0, 1], "--", color="gray", label="Perfect Calibration")
    ax1.bar(bin_centers, bin_accs_uncal, width=1.0 / n_bins, alpha=0.6, edgecolor="black", label="Outputs")
    ax1.set_title(f"Uncalibrated (ECE = {ece_uncal*100:.2f}%)")
    ax1.set_xlabel("Confidence")
    ax1.set_ylabel("Accuracy")
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1])
    ax1.legend()
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Calibrated
    ax2.plot([0, 1], [0, 1], "--", color="gray", label="Perfect Calibration")
    ax2.bar(bin_centers, bin_accs_cal, width=1.0 / n_bins, alpha=0.6, color="green", edgecolor="black", label="Outputs (Scaled)")
    ax2.set_title(f"Temperature Scaled (ECE = {ece_cal*100:.2f}%)")
    ax2.set_xlabel("Confidence")
    ax2.set_ylabel("Accuracy")
    ax2.set_xlim([0, 1])
    ax2.set_ylim([0, 1])
    ax2.legend()
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved reliability diagram to {output_path}")


def run_calibration(config_path: str = "ml/configs/train_config.yaml") -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    device = get_device()
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    best_model_path = Path(config["artifacts"]["best_model_path"])
    checkpoint = torch.load(best_model_path, map_location=device)
    classes = checkpoint["classes"]

    model = create_model(
        model_name=config["model"]["architecture"],
        num_classes=len(classes),
        pretrained=False
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    image_size = config["data"]["image_size"]

    # Validation set for tuning Temperature T
    val_dataset = PlantVillageDataset(config["data"]["manifest_path"], split="val", transform=get_eval_transforms(image_size))
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=2)

    # Test set for evaluating calibration before/after
    test_dataset = PlantVillageDataset(config["data"]["manifest_path"], split="test", transform=get_eval_transforms(image_size))
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=2)

    # Collect validation logits
    print("Collecting validation logits for temperature scaling...")
    val_logits_list, val_labels_list = [], []
    with torch.no_grad():
        for imgs, lbls in val_loader:
            imgs = imgs.to(device)
            out = model(imgs)
            val_logits_list.append(out.cpu())
            val_labels_list.append(lbls)

    val_logits = torch.cat(val_logits_list, dim=0)
    val_labels = torch.cat(val_labels_list, dim=0)

    # Fit temperature scaler
    scaler = TemperatureScaler()
    optimal_t = scaler.fit(val_logits, val_labels)
    print(f"Optimal Temperature parameter T = {optimal_t:.4f}")

    # Collect test logits
    print("Collecting test logits...")
    test_logits_list, test_labels_list = [], []
    with torch.no_grad():
        for imgs, lbls in test_loader:
            imgs = imgs.to(device)
            out = model(imgs)
            test_logits_list.append(out.cpu())
            test_labels_list.append(lbls)

    test_logits = torch.cat(test_logits_list, dim=0)
    test_labels = torch.cat(test_labels_list, dim=0).numpy()

    # Uncalibrated probabilities
    probs_uncal = torch.softmax(test_logits, dim=1).numpy()
    ece_uncal, bin_accs_uncal, bin_confs_uncal, counts_uncal = compute_ece(probs_uncal, test_labels)

    # Calibrated probabilities
    probs_cal = torch.softmax(scaler(test_logits), dim=1).detach().numpy()
    ece_cal, bin_accs_cal, bin_confs_cal, counts_cal = compute_ece(probs_cal, test_labels)

    # Save diagram
    plot_reliability_diagram(
        bin_accs_uncal, bin_confs_uncal, ece_uncal,
        bin_accs_cal, bin_confs_cal, ece_cal,
        reports_dir / "reliability_diagram.png"
    )

    calibration_report = {
        "optimal_temperature": round(optimal_t, 4),
        "uncalibrated_ece": round(ece_uncal, 4),
        "calibrated_ece": round(ece_cal, 4),
        "ece_reduction_pct": round((1.0 - (ece_cal / ece_uncal)) * 100, 2) if ece_uncal > 0 else 0.0,
        "n_bins": 15
    }

    with open(reports_dir / "calibration_report.json", "w") as f:
        json.dump(calibration_report, f, indent=2)

    # Save calibrated temperature parameter for backend inference
    with open(Path(config["artifacts"]["checkpoint_dir"]) / "temperature.json", "w") as f:
        json.dump({"temperature": optimal_t}, f, indent=2)

    print(f"Calibration Complete: ECE reduced from {ece_uncal*100:.2f}% to {ece_cal*100:.2f}% (T={optimal_t:.4f})")
    return calibration_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    run_calibration(args.config)

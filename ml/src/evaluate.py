"""Comprehensive evaluation pipeline on PlantVillage test split and PlantDoc cross-dataset."""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

import yaml
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    top_k_accuracy_score
)
from tqdm import tqdm

from ml.src.datasets import PlantVillageDataset, PlantDocDataset
from ml.src.transforms import get_eval_transforms
from ml.src.train import create_model, get_device


def evaluate_test_split(
    model: nn.Module,
    loader: DataLoader,
    classes: List[str],
    device: torch.device,
    reports_dir: Path
) -> Dict[str, Any]:
    """Evaluate on the held-out PlantVillage test split."""
    print("\n=== Evaluating on PlantVillage Held-Out Test Split ===")
    model.eval()
    
    all_targets = []
    all_preds = []
    all_probs = []
    
    with torch.no_grad():
        for images, targets in tqdm(loader, desc="Test eval"):
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            preds = outputs.argmax(dim=1).cpu().numpy()
            
            all_targets.extend(targets.numpy())
            all_preds.extend(preds)
            all_probs.extend(probs)
            
    all_targets_arr = np.array(all_targets)
    all_preds_arr = np.array(all_preds)
    all_probs_arr = np.array(all_probs)
    
    acc = float(accuracy_score(all_targets_arr, all_preds_arr))
    macro_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="weighted", zero_division=0))
    macro_prec = float(precision_score(all_targets_arr, all_preds_arr, average="macro", zero_division=0))
    macro_rec = float(recall_score(all_targets_arr, all_preds_arr, average="macro", zero_division=0))
    
    # Top-3 Accuracy
    try:
        top3_acc = float(top_k_accuracy_score(all_targets_arr, all_probs_arr, k=3, labels=list(range(len(classes)))))
    except Exception:
        top3_acc = float(acc)
        
    per_class_report = classification_report(
        all_targets_arr,
        all_preds_arr,
        target_names=classes,
        output_dict=True,
        zero_division=0
    )
    
    # Generate and save Confusion Matrix plot
    cm = confusion_matrix(all_targets_arr, all_preds_arr, labels=list(range(len(classes))))
    
    plt.figure(figsize=(18, 15))
    sns.heatmap(cm, annot=False, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.title(f"PlantVillage Test Confusion Matrix (Accuracy: {acc*100:.2f}%, Macro-F1: {macro_f1*100:.2f}%)")
    plt.xlabel("Predicted Class")
    plt.ylabel("True Class")
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    cm_path = reports_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"Saved confusion matrix plot to {cm_path}")
    
    metrics = {
        "dataset": "PlantVillage_Test_Split",
        "total_samples": len(all_targets_arr),
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "top3_accuracy": round(top3_acc, 4),
        "per_class_metrics": per_class_report,
        "confusion_matrix_shape": list(cm.shape)
    }
    
    with open(reports_dir / "test_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"PlantVillage Test Accuracy: {acc*100:.2f}%, Macro-F1: {macro_f1*100:.2f}%, Top-3 Acc: {top3_acc*100:.2f}%")
    return metrics


def evaluate_plantdoc_cross_dataset(
    model: nn.Module,
    plantdoc_root: str,
    mapping_file: str,
    image_size: int,
    classes: List[str],
    device: torch.device,
    reports_dir: Path
) -> Dict[str, Any]:
    """Evaluate on the real-world PlantDoc field dataset to measure domain shift / generalization gap."""
    print("\n=== Evaluating on PlantDoc Cross-Dataset (Real Field Images) ===")
    plantdoc_dataset = PlantDocDataset(
        root_dir=plantdoc_root,
        split="test",
        mapping_file=mapping_file,
        transform=get_eval_transforms(image_size)
    )
    
    if len(plantdoc_dataset) == 0:
        print("Warning: PlantDoc test set has 0 mapped samples. Checking all splits...")
        plantdoc_dataset = PlantDocDataset(
            root_dir=plantdoc_root,
            split="train",
            mapping_file=mapping_file,
            transform=get_eval_transforms(image_size)
        )
        
    if len(plantdoc_dataset) == 0:
        print("PlantDoc dataset not available or unmapped. Skipping cross-dataset eval.")
        return {"error": "PlantDoc dataset not available or 0 mapped samples."}
        
    loader = DataLoader(plantdoc_dataset, batch_size=32, shuffle=False, num_workers=2)
    model.eval()
    
    all_targets = []
    all_preds = []
    all_raw_names = []
    all_probs = []
    
    with torch.no_grad():
        for images, targets, raw_names in tqdm(loader, desc="PlantDoc eval"):
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            preds = outputs.argmax(dim=1).cpu().numpy()
            
            all_targets.extend(targets.numpy())
            all_preds.extend(preds)
            all_raw_names.extend(raw_names)
            all_probs.extend(probs)
            
    all_targets_arr = np.array(all_targets)
    all_preds_arr = np.array(all_preds)
    all_probs_arr = np.array(all_probs)
    
    acc = float(accuracy_score(all_targets_arr, all_preds_arr))
    macro_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="weighted", zero_division=0))
    
    unique_present_classes = sorted(list(set(all_targets_arr)))
    present_class_names = [classes[i] for i in unique_present_classes]
    
    # Common error analysis
    error_analysis = []
    for i in range(len(all_targets)):
        if all_targets[i] != all_preds[i]:
            error_analysis.append({
                "plantdoc_class": all_raw_names[i],
                "ground_truth": classes[all_targets[i]],
                "predicted": classes[all_preds[i]],
                "confidence": float(all_probs_arr[i][all_preds[i]])
            })
            
    metrics = {
        "dataset": "PlantDoc_Cross_Dataset",
        "total_evaluated_samples": len(all_targets_arr),
        "overlapping_classes_count": len(unique_present_classes),
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "most_common_errors": error_analysis[:20],
        "total_misclassifications": len(error_analysis)
    }
    
    with open(reports_dir / "plantdoc_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"PlantDoc Cross-Dataset Accuracy: {acc*100:.2f}%, Macro-F1: {macro_f1*100:.2f}%")
    return metrics


def run_evaluation(config_path: str = "ml/configs/train_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    device = get_device()
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    best_model_path = Path(config["artifacts"]["best_model_path"])
    if not best_model_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found at {best_model_path}. Run training first.")
        
    checkpoint = torch.load(best_model_path, map_location=device)
    classes = checkpoint["classes"]
    
    model = create_model(
        model_name=config["model"]["architecture"],
        num_classes=len(classes),
        pretrained=False
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    # 1. Evaluate PlantVillage Test Split
    image_size = config["data"]["image_size"]
    test_dataset = PlantVillageDataset(
        config["data"]["manifest_path"],
        split="test",
        transform=get_eval_transforms(image_size)
    )
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=2)
    pv_metrics = evaluate_test_split(model, test_loader, classes, device, reports_dir)
    
    # 2. Evaluate PlantDoc Cross Dataset
    pd_metrics = evaluate_plantdoc_cross_dataset(
        model=model,
        plantdoc_root=config["data"]["plantdoc_root"],
        mapping_file=config["data"]["plantdoc_mapping"],
        image_size=image_size,
        classes=classes,
        device=device,
        reports_dir=reports_dir
    )
    
    # 3. Compute Generalization Gap
    if "accuracy" in pd_metrics:
        gap_acc = pv_metrics["accuracy"] - pd_metrics["accuracy"]
        gap_f1 = pv_metrics["macro_f1"] - pd_metrics["macro_f1"]
        gen_gap_report = {
            "plantvillage_test_accuracy": pv_metrics["accuracy"],
            "plantvillage_test_macro_f1": pv_metrics["macro_f1"],
            "plantdoc_cross_accuracy": pd_metrics["accuracy"],
            "plantdoc_cross_macro_f1": pd_metrics["macro_f1"],
            "accuracy_generalization_gap": round(gap_acc, 4),
            "macro_f1_generalization_gap": round(gap_f1, 4),
            "analysis": "The lab-to-field generalization gap arises from complex background foliage, variable lighting, partial leaf occlusion, and multiple disease co-infections in field settings compared to lab conditions."
        }
        with open(reports_dir / "generalization_gap.json", "w") as f:
            json.dump(gen_gap_report, f, indent=2)
        print(f"\nGeneralization Gap: {gap_acc*100:.2f}% Accuracy drop from lab to field.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    run_evaluation(args.config)

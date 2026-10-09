"""Two-stage training pipeline for crop disease classification with MLflow tracking."""
import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple

import yaml
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import timm
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm

from ml.src.datasets import PlantVillageDataset
from ml.src.transforms import get_train_transforms, get_eval_transforms


def set_seed(seed: int = 42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """Select best available compute device (MPS on Apple Silicon, CUDA, or CPU)."""
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon MPS acceleration.")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using NVIDIA CUDA acceleration.")
    else:
        device = torch.device("cpu")
        print("Using CPU.")
    return device


def create_model(model_name: str, num_classes: int, pretrained: bool = True, drop_rate: float = 0.3) -> nn.Module:
    """Create timm vision backbone with custom classification head."""
    print(f"Creating model {model_name} (num_classes={num_classes}, pretrained={pretrained})...")
    model = timm.create_model(
        model_name,
        pretrained=pretrained,
        num_classes=num_classes,
        drop_rate=drop_rate
    )
    return model


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    scaler: Any = None
) -> Tuple[float, float, float]:
    model.train()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    
    for images, targets in tqdm(loader, desc="Train batch", leave=False):
        images = images.to(device)
        targets = targets.to(device)
        
        optimizer.zero_grad()
        
        if scaler and device.type == "cuda":
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, targets)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(targets.cpu().numpy())
        
    epoch_loss = total_loss / len(loader.dataset)
    acc = accuracy_score(all_targets, all_preds)
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    return epoch_loss, acc, macro_f1


@torch.no_grad()
def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, float, float]:
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    
    for images, targets in tqdm(loader, desc="Eval batch", leave=False):
        images = images.to(device)
        targets = targets.to(device)
        
        outputs = model(images)
        loss = criterion(outputs, targets)
        
        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(targets.cpu().numpy())
        
    val_loss = total_loss / len(loader.dataset)
    acc = accuracy_score(all_targets, all_preds)
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    return val_loss, acc, macro_f1


def run_training(config_path: str = "ml/configs/train_config.yaml") -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    set_seed(config.get("seed", 42))
    device = get_device()
    
    # Try initializing MLflow
    mlflow_active = False
    try:
        import mlflow
        mlflow.set_experiment(config.get("experiment_name", "crop_disease_classification"))
        mlflow.start_run(run_name=f"{config['model']['architecture']}_{int(time.time())}")
        mlflow.log_params({
            "model_arch": config["model"]["architecture"],
            "batch_size": config["training"]["batch_size"],
            "image_size": config["data"]["image_size"],
            "optimizer": config["training"]["optimizer"],
            "stage1_epochs": config["training"]["stage1"]["epochs"],
            "stage2_epochs": config["training"]["stage2"]["epochs"],
            "seed": config.get("seed", 42)
        })
        mlflow_active = True
        print("MLflow tracking initialized.")
    except Exception as e:
        print(f"MLflow note: {e}. Proceeding with local metric logging.")

    # Datasets and Loaders
    image_size = config["data"]["image_size"]
    manifest_path = config["data"]["manifest_path"]
    
    train_dataset = PlantVillageDataset(manifest_path, split="train", transform=get_train_transforms(image_size))
    val_dataset = PlantVillageDataset(manifest_path, split="val", transform=get_eval_transforms(image_size))
    
    num_classes = len(train_dataset.classes)
    print(f"Loaded {len(train_dataset)} training and {len(val_dataset)} validation samples across {num_classes} classes.")
    
    batch_size = config["training"]["batch_size"]
    num_workers = min(4, os.cpu_count() or 1)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=(device.type != "cpu")
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=(device.type != "cpu")
    )
    
    # Class weights & Loss criterion
    if config["training"].get("use_class_weights", True):
        class_weights = train_dataset.get_class_weights().to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=config["training"]["stage1"].get("label_smoothing", 0.1))
    else:
        criterion = nn.CrossEntropyLoss(label_smoothing=config["training"]["stage1"].get("label_smoothing", 0.1))

    # Create model
    model = create_model(
        model_name=config["model"]["architecture"],
        num_classes=num_classes,
        pretrained=config["model"]["pretrained"],
        drop_rate=config["model"]["drop_rate"]
    ).to(device)
    
    history = {
        "train_loss": [],
        "train_acc": [],
        "train_f1": [],
        "val_loss": [],
        "val_acc": [],
        "val_f1": [],
        "learning_rates": []
    }
    
    best_val_f1 = 0.0
    best_val_loss = float("inf")
    checkpoint_dir = Path(config["artifacts"]["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    best_model_path = Path(config["artifacts"]["best_model_path"])
    
    # ================= STAGE 1: Frozen Backbone =================
    stage1_cfg = config["training"]["stage1"]
    print(f"\n>>> Starting {stage1_cfg['description']} ({stage1_cfg['epochs']} epochs, LR={stage1_cfg['lr']})")
    
    # Freeze backbone parameters
    for name, param in model.named_parameters():
        if "classifier" not in name and "head" not in name and "fc" not in name:
            param.requires_grad = False
            
    optimizer_s1 = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=stage1_cfg["lr"],
        weight_decay=stage1_cfg["weight_decay"]
    )
    
    for epoch in range(1, stage1_cfg["epochs"] + 1):
        t0 = time.time()
        tr_loss, tr_acc, tr_f1 = train_one_epoch(model, train_loader, criterion, optimizer_s1, device)
        vl_loss, vl_acc, vl_f1 = evaluate_model(model, val_loader, criterion, device)
        duration = time.time() - t0
        
        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["train_f1"].append(tr_f1)
        history["val_loss"].append(vl_loss)
        history["val_acc"].append(vl_acc)
        history["val_f1"].append(vl_f1)
        history["learning_rates"].append(stage1_cfg["lr"])
        
        print(f"Stage 1 [Epoch {epoch}/{stage1_cfg['epochs']}] ({duration:.1f}s) - "
              f"Train Loss: {tr_loss:.4f} Acc: {tr_acc:.4f} F1: {tr_f1:.4f} | "
              f"Val Loss: {vl_loss:.4f} Acc: {vl_acc:.4f} F1: {vl_f1:.4f}")
              
        if mlflow_active:
            try:
                import mlflow
                mlflow.log_metrics({
                    "stage1_train_loss": tr_loss, "stage1_train_acc": tr_acc, "stage1_train_f1": tr_f1,
                    "stage1_val_loss": vl_loss, "stage1_val_acc": vl_acc, "stage1_val_f1": vl_f1
                }, step=epoch)
            except Exception:
                pass
                
        if vl_f1 > best_val_f1:
            best_val_f1 = vl_f1
            torch.save({
                "model_state_dict": model.state_dict(),
                "classes": train_dataset.classes,
                "val_acc": vl_acc,
                "val_f1": vl_f1,
                "config": config,
                "epoch": epoch,
                "stage": 1
            }, best_model_path)
            
    # ================= STAGE 2: Unfreeze Full Backbone =================
    stage2_cfg = config["training"]["stage2"]
    print(f"\n>>> Starting {stage2_cfg['description']} ({stage2_cfg['epochs']} epochs, LR={stage2_cfg['lr']})")
    
    for param in model.parameters():
        param.requires_grad = True
        
    optimizer_s2 = torch.optim.AdamW(
        model.parameters(),
        lr=stage2_cfg["lr"],
        weight_decay=stage2_cfg["weight_decay"]
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer_s2,
        T_max=stage2_cfg["epochs"],
        eta_min=stage2_cfg.get("min_lr", 1e-6)
    )
    
    patience = config["training"].get("early_stopping_patience", 5)
    epochs_no_improve = 0
    
    for epoch in range(1, stage2_cfg["epochs"] + 1):
        t0 = time.time()
        curr_lr = optimizer_s2.param_groups[0]["lr"]
        tr_loss, tr_acc, tr_f1 = train_one_epoch(model, train_loader, criterion, optimizer_s2, device)
        vl_loss, vl_acc, vl_f1 = evaluate_model(model, val_loader, criterion, device)
        scheduler.step()
        duration = time.time() - t0
        
        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["train_f1"].append(tr_f1)
        history["val_loss"].append(vl_loss)
        history["val_acc"].append(vl_acc)
        history["val_f1"].append(vl_f1)
        history["learning_rates"].append(curr_lr)
        
        print(f"Stage 2 [Epoch {epoch}/{stage2_cfg['epochs']}] (LR: {curr_lr:.2e}, {duration:.1f}s) - "
              f"Train Loss: {tr_loss:.4f} Acc: {tr_acc:.4f} F1: {tr_f1:.4f} | "
              f"Val Loss: {vl_loss:.4f} Acc: {vl_acc:.4f} F1: {vl_f1:.4f}")
              
        if mlflow_active:
            try:
                import mlflow
                mlflow.log_metrics({
                    "train_loss": tr_loss, "train_acc": tr_acc, "train_f1": tr_f1,
                    "val_loss": vl_loss, "val_acc": vl_acc, "val_f1": vl_f1,
                    "lr": curr_lr
                }, step=stage1_cfg["epochs"] + epoch)
            except Exception:
                pass
                
        if vl_f1 > best_val_f1:
            best_val_f1 = vl_f1
            epochs_no_improve = 0
            print(f"  --> Saved new best model checkpoint (Val Macro-F1: {best_val_f1:.4f})")
            torch.save({
                "model_state_dict": model.state_dict(),
                "classes": train_dataset.classes,
                "val_acc": vl_acc,
                "val_f1": vl_f1,
                "config": config,
                "epoch": stage1_cfg["epochs"] + epoch,
                "stage": 2
            }, best_model_path)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered after {patience} epochs without improvement.")
                break
                
    # Save labels and model version
    labels_path = Path(config["artifacts"]["labels_path"])
    with open(labels_path, "w") as f:
        json.dump(train_dataset.classes, f, indent=2)
    print(f"Saved {len(train_dataset.classes)} class labels to {labels_path}")
    
    version_str = f"v1.0.0_{config['model']['architecture']}_{int(time.time())}"
    with open(Path(config["artifacts"]["model_version_path"]), "w") as f:
        f.write(version_str)
        
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "training_curves.json", "w") as f:
        json.dump(history, f, indent=2)
    print(f"Saved training curves to {reports_dir / 'training_curves.json'}")
    
    if mlflow_active:
        try:
            import mlflow
            mlflow.log_artifact(str(labels_path))
            mlflow.log_artifact(str(reports_dir / "training_curves.json"))
            mlflow.end_run()
        except Exception:
            pass
            
    return {
        "best_val_f1": best_val_f1,
        "best_model_path": str(best_model_path),
        "labels_path": str(labels_path),
        "model_version": version_str
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    run_training(args.config)

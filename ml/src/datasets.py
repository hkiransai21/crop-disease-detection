"""PyTorch Dataset implementations for PlantVillage (manifest-driven) and PlantDoc."""
import os
from pathlib import Path
from typing import Callable, Optional, Tuple, List, Dict
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset
import numpy as np


class PlantVillageDataset(Dataset):
    """Manifest-driven PlantVillage Dataset with verified leakage-free splits."""
    
    def __init__(
        self,
        manifest_path: str,
        split: str = "train",
        transform: Optional[Callable] = None,
        data_root: Optional[str] = None
    ):
        self.manifest_path = Path(manifest_path)
        self.split = split
        self.transform = transform
        self.data_root = Path(data_root) if data_root else Path.cwd()
        
        df = pd.read_csv(self.manifest_path)
        self.data = df[df["split"] == split].reset_index(drop=True)
        
        if len(self.data) == 0:
            raise ValueError(f"No records found for split '{split}' in {manifest_path}")
            
        self.classes = sorted(df["class_name"].unique().tolist())
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        self.idx_to_class = {i: c for i, c in enumerate(self.classes)}
        
    def __len__(self) -> int:
        return len(self.data)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        row = self.data.iloc[idx]
        img_path = Path(row["full_path"])
        
        # Fallback if path is relative
        if not img_path.exists():
            img_path = self.data_root / row["relative_path"]
            
        try:
            with Image.open(img_path) as img:
                img_rgb = img.convert("RGB")
        except Exception as e:
            raise RuntimeError(f"Failed to load image at {img_path}: {e}")
            
        label = int(row["class_id"])
        
        if self.transform:
            img_tensor = self.transform(img_rgb)
        else:
            img_tensor = img_rgb
            
        return img_tensor, label

    def get_class_weights(self) -> torch.Tensor:
        """Calculate inverse class frequency weights for balanced Cross-Entropy Loss."""
        class_counts = self.data["class_id"].value_counts().sort_index()
        total_samples = len(self.data)
        num_classes = len(self.classes)
        
        weights = np.zeros(num_classes, dtype=np.float32)
        for cls_id in range(num_classes):
            count = class_counts.get(cls_id, 1)
            weights[cls_id] = total_samples / (num_classes * count)
            
        # Normalize weights
        weights = weights / np.mean(weights)
        return torch.tensor(weights, dtype=torch.float32)


class PlantDocDataset(Dataset):
    """PlantDoc real-world field dataset loader with label mapping to PlantVillage."""
    
    def __init__(
        self,
        root_dir: str,
        split: str = "test",
        mapping_file: Optional[str] = "ml/configs/plantdoc_mapping.json",
        transform: Optional[Callable] = None
    ):
        self.root_dir = Path(root_dir) / split
        self.split = split
        self.transform = transform
        self.samples: List[Tuple[Path, int, str]] = []
        
        # Load mapping if provided
        self.mapping: Dict[str, Optional[int]] = {}
        if mapping_file and Path(mapping_file).exists():
            import json
            with open(mapping_file, "r") as f:
                data = json.load(f)
                self.mapping = data.get("plantdoc_to_class_id", {})
                self.class_names = data.get("target_classes", [])
                
        valid_exts = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
        
        if self.root_dir.exists():
            for cls_dir in sorted(self.root_dir.iterdir()):
                if cls_dir.is_dir():
                    raw_cls_name = cls_dir.name
                    mapped_target_id = self.mapping.get(raw_cls_name)
                    
                    for img_file in cls_dir.iterdir():
                        if img_file.is_file() and img_file.suffix in valid_exts:
                            if mapped_target_id is not None:
                                self.samples.append((img_file, mapped_target_id, raw_cls_name))
                                
    def __len__(self) -> int:
        return len(self.samples)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        img_path, target_id, raw_name = self.samples[idx]
        with Image.open(img_path) as img:
            img_rgb = img.convert("RGB")
            
        if self.transform:
            img_tensor = self.transform(img_rgb)
        else:
            img_tensor = img_rgb
            
        return img_tensor, target_id, raw_name

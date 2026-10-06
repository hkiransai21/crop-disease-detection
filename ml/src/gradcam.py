"""Grad-CAM explainability implementation for visual attribution on plant disease lesions."""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

import yaml
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ml.src.datasets import PlantVillageDataset
from ml.src.transforms import get_eval_transforms
from ml.src.train import create_model, get_device


class GradCAM:
    """Computes Gradient-weighted Class Activation Mapping (Grad-CAM) for CNN backbones."""
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        self.hook_handles = []
        self._register_hooks()
        
    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()
            
        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()
            
        self.hook_handles.append(self.target_layer.register_forward_hook(forward_hook))
        self.hook_handles.append(self.target_layer.register_full_backward_hook(backward_hook))
        
    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: Optional[int] = None) -> np.ndarray:
        self.model.eval()
        self.model.zero_grad()
        
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
            
        score = output[0, class_idx]
        score.backward(retain_graph=True)
        
        # Global average pool the gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        
        # Weight activations by pooled gradients
        activations = self.activations.clone()
        for i in range(pooled_gradients.size(0)):
            activations[0, i, :, :] *= pooled_gradients[i]
            
        heatmap = torch.mean(activations, dim=1).squeeze().cpu().numpy()
        # ReLU on top of the heatmap
        heatmap = np.maximum(heatmap, 0)
        # Normalize
        if np.max(heatmap) > 0:
            heatmap /= np.max(heatmap)
            
        return heatmap

    def remove_hooks(self):
        for handle in self.hook_handles:
            handle.remove()


def overlay_heatmap_on_image(img_pil: Image.Image, heatmap: np.ndarray, alpha: float = 0.5) -> Image.Image:
    """Superimpose Grad-CAM heatmap over the original PIL image."""
    img_np = np.array(img_pil)
    w, h = img_pil.size
    
    # Resize heatmap to match image dimensions
    heatmap_resized = cv2.resize(heatmap, (w, h))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    superimposed = np.uint8(alpha * heatmap_colored + (1.0 - alpha) * img_np)
    return Image.fromarray(superimposed)


def run_gradcam_analysis(config_path: str = "ml/configs/train_config.yaml", num_samples: int = 6):
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
    
    # Determine the target layer for Grad-CAM
    # For EfficientNet, the last convolutional block is `conv_head` or `blocks[-1]`
    target_layer = None
    if hasattr(model, "conv_head") and model.conv_head is not None:
        target_layer = model.conv_head
    elif hasattr(model, "blocks"):
        target_layer = model.blocks[-1]
    elif hasattr(model, "features"):
        target_layer = model.features[-1]
    else:
        # Fallback to last conv module in named modules
        for name, module in model.named_modules():
            if isinstance(module, nn.Conv2d):
                target_layer = module
                
    if target_layer is None:
        print("Could not find suitable conv layer for Grad-CAM.")
        return
        
    print(f"Using target layer {target_layer} for Grad-CAM.")
    cam = GradCAM(model, target_layer)
    
    image_size = config["data"]["image_size"]
    test_dataset = PlantVillageDataset(
        config["data"]["manifest_path"],
        split="test",
        transform=None # We need raw PIL image
    )
    
    eval_transform = get_eval_transforms(image_size)
    
    # Select sample cases: correct and incorrect
    correct_samples = []
    incorrect_samples = []
    
    for i in range(len(test_dataset)):
        img_pil, true_label = test_dataset[i]
        input_tensor = eval_transform(img_pil).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_tensor)
            pred_label = output.argmax(dim=1).item()
            prob = torch.softmax(output, dim=1)[0, pred_label].item()
            
        if pred_label == true_label and len(correct_samples) < (num_samples // 2):
            correct_samples.append((img_pil, true_label, pred_label, prob, input_tensor))
        elif pred_label != true_label and len(incorrect_samples) < (num_samples // 2):
            incorrect_samples.append((img_pil, true_label, pred_label, prob, input_tensor))
            
        if len(correct_samples) >= (num_samples // 2) and (len(incorrect_samples) >= (num_samples // 2) or i > 200):
            break
            
    all_selected = correct_samples + incorrect_samples
    fig, axes = plt.subplots(len(all_selected), 3, figsize=(15, 4 * len(all_selected)))
    if len(all_selected) == 1:
        axes = np.expand_dims(axes, 0)
        
    for idx, (img_pil, true_lbl, pred_lbl, prob, inp_tensor) in enumerate(all_selected):
        heatmap = cam.generate_heatmap(inp_tensor, pred_lbl)
        overlay = overlay_heatmap_on_image(img_pil.resize((image_size, image_size)), heatmap)
        
        # Col 1: Original
        axes[idx, 0].imshow(img_pil.resize((image_size, image_size)))
        axes[idx, 0].set_title(f"True: {classes[true_lbl]}", fontsize=9)
        axes[idx, 0].axis("off")
        
        # Col 2: Heatmap
        axes[idx, 1].imshow(heatmap, cmap="jet")
        axes[idx, 1].set_title(f"Grad-CAM Heatmap", fontsize=9)
        axes[idx, 1].axis("off")
        
        # Col 3: Overlay
        status = "CORRECT" if true_lbl == pred_lbl else "MISCLASSIFIED"
        color = "green" if true_lbl == pred_lbl else "red"
        axes[idx, 2].imshow(overlay)
        axes[idx, 2].set_title(f"Pred: {classes[pred_lbl]} ({prob*100:.1f}%) [{status}]", color=color, fontsize=9)
        axes[idx, 2].axis("off")
        
    plt.tight_layout()
    output_path = reports_dir / "gradcam_samples.png"
    plt.savefig(output_path, dpi=200)
    plt.close()
    cam.remove_hooks()
    print(f"Saved Grad-CAM visualizations to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="ml/configs/train_config.yaml")
    args = parser.parse_args()
    run_gradcam_analysis(args.config)

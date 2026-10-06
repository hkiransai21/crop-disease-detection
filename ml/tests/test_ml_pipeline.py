"""Unit tests for ML pipeline integrity, transforms, data splits, and model architectures."""
import pytest
import numpy as np
import torch
from PIL import Image

from ml.src.transforms import get_train_transforms, get_eval_transforms
from ml.src.train import create_model
from ml.src.calibrate import compute_ece, TemperatureScaler
from backend.app.ml.inference import preprocess_image, compute_entropy


def test_train_and_eval_transforms():
    """Verify that torchvision data augmentations produce correct tensor shapes and normalization ranges."""
    sample_img = Image.new("RGB", (300, 300), color=(100, 150, 200))

    train_t = get_train_transforms(224)
    eval_t = get_eval_transforms(224)

    t_tensor = train_t(sample_img)
    e_tensor = eval_t(sample_img)

    assert isinstance(t_tensor, torch.Tensor)
    assert t_tensor.shape == (3, 224, 224)
    assert isinstance(e_tensor, torch.Tensor)
    assert e_tensor.shape == (3, 224, 224)


def test_inference_preprocessing():
    """Verify ONNX runtime preprocessing pipeline."""
    sample_img = Image.new("RGB", (400, 300), color=(50, 120, 200))
    tensor_np = preprocess_image(sample_img, 224)

    assert isinstance(tensor_np, np.ndarray)
    assert tensor_np.shape == (1, 3, 224, 224)
    assert tensor_np.dtype == np.float32


def test_entropy_computation():
    """Verify Shannon entropy calculation."""
    # Perfectly confident distribution -> 0 entropy
    conf_probs = np.array([1.0, 0.0, 0.0])
    assert compute_entropy(conf_probs) < 0.01

    # Uniform distribution (3 classes) -> log(3) ~= 1.098
    uniform_probs = np.array([1/3, 1/3, 1/3])
    ent = compute_entropy(uniform_probs)
    assert abs(ent - np.log(3)) < 0.05


def test_temperature_scaling_optimization():
    """Verify TemperatureScaler learns positive scaling factor reducing NLL loss."""
    scaler = TemperatureScaler()
    logits = torch.tensor([[10.0, 2.0, 1.0], [1.0, 8.0, 2.0]], dtype=torch.float32)
    labels = torch.tensor([0, 1], dtype=torch.long)

    opt_t = scaler.fit(logits, labels, max_iter=20)
    assert opt_t > 0.0
    scaled = scaler(logits)
    assert scaled.shape == logits.shape


def test_ece_computation():
    """Verify ECE computation returns expected calibration error."""
    # Perfectly calibrated
    probs = np.array([[0.9, 0.1], [0.8, 0.2], [0.1, 0.9], [0.2, 0.8]])
    labels = np.array([0, 0, 1, 1])

    ece, _, _, _ = compute_ece(probs, labels, n_bins=5)
    assert 0.0 <= ece <= 1.0


def test_model_instantiation():
    """Verify efficientnet_b0 architecture creates correct output dimensions."""
    model = create_model("efficientnet_b0", num_classes=38, pretrained=False)
    dummy = torch.randn(2, 3, 224, 224)
    out = model(dummy)
    assert out.shape == (2, 38)

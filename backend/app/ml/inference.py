"""ONNX Runtime high-performance CPU inference service for plant disease diagnosis."""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image
import onnxruntime as ort
from backend.app.core.config import settings

_ORT_SESSION: Optional[ort.InferenceSession] = None
_LABELS: Optional[List[str]] = None
_MODEL_VERSION: str = "v1.0.0"
_TEMPERATURE: float = 1.0

# 38 Default PlantVillage classes fallback if labels.json is not yet created
DEFAULT_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy"
]


def load_inference_artifacts():
    """Load ONNX model session, class labels, and temperature scaler at application startup."""
    global _ORT_SESSION, _LABELS, _MODEL_VERSION, _TEMPERATURE

    # 1. Load labels
    labels_path = Path(settings.LABELS_PATH)
    if labels_path.exists():
        with open(labels_path, "r") as f:
            _LABELS = json.load(f)
    else:
        _LABELS = DEFAULT_CLASSES

    # 2. Load model version
    v_path = Path(settings.MODEL_VERSION_PATH)
    if v_path.exists():
        with open(v_path, "r") as f:
            _MODEL_VERSION = f.read().strip()
    else:
        _MODEL_VERSION = "v1.0.0_efficientnet_b0"

    # 3. Load Temperature scaling parameter
    t_path = Path(settings.TEMPERATURE_PATH)
    if t_path.exists():
        try:
            with open(t_path, "r") as f:
                data = json.load(f)
                _TEMPERATURE = float(data.get("temperature", 1.0))
        except Exception:
            _TEMPERATURE = 1.0

    # 4. Load ONNX model session (check FP32 first, fallback to INT8)
    model_path = Path(settings.MODEL_PATH)
    if not model_path.exists():
        model_path = Path(settings.QUANTIZED_MODEL_PATH)

    if model_path.exists():
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = min(4, os.cpu_count() or 1)
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        _ORT_SESSION = ort.InferenceSession(str(model_path), sess_options, providers=["CPUExecutionProvider"])
        print(f"Loaded ONNX model for CPU inference from {model_path} ({_MODEL_VERSION}, T={_TEMPERATURE:.3f})")
    else:
        print(f"Warning: ONNX model not found at {model_path}. Will use dummy fallback prediction until model is trained.")


def preprocess_image(image: Image.Image, target_size: int = 224) -> np.ndarray:
    """Preprocess PIL image: Resize to 256, CenterCrop to 224, Normalize with ImageNet mean/std."""
    # Resize shorter side to 256
    w, h = image.size
    scale = 256.0 / min(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = image.resize((new_w, new_h), Image.BILINEAR)

    # Center crop 224x224
    left = (new_w - target_size) // 2
    top = (new_h - target_size) // 2
    img_cropped = img_resized.crop((left, top, left + target_size, top + target_size))

    # Convert to float32 numpy array [0, 1]
    img_np = np.array(img_cropped).astype(np.float32) / 255.0

    # Normalize with ImageNet mean and std
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_norm = (img_np - mean) / std

    # Transpose HWC -> CHW and add batch dimension -> NCHW
    img_tensor = np.transpose(img_norm, (2, 0, 1))[np.newaxis, ...]
    return img_tensor


def compute_entropy(probs: np.ndarray, eps: float = 1e-9) -> float:
    """Compute Shannon entropy in nats."""
    p = np.clip(probs, eps, 1.0)
    return float(-np.sum(p * np.log(p)))


def predict_disease(image: Image.Image, top_k: int = 3) -> Dict[str, Any]:
    """Execute model inference and return top-k predictions with uncertainty detection."""
    global _ORT_SESSION, _LABELS, _MODEL_VERSION, _TEMPERATURE

    if _LABELS is None:
        _LABELS = DEFAULT_CLASSES

    # Fast path if ONNX model is loaded
    if _ORT_SESSION is not None:
        input_tensor = preprocess_image(image)
        input_name = _ORT_SESSION.get_inputs()[0].name
        logits = _ORT_SESSION.run(None, {input_name: input_tensor})[0][0]

        # Apply learned temperature scaling
        scaled_logits = logits / _TEMPERATURE

        # Compute calibrated Softmax
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        probs = exp_logits / np.sum(exp_logits)
    else:
        # Fallback pseudo-prediction if model is still being trained
        probs = np.random.dirichlet(np.ones(len(_LABELS)) * 0.1)

    top_indices = np.argsort(probs)[::-1][:top_k]
    entropy = compute_entropy(probs)
    top_confidence = float(probs[top_indices[0]])
    top_class_id = _LABELS[top_indices[0]]

    # Uncertainty / Out-of-distribution rejection heuristic
    is_uncertain = (
        top_confidence < settings.CONFIDENCE_THRESHOLD or
        entropy > settings.UNCERTAIN_ENTROPY_THRESHOLD
    )

    uncertainty_reason = None
    if is_uncertain:
        if top_confidence < settings.CONFIDENCE_THRESHOLD:
            uncertainty_reason = f"Low diagnostic confidence ({top_confidence*100:.1f}% < {settings.CONFIDENCE_THRESHOLD*100:.0f}% threshold). Leaf may be blurry, occluded, or non-plant."
        else:
            uncertainty_reason = f"High prediction ambiguity / entropy ({entropy:.2f}). Visual features match multiple distinct leaf conditions."

    # Parse crop and disease name
    def parse_name(cid: str) -> Tuple[str, str, bool]:
        if "___" in cid:
            crop_part, disease_part = cid.split("___", 1)
        else:
            crop_part, disease_part = "Plant", cid
            
        crop_clean = crop_part.replace("_", " ").replace("(maize)", "").replace("(including sour)", "").strip()
        disease_clean = disease_part.replace("_", " ").strip()
        is_healthy = "healthy" in disease_part.lower()
        return crop_clean, disease_clean, is_healthy

    top_predictions = []
    for idx in top_indices:
        cid = _LABELS[idx]
        c_crop, c_disease, c_healthy = parse_name(cid)
        top_predictions.append({
            "class_id": cid,
            "crop": c_crop,
            "disease_name": c_disease,
            "confidence": float(probs[idx]),
            "confidence_percentage": round(float(probs[idx] * 100), 2),
            "is_healthy": c_healthy
        })

    top_crop, top_disease, is_healthy = parse_name(top_class_id)

    # Simple wording for farmers
    if top_confidence >= 0.85:
        conf_display = "Very High Confidence"
    elif top_confidence >= 0.65:
        conf_display = "High Confidence"
    elif top_confidence >= 0.45:
        conf_display = "Moderate Confidence"
    else:
        conf_display = "Low / Uncertain"

    return {
        "predicted_label": top_class_id,
        "crop": top_crop,
        "disease_name": top_disease,
        "is_healthy": is_healthy,
        "confidence": top_confidence,
        "confidence_display": conf_display,
        "is_uncertain": is_uncertain,
        "uncertainty_reason": uncertainty_reason,
        "entropy": round(entropy, 4),
        "top_k": top_predictions,
        "model_version": _MODEL_VERSION
    }

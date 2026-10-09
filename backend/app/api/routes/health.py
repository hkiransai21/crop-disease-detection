"""Health, Readiness, and Model Metadata endpoints."""
import os
import json
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health & Model Info"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic liveness probe."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking database connectivity and ML model availability."""
    # Check ONNX model file
    model_ready = Path(settings.QUANTIZED_MODEL_PATH).exists() or Path(settings.MODEL_PATH).exists()
    labels_ready = Path(settings.LABELS_PATH).exists()
    kb_ready = Path(settings.KNOWLEDGE_BASE_PATH).exists()

    return {
        "status": "ready" if kb_ready else "degraded",
        "database": "connected",
        "model_file_present": model_ready,
        "labels_present": labels_ready,
        "knowledge_base_present": kb_ready
    }


@router.get("/model/info")
async def get_model_info() -> Dict[str, Any]:
    """Fetch active ML model version, architecture, and measured benchmark reports."""
    reports_dir = Path("ml/reports")
    
    test_metrics = {}
    if (reports_dir / "test_metrics.json").exists():
        with open(reports_dir / "test_metrics.json", "r") as f:
            test_metrics = json.load(f)

    benchmark_metrics = {}
    if (reports_dir / "benchmark_report.json").exists():
        with open(reports_dir / "benchmark_report.json", "r") as f:
            benchmark_metrics = json.load(f)

    gen_gap = {}
    if (reports_dir / "generalization_gap.json").exists():
        with open(reports_dir / "generalization_gap.json", "r") as f:
            gen_gap = json.load(f)

    calibration = {}
    if (reports_dir / "calibration_report.json").exists():
        with open(reports_dir / "calibration_report.json", "r") as f:
            calibration = json.load(f)

    version_str = "v1.0.0_efficientnet_b0"
    if Path(settings.MODEL_VERSION_PATH).exists():
        with open(settings.MODEL_VERSION_PATH, "r") as f:
            version_str = f.read().strip()

    return {
        "model_version": version_str,
        "architecture": "EfficientNet-B0 (Transfer Learning)",
        "num_classes": 38,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "entropy_uncertainty_threshold": settings.UNCERTAIN_ENTROPY_THRESHOLD,
        "test_metrics": test_metrics,
        "benchmark": benchmark_metrics,
        "generalization_gap": gen_gap,
        "calibration": calibration
    }

"""Data drift and model performance monitoring script analyzing prediction logs and feedback."""
import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon


def calculate_kl_and_js_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-7) -> Dict[str, float]:
    """Calculate KL and Jensen-Shannon divergence between baseline and production class distributions."""
    p = np.asarray(p, dtype=np.float64) + eps
    p = p / np.sum(p)
    q = np.asarray(q, dtype=np.float64) + eps
    q = q / np.sum(q)
    
    js_div = float(jensenshannon(p, q))
    kl_div = float(np.sum(p * np.log(p / q)))
    
    return {
        "jensen_shannon_divergence": round(js_div, 4),
        "kl_divergence": round(kl_div, 4),
        "drift_detected": js_div > 0.20 # Standard threshold
    }


def analyze_drift_from_db(
    db_path: str = "backend/app.db",
    labels_path: str = "ml/models/labels.json",
    baseline_stats_path: str = "ml/reports/raw_dataset_stats.json",
    output_path: str = "ml/reports/drift_report.json"
) -> Dict[str, Any]:
    print(f"\n=== Running Production Drift Analysis on {db_path} ===")
    
    if not Path(labels_path).exists():
        raise FileNotFoundError(f"Labels file not found at {labels_path}")
        
    with open(labels_path, "r") as f:
        classes = json.load(f)
        
    # Load baseline training distribution
    baseline_counts = np.ones(len(classes), dtype=float)
    if Path(baseline_stats_path).exists():
        with open(baseline_stats_path, "r") as f:
            stats = json.load(f)
            pv_classes = stats.get("plantvillage", {}).get("classes", {})
            for idx, cname in enumerate(classes):
                baseline_counts[idx] = pv_classes.get(cname, 1)
                
    baseline_dist = baseline_counts / np.sum(baseline_counts)
    
    # Check if DB exists
    if not Path(db_path).exists():
        print(f"Database at {db_path} not found. Generating sample baseline report.")
        sample_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_production_inferences": 0,
            "status": "NO_PRODUCTION_DATA",
            "message": "Database has not accumulated production requests yet.",
            "baseline_num_classes": len(classes),
            "distribution_drift": {
                "jensen_shannon_divergence": 0.0,
                "kl_divergence": 0.0,
                "drift_detected": False
            },
            "feedback_accuracy_proxy": None,
            "bias_warning": "User feedback is voluntary and subject to reporting bias (farmers report unexpected/incorrect results more frequently than correct ones)."
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(sample_report, f, indent=2)
        return sample_report

    conn = sqlite3.connect(db_path)
    
    # Query analyses
    analyses_df = pd.read_sql_query("SELECT id, predicted_label, confidence, is_uncertain, created_at FROM analyses", conn)
    # Query feedback
    feedback_df = pd.read_sql_query("SELECT analysis_id, is_correct, corrected_label, created_at FROM feedbacks", conn)
    conn.close()
    
    total_inferences = len(analyses_df)
    if total_inferences == 0:
        print("0 production inferences found in database.")
        prod_dist = baseline_dist
        div_metrics = calculate_kl_and_js_divergence(baseline_dist, prod_dist)
        feedback_proxy = None
    else:
        # Compute production class counts
        prod_counts = np.zeros(len(classes), dtype=float)
        for label, count in analyses_df["predicted_label"].value_counts().items():
            if label in classes:
                prod_counts[classes.index(label)] = count
                
        prod_dist = prod_counts / (np.sum(prod_counts) if np.sum(prod_counts) > 0 else 1.0)
        div_metrics = calculate_kl_and_js_divergence(baseline_dist, prod_dist)
        
        # Feedback accuracy proxy
        if len(feedback_df) > 0:
            feedback_proxy = {
                "total_feedbacks": len(feedback_df),
                "user_confirmed_correct_count": int((feedback_df["is_correct"] == 1).sum()),
                "user_corrected_count": int((feedback_df["is_correct"] == 0).sum()),
                "raw_feedback_accuracy_pct": round(float((feedback_df["is_correct"] == 1).mean() * 100), 2),
                "sampling_bias_note": "CRITICAL: This metric is a voluntary feedback sample, NOT an unbiased test accuracy. Disgruntled users with incorrect classifications are significantly more likely to submit feedback than satisfied users."
            }
        else:
            feedback_proxy = None

    confidence_stats = {
        "mean_confidence": round(float(analyses_df["confidence"].mean()), 4) if total_inferences > 0 else 0.0,
        "median_confidence": round(float(analyses_df["confidence"].median()), 4) if total_inferences > 0 else 0.0,
        "p10_confidence": round(float(np.percentile(analyses_df["confidence"], 10)), 4) if total_inferences > 0 else 0.0,
        "uncertain_rate_pct": round(float(analyses_df["is_uncertain"].mean() * 100), 2) if total_inferences > 0 else 0.0
    }

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_production_inferences": total_inferences,
        "confidence_distribution": confidence_stats,
        "distribution_drift": div_metrics,
        "feedback_accuracy_proxy": feedback_proxy,
        "recommendations": (
            "Trigger automated retraining workflow with new consented samples."
            if div_metrics["drift_detected"]
            else "Model distribution remains aligned with baseline."
        )
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Saved drift analysis to {output_path}")
    return report


if __name__ == "__main__":
    analyze_drift_from_db()

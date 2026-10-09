"""Automated retraining pipeline incorporating consented user-feedback samples into dataset versions."""
import os
import sys
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

import pandas as pd


def extract_consented_feedback_samples(
    db_path: str = "backend/app.db",
    output_dir: str = "ml/data/feedback_dataset",
    manifest_path: str = "ml/data/processed/split_manifest.csv"
) -> Dict[str, Any]:
    """Query database for user-confirmed or corrected samples with consent, saving them to new dataset split."""
    print("=== Extracting Consented Retraining Samples from Production DB ===")
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    if not Path(db_path).exists():
        print(f"No DB found at {db_path}. Nothing to extract.")
        return {"extracted_count": 0, "status": "NO_DATABASE"}
        
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        a.id AS analysis_id,
        a.image_path,
        a.predicted_label,
        f.is_correct,
        f.corrected_label,
        f.consent_for_retraining,
        f.created_at
    FROM feedbacks f
    JOIN analyses a ON f.analysis_id = a.id
    WHERE f.consent_for_retraining = 1
    """
    try:
        feedback_df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Query error (tables might not exist yet): {e}")
        conn.close()
        return {"extracted_count": 0, "status": "ERROR", "error": str(e)}
        
    conn.close()
    
    print(f"Found {len(feedback_df)} consented feedback records.")
    if len(feedback_df) == 0:
        return {"extracted_count": 0, "status": "NO_CONSENTED_RECORDS"}
        
    new_samples = []
    for _, row in feedback_df.iterrows():
        src_img = Path(row["image_path"])
        if not src_img.exists():
            continue
            
        final_label = row["corrected_label"] if (not row["is_correct"] and row["corrected_label"]) else row["predicted_label"]
        target_dir = out_path / final_label
        target_dir.mkdir(parents=True, exist_ok=True)
        
        dst_img = target_dir / f"feedback_{row['analysis_id']}_{src_img.name}"
        shutil.copy2(src_img, dst_img)
        
        new_samples.append({
            "full_path": str(dst_img.resolve()),
            "relative_path": str(dst_img),
            "class_name": final_label,
            "split": "train", # New field samples added to training
            "source": "consented_user_feedback",
            "extracted_at": datetime.now(timezone.utc).isoformat()
        })
        
    print(f"Successfully copied {len(new_samples)} verified images to {out_path}.")
    return {
        "extracted_count": len(new_samples),
        "target_directory": str(out_path),
        "samples": new_samples
    }


if __name__ == "__main__":
    extract_consented_feedback_samples()

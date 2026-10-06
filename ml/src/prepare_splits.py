"""Data preparation, perceptual hash deduplication, and leakage-free stratified splitting."""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
import numpy as np
import pandas as pd
from PIL import Image
import imagehash
from tqdm import tqdm
from sklearn.model_selection import train_test_split

RAW_PV_DIR = Path("ml/data/raw/plantvillage")
PROCESSED_DIR = Path("ml/data/processed")
REPORTS_DIR = Path("ml/reports")

SEED = 42
HASH_THRESHOLD = 4  # Hamming distance threshold for near-duplicates (phash)


def compute_hashes_for_dataset(data_dir: Path) -> List[Dict[str, Any]]:
    """Scan all images and compute perceptual and difference hashes."""
    # Resolve directory if nested (e.g. raw/color or color)
    search_dirs = [data_dir, data_dir / "color", data_dir / "raw" / "color", data_dir / "PlantVillage"]
    actual_dir = data_dir
    for candidate in search_dirs:
        if candidate.exists():
            class_candidates = [d for d in candidate.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if len(class_candidates) >= 30:
                actual_dir = candidate
                break

    print(f"Computing perceptual hashes across PlantVillage ({actual_dir})...")
    records = []
    valid_exts = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
    
    classes = sorted([d.name for d in actual_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    class_to_idx = {c: i for i, c in enumerate(classes)}
    
    for cls_name in tqdm(classes, desc="Processing classes"):
        cls_dir = actual_dir / cls_name
        cls_idx = class_to_idx[cls_name]
        
        img_paths = sorted([p for p in cls_dir.iterdir() if p.is_file() and p.suffix in valid_exts])
        
        for img_path in img_paths:
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB to ensure consistency
                    img_rgb = img.convert("RGB")
                    phash_val = imagehash.phash(img_rgb, hash_size=8)
                    dhash_val = imagehash.dhash(img_rgb, hash_size=8)
                    
                    records.append({
                        "file_name": img_path.name,
                        "relative_path": str(img_path.relative_to(data_dir.parent.parent)),
                        "full_path": str(img_path.resolve()),
                        "class_name": cls_name,
                        "class_id": cls_idx,
                        "phash": str(phash_val),
                        "dhash": str(dhash_val),
                        "hash_obj": phash_val
                    })
            except Exception as e:
                print(f"Warning: Corrupt or unreadable image {img_path}: {e}")
                
    print(f"Computed hashes for {len(records)} images across {len(classes)} classes.")
    return records


def cluster_near_duplicates(records: List[Dict[str, Any]], hash_threshold: int = HASH_THRESHOLD) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Cluster near-duplicates within each class to prevent data leakage."""
    print(f"Clustering near-duplicates (Hamming distance <= {hash_threshold})...")
    
    # Group records by class
    by_class: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        by_class.setdefault(r["class_name"], []).append(r)
        
    global_cluster_counter = 0
    total_exact_duplicates = 0
    total_near_duplicate_pairs = 0
    clustered_records = []
    
    class_dup_stats = {}
    
    for cls_name, class_records in by_class.items():
        n = len(class_records)
        # Disjoint set / Union-Find for clustering
        parent = list(range(n))
        
        def find(i):
            path = []
            while parent[i] != i:
                path.append(i)
                i = parent[i]
            for p in path:
                parent[p] = i
            return i
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        exact_dups = 0
        near_dups = 0
        
        # Fast comparison using hex hash lookup first, then distance comparison
        hashes = [r["hash_obj"] for r in class_records]
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = hashes[i] - hashes[j]
                if dist == 0:
                    exact_dups += 1
                    union(i, j)
                elif dist <= hash_threshold:
                    near_dups += 1
                    union(i, j)
                    
        total_exact_duplicates += exact_dups
        total_near_duplicate_pairs += near_dups
        
        # Map roots to cluster IDs
        root_to_cluster = {}
        for i in range(n):
            root = find(i)
            if root not in root_to_cluster:
                root_to_cluster[root] = global_cluster_counter
                global_cluster_counter += 1
                
            rec = {k: v for k, v in class_records[i].items() if k != "hash_obj"}
            rec["cluster_id"] = root_to_cluster[root]
            clustered_records.append(rec)
            
        num_clusters = len(root_to_cluster)
        class_dup_stats[cls_name] = {
            "total_images": n,
            "unique_clusters": num_clusters,
            "exact_duplicate_pairs": exact_dups,
            "near_duplicate_pairs": near_dups,
            "redundancy_pct": round((1.0 - (num_clusters / n)) * 100, 2) if n > 0 else 0.0
        }
        
    dup_summary = {
        "total_images_processed": len(records),
        "total_clusters": global_cluster_counter,
        "total_exact_duplicate_pairs": total_exact_duplicates,
        "total_near_duplicate_pairs": total_near_duplicate_pairs,
        "overall_redundancy_pct": round((1.0 - (global_cluster_counter / len(records))) * 100, 2) if records else 0.0,
        "class_level_stats": class_dup_stats
    }
    
    print(f"Formed {global_cluster_counter} unique clusters from {len(records)} images.")
    print(f"Overall redundancy: {dup_summary['overall_redundancy_pct']}%")
    return clustered_records, dup_summary


def create_stratified_group_splits(records: List[Dict[str, Any]], train_ratio: float = 0.70, val_ratio: float = 0.15, test_ratio: float = 0.15) -> pd.DataFrame:
    """Split clusters (not raw images) to ensure 0% leakage between train/val/test."""
    print("Creating stratified group splits (70% train, 15% val, 15% test)...")
    df = pd.DataFrame(records)
    
    # We group by cluster_id and class_name
    cluster_df = df.groupby(["cluster_id", "class_name", "class_id"]).size().reset_index(name="cluster_size")
    
    train_clusters: List[int] = []
    val_clusters: List[int] = []
    test_clusters: List[int] = []
    
    np.random.seed(SEED)
    
    # Stratify by class at the cluster level
    for cls_name, group in cluster_df.groupby("class_name"):
        c_ids = np.array(group["cluster_id"].values, copy=True)
        np.random.shuffle(c_ids)
        
        n_total = len(c_ids)
        n_train = int(np.round(n_total * train_ratio))
        n_val = int(np.round(n_total * val_ratio))
        
        # Ensure at least 1 cluster in val and test if group has >= 3 clusters
        if n_total >= 3:
            n_train = max(1, min(n_train, n_total - 2))
            n_val = max(1, min(n_val, n_total - n_train - 1))
        
        train_c = c_ids[:n_train]
        val_c = c_ids[n_train:n_train + n_val]
        test_c = c_ids[n_train + n_val:]
        
        train_clusters.extend(train_c)
        val_clusters.extend(val_c)
        test_clusters.extend(test_c)
        
    train_set = set(train_clusters)
    val_set = set(val_clusters)
    test_set = set(test_clusters)
    
    def assign_split(cid):
        if cid in train_set:
            return "train"
        elif cid in val_set:
            return "val"
        elif cid in test_set:
            return "test"
        return "train"
        
    df["split"] = df["cluster_id"].apply(assign_split)
    
    # Verification: confirm zero cluster overlap
    assert len(train_set.intersection(val_set)) == 0, "Leakage detected between train and val!"
    assert len(train_set.intersection(test_set)) == 0, "Leakage detected between train and test!"
    assert len(val_set.intersection(test_set)) == 0, "Leakage detected between val and test!"
    
    print("\nSplit Image Counts:")
    print(df["split"].value_counts())
    print("\nSplit Percentage:")
    print(df["split"].value_counts(normalize=True) * 100)
    
    return df


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not RAW_PV_DIR.exists():
        print(f"Error: {RAW_PV_DIR} does not exist. Run download_data.py first.")
        sys.exit(1)
        
    records = compute_hashes_for_dataset(RAW_PV_DIR)
    clustered_records, dup_summary = cluster_near_duplicates(records)
    
    split_df = create_stratified_group_splits(clustered_records)
    
    # Save manifest CSV
    manifest_path = PROCESSED_DIR / "split_manifest.csv"
    split_df.to_csv(manifest_path, index=False)
    print(f"\nSaved split manifest to {manifest_path}")
    
    # Save deduplication and split report
    split_stats = {
        "train_count": int((split_df["split"] == "train").sum()),
        "val_count": int((split_df["split"] == "val").sum()),
        "test_count": int((split_df["split"] == "test").sum()),
        "total_count": len(split_df),
        "split_percentages": {
            "train": round(float((split_df["split"] == "train").mean() * 100), 2),
            "val": round(float((split_df["split"] == "val").mean() * 100), 2),
            "test": round(float((split_df["split"] == "test").mean() * 100), 2)
        },
        "per_class_split": split_df.groupby(["class_name", "split"]).size().unstack(fill_value=0).to_dict(orient="index")
    }
    
    full_report = {
        "deduplication": dup_summary,
        "splits": split_stats
    }
    
    with open(REPORTS_DIR / "deduplication_and_splits_report.json", "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"Saved deduplication report to {REPORTS_DIR / 'deduplication_and_splits_report.json'}")


if __name__ == "__main__":
    main()

"""Dataset downloader and integrity verifier for PlantVillage and PlantDoc datasets."""
import os
import sys
import shutil
import zipfile
import tarfile
import urllib.request
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

RAW_DATA_DIR = Path("ml/data/raw")
PLANTVILLAGE_DIR = RAW_DATA_DIR / "plantvillage"
PLANTDOC_DIR = RAW_DATA_DIR / "plantdoc"
REPORTS_DIR = Path("ml/reports")

# Authoritative 38 classes of PlantVillage
EXPECTED_PLANTVILLAGE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]


def download_plantdoc():
    """Download PlantDoc dataset from official GitHub repository."""
    print("=== Downloading PlantDoc dataset ===")
    plantdoc_repo_dir = RAW_DATA_DIR / "plantdoc_git"
    PLANTDOC_DIR.mkdir(parents=True, exist_ok=True)
    
    if (PLANTDOC_DIR / "test").exists() and any((PLANTDOC_DIR / "test").iterdir()):
        print("PlantDoc dataset already present.")
        return

    if not plantdoc_repo_dir.exists():
        print("Cloning PlantDoc repository from https://github.com/pratikkayal/PlantDoc-Dataset...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/pratikkayal/PlantDoc-Dataset.git", str(plantdoc_repo_dir)],
            check=True
        )
    
    # Copy train and test folders to plantdoc dir
    for split in ["train", "test"]:
        src_split = plantdoc_repo_dir / split
        dst_split = PLANTDOC_DIR / split
        if src_split.exists() and not dst_split.exists():
            shutil.copytree(src_split, dst_split)
            print(f"Copied PlantDoc {split} images to {dst_split}")
            
    print("PlantDoc download complete.")


def download_plantvillage():
    """Download PlantVillage dataset (38 classes) via reliable repository mirror."""
    print("=== Downloading PlantVillage dataset (38 classes) ===")
    PLANTVILLAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if already populated
    existing_classes = [d.name for d in PLANTVILLAGE_DIR.iterdir() if d.is_dir()]
    if len(existing_classes) >= 38:
        print(f"PlantVillage already present with {len(existing_classes)} classes.")
        return

    # Method 1: Clone from spMohanty/PlantVillage-Dataset or mirror
    pv_git_dir = RAW_DATA_DIR / "plantvillage_git"
    if not pv_git_dir.exists():
        print("Cloning PlantVillage repository from https://github.com/spMohanty/PlantVillage-Dataset...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "https://github.com/spMohanty/PlantVillage-Dataset.git", str(pv_git_dir)],
                check=True
            )
        except Exception as e:
            print(f"Git clone error: {e}. Trying alternative archive download...")

    # Look for raw/color or color directory
    possible_color_dirs = [
        pv_git_dir / "raw" / "color",
        pv_git_dir / "color",
        pv_git_dir / "raw" / "segmented"
    ]
    
    found_src = None
    for p in possible_color_dirs:
        if p.exists() and len(list(p.iterdir())) >= 30:
            found_src = p
            break
            
    if found_src:
        print(f"Copying classes from {found_src} to {PLANTVILLAGE_DIR}...")
        for class_dir in found_src.iterdir():
            if class_dir.is_dir():
                target_dir = PLANTVILLAGE_DIR / class_dir.name
                if not target_dir.exists():
                    shutil.copytree(class_dir, target_dir)
        print("PlantVillage images successfully copied.")
    else:
        # Fallback to direct zip archive download if needed
        print("Attempting direct mirror zip download...")
        zip_url = "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/d5652a28-c1d8-4b76-97f3-72fb80f94efc/file_downloaded"
        zip_path = RAW_DATA_DIR / "plantvillage.zip"
        if not zip_path.exists():
            print(f"Downloading from {zip_url}...")
            urllib.request.urlretrieve(zip_url, zip_path)
        print("Extracting zip archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DATA_DIR / "pv_extracted")


def verify_and_report() -> Dict[str, Any]:
    """Verify downloaded dataset integrity and save summary statistics."""
    print("=== Verifying Dataset Counts ===")
    stats: Dict[str, Any] = {
        "plantvillage": {
            "total_images": 0,
            "num_classes": 0,
            "classes": {}
        },
        "plantdoc": {
            "train_images": 0,
            "test_images": 0,
            "total_images": 0,
            "classes": {}
        }
    }
    
    valid_exts = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

    # PlantVillage stats
    if PLANTVILLAGE_DIR.exists():
        pv_classes = sorted([d.name for d in PLANTVILLAGE_DIR.iterdir() if d.is_dir()])
        stats["plantvillage"]["num_classes"] = len(pv_classes)
        total_pv = 0
        for cls_name in pv_classes:
            cls_path = PLANTVILLAGE_DIR / cls_name
            img_count = len([f for f in cls_path.iterdir() if f.is_file() and f.suffix in valid_exts])
            stats["plantvillage"]["classes"][cls_name] = img_count
            total_pv += img_count
        stats["plantvillage"]["total_images"] = total_pv
        print(f"PlantVillage verified: {len(pv_classes)} classes, {total_pv} total images.")

    # PlantDoc stats
    if PLANTDOC_DIR.exists():
        for split in ["train", "test"]:
            split_dir = PLANTDOC_DIR / split
            if split_dir.exists():
                for cls_dir in split_dir.iterdir():
                    if cls_dir.is_dir():
                        cname = cls_dir.name
                        if cname not in stats["plantdoc"]["classes"]:
                            stats["plantdoc"]["classes"][cname] = {"train": 0, "test": 0, "total": 0}
                        count = len([f for f in cls_dir.iterdir() if f.is_file() and f.suffix in valid_exts])
                        stats["plantdoc"]["classes"][cname][split] = count
                        stats["plantdoc"]["classes"][cname]["total"] += count
                        if split == "train":
                            stats["plantdoc"]["train_images"] += count
                        else:
                            stats["plantdoc"]["test_images"] += count
        stats["plantdoc"]["total_images"] = stats["plantdoc"]["train_images"] + stats["plantdoc"]["test_images"]
        print(f"PlantDoc verified: {len(stats['plantdoc']['classes'])} classes, {stats['plantdoc']['total_images']} total images ({stats['plantdoc']['train_images']} train, {stats['plantdoc']['test_images']} test).")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "raw_dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved stats to {REPORTS_DIR / 'raw_dataset_stats.json'}")
    return stats


if __name__ == "__main__":
    download_plantvillage()
    download_plantdoc()
    verify_and_report()

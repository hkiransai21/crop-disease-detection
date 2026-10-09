"""Helper script to extract and structure PlantVillage dataset after download."""
import os
import sys
import zipfile
import shutil
from pathlib import Path

RAW_DIR = Path("ml/data/raw")
ZIP_PATH = RAW_DIR / "data.zip"
TARGET_PV_DIR = RAW_DIR / "plantvillage"


def extract_and_organize():
    if not ZIP_PATH.exists():
        # Check in .cache
        cache_files = list(RAW_DIR.glob("**/*.zip"))
        if cache_files:
            zip_file = cache_files[0]
        else:
            print(f"No zip file found in {RAW_DIR}")
            return False
    else:
        zip_file = ZIP_PATH

    print(f"Extracting {zip_file}...")
    temp_extract = RAW_DIR / "temp_extracted"
    temp_extract.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)
        
    print("Finding class directories...")
    TARGET_PV_DIR.mkdir(parents=True, exist_ok=True)
    
    # Search for directory with classes
    possible_roots = [
        temp_extract,
        temp_extract / "color",
        temp_extract / "raw" / "color",
        temp_extract / "PlantVillage",
        temp_extract / "data" / "color"
    ]
    
    found_root = None
    for r in possible_roots:
        if r.exists():
            dirs = [d for d in r.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if len(dirs) >= 30:
                found_root = r
                break
                
    if not found_root:
        # Recursive search for any directory with >= 30 subdirs
        for p in temp_extract.rglob("*"):
            if p.is_dir():
                subdirs = [d for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")]
                if len(subdirs) >= 30:
                    found_root = p
                    break
                    
    if found_root:
        print(f"Found class root at {found_root}. Copying to {TARGET_PV_DIR}...")
        for cls_dir in found_root.iterdir():
            if cls_dir.is_dir() and not cls_dir.name.startswith("."):
                dst = TARGET_PV_DIR / cls_dir.name
                if not dst.exists():
                    shutil.copytree(cls_dir, dst)
        print(f"Successfully populated {TARGET_PV_DIR} with {len(list(TARGET_PV_DIR.iterdir()))} classes.")
        
        # Clean up temp
        shutil.rmtree(temp_extract, ignore_errors=True)
        return True
    else:
        print(f"Could not find class directories in {temp_extract}")
        return False


if __name__ == "__main__":
    extract_and_organize()

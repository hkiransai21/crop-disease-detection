"""Image storage service handling privacy (EXIF stripping), validation, and disk persistence."""
import os
import uuid
import io
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
from backend.app.core.config import settings

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_and_process_image(
    file_bytes: bytes,
    original_filename: str
) -> Tuple[str, Image.Image, int, int]:
    """
    Validate image type/size/dimensions, strip all EXIF metadata for farmer privacy,
    and save clean image to disk with a unique UUID filename.
    """
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    ext = Path(original_filename).suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        # Fallback check if it's a valid image
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify() # Verify file integrity
        # Re-open after verify()
        image = Image.open(io.BytesIO(file_bytes))
        # Auto-orient based on EXIF orientation before stripping EXIF
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Corrupted or unreadable image file: {str(e)}"
        )

    width, height = image.size
    if width < 32 or height < 32:
        raise HTTPException(
            status_code=400,
            detail=f"Image dimensions ({width}x{height}) are too small for diagnostic analysis. Minimum is 32x32."
        )

    # Strip EXIF metadata completely by creating a clean copy without info dict
    clean_image = Image.new(image.mode, image.size)
    clean_image.paste(image)

    # Generate unique filename
    unique_id = str(uuid.uuid4())
    save_filename = f"{unique_id}.jpg"
    save_path = UPLOAD_DIR / save_filename

    # Save as high-quality clean JPEG
    clean_image.save(save_path, format="JPEG", quality=92, optimize=True)

    return str(save_path), clean_image, width, height

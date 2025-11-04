import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException
from shared.config import Config


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp"
}


def validate_image_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    filename = file.filename or ""
    extension = filename.lower().split(".")[-1] if "." in filename else ""
    if extension not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid extension. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        )


async def save_uploaded_file(file: UploadFile) -> Tuple[str, str, int]:
    validate_image_file(file)
    
    file_id = str(uuid.uuid4())
    original_filename = file.filename or "unknown"
    extension = original_filename.split(".")[-1] if "." in original_filename else "jpg"
    stored_filename = f"{file_id}.{extension}"
    
    upload_dir = Path(Config.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / stored_filename
    
    try:
        content = await file.read()
        file_size = len(content)
        
        max_size = Config.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max: {Config.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"✅ Saved: {stored_filename} ({file_size} bytes)")
        return file_id, str(file_path), file_size
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")


def get_thumbnail_path(image_id: str, size: str, extension: str = "jpg") -> str:
    thumbnail_dir = Path(Config.THUMBNAIL_DIR) / size
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    return str(thumbnail_dir / f"{image_id}.{extension}")


def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)

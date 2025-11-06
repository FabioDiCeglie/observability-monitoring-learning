import os
import time
from pathlib import Path
from PIL import Image
from shared.config import Config, THUMBNAIL_SIZES


def generate_thumbnails(image_path: str, image_id: str) -> list:
    """
    Generate thumbnails for an image.
    Returns list of tuples: (size_name, width, height, file_path, file_size_bytes, processing_time_ms)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    results = []
    original_image = Image.open(image_path)
    extension = Path(image_path).suffix or ".jpg"
    
    for size_name, (width, height) in THUMBNAIL_SIZES.items():
        start_time = time.time()
        
        thumbnail = original_image.copy()
        thumbnail.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        thumbnail_dir = Path(Config.THUMBNAIL_DIR) / size_name
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = thumbnail_dir / f"{image_id}{extension}"
        
        thumbnail.save(thumbnail_path, quality=85, optimize=True)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        file_size = os.path.getsize(thumbnail_path)
        
        results.append((
            size_name,
            thumbnail.width,
            thumbnail.height,
            str(thumbnail_path),
            file_size,
            processing_time_ms
        ))
        
        print(f"✅ Generated {size_name}: {thumbnail.width}x{thumbnail.height} ({processing_time_ms}ms)")
    
    original_image.close()
    return results


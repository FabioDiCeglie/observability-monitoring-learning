"""
Image API routes for upload and download.
"""
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.models.schemas import ImageUploadResponse
from api.storage.file_handler import save_uploaded_file, file_exists
from shared.database import get_db, Image, Thumbnail, ImageStatus
from shared.pubsub_client import get_pubsub_client
from shared.metrics import init_metrics, increment_counter, record_histogram

init_metrics()

router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image for processing.
    
    - Validates the image file
    - Saves to storage
    - Creates database record
    - Publishes message to Pub/Sub for processing
    """
    try:
        file_id, file_path, file_size = await save_uploaded_file(file)
        
        increment_counter("image.upload.count", tags=["status:success"])
        record_histogram("image.upload.size_bytes", file_size)
        
        image = Image(
            id=file_id,
            original_filename=file.filename or "unknown",
            original_path=file_path,
            original_size_bytes=file_size,
            status=ImageStatus.UPLOADED,
            uploaded_at=datetime.utcnow()
        )
        db.add(image)
        db.commit()
        
        pubsub_client = get_pubsub_client()
        message = {
            "image_id": file_id,
            "file_path": file_path,
            "original_filename": file.filename,
        }
        message_id = pubsub_client.publish_message(message)
        
        print(f"📤 Published processing task for image {file_id} (message: {message_id})")
        
        return ImageUploadResponse(
            id=file_id,
            filename=file.filename or "unknown",
            status=ImageStatus.UPLOADED.value,
            size_bytes=file_size,
            uploaded_at=image.uploaded_at,
            message="Image uploaded successfully and queued for processing"
        )
        
    except HTTPException:
        increment_counter("image.upload.count", tags=["status:error"])
        raise
    except Exception as e:
        db.rollback()
        increment_counter("image.upload.count", tags=["status:error"])
        print(f"❌ Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{image_id}/{size}")
def download_thumbnail(
    image_id: str,
    size: str,
    db: Session = Depends(get_db)
):
    """
    Download a generated thumbnail.
    
    Size options: small, medium, large
    """
    if size not in ["small", "medium", "large"]:
        increment_counter("thumbnail.download.count", tags=["status:error", "reason:invalid_size"])
        raise HTTPException(
            status_code=400, 
            detail="Invalid size. Must be: small, medium, or large"
        )
    
    thumbnail = db.query(Thumbnail).join(Image).filter(
        Image.id == image_id,
        Thumbnail.size_name == size
    ).first()
    
    if not thumbnail:
        increment_counter("thumbnail.download.count", tags=["status:error", "reason:not_found", f"size:{size}"])
        raise HTTPException(
            status_code=404,
            detail=f"Thumbnail '{size}' not found for image. It may still be processing."
        )
    
    if not file_exists(thumbnail.file_path):
        increment_counter("thumbnail.download.count", tags=["status:error", "reason:file_missing", f"size:{size}"])
        raise HTTPException(
            status_code=404, 
            detail="Thumbnail file not found on disk"
        )
    
    increment_counter("thumbnail.download.count", tags=["status:success", f"size:{size}"])
    
    return FileResponse(
        thumbnail.file_path,
        media_type="image/jpeg",
        filename=f"{image_id}_{size}.jpg"
    )

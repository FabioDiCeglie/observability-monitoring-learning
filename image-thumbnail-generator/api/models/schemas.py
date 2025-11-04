"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Response model after uploading an image."""
    id: str
    filename: str
    status: str
    size_bytes: int
    uploaded_at: datetime
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    database: str
    pubsub: str


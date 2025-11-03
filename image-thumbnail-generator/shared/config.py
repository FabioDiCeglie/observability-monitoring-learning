"""
Shared configuration for the image thumbnail generator system.
"""
import os
from typing import Dict, Tuple


class Config:
    """Application configuration loaded from environment variables."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://imageprocessor:imageprocessor123@localhost:5432/image_processing")
    
    # Pub/Sub
    PUBSUB_PROJECT_ID = os.getenv("PUBSUB_PROJECT_ID", "image-thumbnail-project")
    PUBSUB_EMULATOR_HOST = os.getenv("PUBSUB_EMULATOR_HOST", "localhost:8085")
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "image-processing-tasks")
    
    # Storage paths
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/storage/uploads")
    THUMBNAIL_DIR = os.getenv("THUMBNAIL_DIR", "/app/storage/thumbnails")
    
    # Image processing
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp").split(",")
    
    # Thumbnail sizes configuration
    @staticmethod
    def get_thumbnail_sizes() -> Dict[str, Tuple[int, int]]:
        """
        Parse thumbnail sizes from environment variable.
        Format: small:150x150,medium:400x400,large:800x800
        """
        sizes_str = os.getenv("THUMBNAIL_SIZES", "small:150x150,medium:400x400,large:800x800")
        sizes = {}
        
        for size_config in sizes_str.split(","):
            name, dimensions = size_config.split(":")
            width, height = dimensions.split("x")
            sizes[name.strip()] = (int(width), int(height))
        
        return sizes
    
    # Worker
    WORKER_COUNT = int(os.getenv("WORKER_COUNT", "2"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))
    WORKER_SLEEP_SECONDS = float(os.getenv("WORKER_SLEEP_SECONDS", "0.1"))
    
    # Datadog
    DD_AGENT_HOST = os.getenv("DD_AGENT_HOST", "datadog-agent")
    DD_TRACE_AGENT_PORT = int(os.getenv("DD_TRACE_AGENT_PORT", "8126"))
    DD_ENV = os.getenv("DD_ENV", "development")
    DD_SERVICE_API = os.getenv("DD_SERVICE_API", "image-api")
    DD_SERVICE_WORKER = os.getenv("DD_SERVICE_WORKER", "image-worker")
    DD_TRACE_ENABLED = os.getenv("DD_TRACE_ENABLED", "false").lower() == "true"
    DD_API_KEY = os.getenv("DD_API_KEY", "")
    
    # API
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")


# Thumbnail size presets
THUMBNAIL_SIZES = Config.get_thumbnail_sizes()

print(f"📸 Configured thumbnail sizes: {THUMBNAIL_SIZES}")


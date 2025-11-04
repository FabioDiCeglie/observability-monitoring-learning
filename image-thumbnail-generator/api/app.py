"""
FastAPI application for Image Thumbnail Generator API service.
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import images
from api.models.schemas import HealthResponse
from shared.database import init_db
from shared.pubsub_client import get_pubsub_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application.
    Handles startup and shutdown tasks.
    """
    print("🚀 Starting Image Thumbnail Generator API...")
    
    init_db()
    print("✅ Database initialized")
    
    pubsub_client = get_pubsub_client()
    print("✅ Pub/Sub client initialized")
    
    yield
    
    print("👋 Shutting down API service...")


app = FastAPI(
    title="Image Thumbnail Generator API",
    description="Upload images and generate thumbnails with distributed processing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router)

@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """
    Health check endpoint.
    
    Verifies that the API service is running and can connect to dependencies.
    """
    db_status = "unknown"
    try:
        from shared.database import engine
        if engine:
            connection = engine.connect()
            connection.close()
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    pubsub_status = "unknown"
    try:
        pubsub_client = get_pubsub_client()
        if pubsub_client:
            pubsub_status = "healthy"
    except Exception as e:
        pubsub_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and pubsub_status == "healthy" else "degraded",
        service="image-api",
        timestamp=datetime.utcnow(),
        database=db_status,
        pubsub=pubsub_status
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

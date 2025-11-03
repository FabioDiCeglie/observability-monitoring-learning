"""
Database models and connection setup for image thumbnail generator.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, BigInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from shared.config import Config

Base = declarative_base()


class ImageStatus(enum.Enum):
    """Status of image processing."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Image(Base):
    """Main image record."""
    __tablename__ = "images"
    
    id = Column(String(36), primary_key=True)  # UUID
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(512), nullable=False)
    original_size_bytes = Column(BigInteger, nullable=False)
    status = Column(SQLEnum(ImageStatus), nullable=False, default=ImageStatus.UPLOADED)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(String(1024), nullable=True)
    
    # Relationship to thumbnails
    thumbnails = relationship("Thumbnail", back_populates="image", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename={self.original_filename}, status={self.status})>"


class Thumbnail(Base):
    """Generated thumbnail record."""
    __tablename__ = "thumbnails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(String(36), ForeignKey("images.id"), nullable=False)
    size_name = Column(String(50), nullable=False)  # small, medium, large
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    processing_time_ms = Column(Integer, nullable=False)  # Time to generate this thumbnail
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to parent image
    image = relationship("Image", back_populates="thumbnails")
    
    def __repr__(self):
        return f"<Thumbnail(id={self.id}, image_id={self.image_id}, size={self.size_name})>"


# Database engine and session factory
engine = None
SessionLocal = None


def init_db():
    """Initialize database connection and create tables."""
    global engine, SessionLocal
    
    engine = create_engine(
        Config.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def get_db():
    """Get database session (dependency for FastAPI)."""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


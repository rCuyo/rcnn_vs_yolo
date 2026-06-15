"""
Configuration settings for the RCNN vs YOLO application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "RCNN vs YOLO Detection"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    IMAGES_DIR: Path = UPLOAD_DIR / "images"
    VIDEOS_DIR: Path = UPLOAD_DIR / "videos"
    RESULTS_DIR: Path = UPLOAD_DIR / "results"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'app' / 'backend' / 'database' / 'detection.db'}"
    
    # Model settings
    DEVICE: str = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    
    # RCNN model
    RCNN_MODEL_NAME: str = "fasterrcnn_resnet50_fpn"
    RCNN_CONFIDENCE_THRESHOLD: float = 0.6  # umbral mayor para reducir falsos positivos

    # YOLO model
    YOLO_MODEL_PATH: str = "yolov8s.pt"  # variante "small": mejor precisión que nano
    YOLO_CONFIDENCE_THRESHOLD: float = 0.6  # umbral mayor para reducir falsos positivos
    
    # Detection settings
    MAX_IMAGE_SIZE: int = 1920
    MAX_VIDEO_DURATION: int = 600  # seconds
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    
    # Video processing
    VIDEO_FPS: int = 30
    VIDEO_FRAME_SKIP: int = 1  # Process every frame
    
    # API settings
    CORS_ORIGINS: list = ["*"]
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

"""
Database models for storing detection results and metrics
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DetectionResult(Base):
    """Model for storing detection results"""
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # File information
    filename = Column(String, index=True)
    file_type = Column(String)  # "image" or "video"
    file_path = Column(String)
    
    # Model information
    model_type = Column(String, index=True)  # "rcnn" or "yolo"
    model_name = Column(String)
    
    # Detection results
    detected_objects = Column(JSON)  # List of detected objects
    detections_count = Column(Integer)
    
    # Metrics
    inference_time = Column(Float)  # seconds
    fps = Column(Float, nullable=True)  # for videos
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    map_score = Column(Float, nullable=True)  # mAP
    
    # Resource usage
    cpu_usage = Column(Float, nullable=True)  # percentage
    memory_usage = Column(Float, nullable=True)  # MB
    gpu_usage = Column(Float, nullable=True)  # percentage
    
    # Output
    output_image_path = Column(String, nullable=True)
    output_video_path = Column(String, nullable=True)
    
    # Metadata
    is_compared = Column(Boolean, default=False)
    comparison_json = Column(JSON, nullable=True)

class ComparisonResult(Base):
    """Model for storing comparison between RCNN and YOLO"""
    __tablename__ = "comparison_results"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # File information
    filename = Column(String, index=True)
    file_type = Column(String)  # "image" or "video"
    
    # RCNN results
    rcnn_result_id = Column(Integer)
    rcnn_inference_time = Column(Float)
    rcnn_detections = Column(Integer)
    rcnn_fps = Column(Float, nullable=True)
    rcnn_precision = Column(Float, nullable=True)
    rcnn_recall = Column(Float, nullable=True)
    rcnn_map = Column(Float, nullable=True)
    rcnn_memory = Column(Float, nullable=True)
    
    # YOLO results
    yolo_result_id = Column(Integer)
    yolo_inference_time = Column(Float)
    yolo_detections = Column(Integer)
    yolo_fps = Column(Float, nullable=True)
    yolo_precision = Column(Float, nullable=True)
    yolo_recall = Column(Float, nullable=True)
    yolo_map = Column(Float, nullable=True)
    yolo_memory = Column(Float, nullable=True)
    
    # Comparison analysis
    faster_model = Column(String)  # "rcnn" or "yolo"
    speed_advantage = Column(Float)  # percentage
    accuracy_difference = Column(String)  # JSON with detailed differences
    winner = Column(String)  # "rcnn", "yolo", or "tie"

class SystemMetrics(Base):
    """Model for storing system metrics over time"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # CPU and memory metrics
    cpu_percent = Column(Float)
    memory_mb = Column(Float)
    memory_percent = Column(Float)
    
    # GPU metrics (if available)
    gpu_available = Column(Boolean)
    gpu_percent = Column(Float, nullable=True)
    gpu_memory_mb = Column(Float, nullable=True)
    
    # Active process
    active_model = Column(String, nullable=True)
    active_file = Column(String, nullable=True)

"""
Main FastAPI application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import time
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from config import settings
from database.db import init_db, get_db, engine
from database.models import Base
from detection.rcnn_detector import RCNNDetector
from detection.yolo_detector import YOLODetector
from metrics.calculator import MetricsCalculator
from utils.file_handler import FileHandler, ImageProcessor
from database.models import DetectionResult, ComparisonResult

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Object Detection Comparison Platform - RCNN vs YOLO"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
static_path = frontend_path / "static"
templates_path = frontend_path / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize detectors
rcnn_detector = None
yolo_detector = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and load models on startup"""
    global rcnn_detector, yolo_detector
    
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    print("Loading detection models...")
    try:
        rcnn_detector = RCNNDetector(
            device=settings.DEVICE,
            confidence_threshold=settings.RCNN_CONFIDENCE_THRESHOLD
        )
        print("✓ RCNN model loaded")
    except Exception as e:
        print(f"✗ Error loading RCNN model: {e}")
    
    try:
        yolo_detector = YOLODetector(
            model_name=settings.YOLO_MODEL_PATH,
            device=settings.DEVICE,
            confidence_threshold=settings.YOLO_CONFIDENCE_THRESHOLD
        )
        print("✓ YOLO model loaded")
    except Exception as e:
        print(f"✗ Error loading YOLO model: {e}")

# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """Serve the main HTML file"""
    index_path = templates_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"message": "RCNN vs YOLO Detection API", "version": settings.APP_VERSION}

@app.get("/{path_name:path}")
async def catch_all(path_name: str):
    """Catch-all route to serve index.html for SPA routing"""
    index_path = templates_path / "index.html"
    if index_path.exists() and not path_name.startswith("api/"):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rcnn_available": rcnn_detector is not None,
        "yolo_available": yolo_detector is not None
    }

# ==================== IMAGE DETECTION ENDPOINTS ====================

@app.post("/api/v1/detect/image/rcnn")
async def detect_image_rcnn(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Detect objects in image using RCNN
    
    Args:
        file: Image file to detect objects in
        
    Returns:
        Detection results with annotated image
    """
    if not rcnn_detector:
        raise HTTPException(status_code=503, detail="RCNN model not available")
    
    try:
        # Read file
        content = await file.read()
        
        # Save file
        file_path = FileHandler.save_upload_file(content, file.filename, "image")
        
        # Validate and resize if needed
        if not FileHandler.validate_image(file_path):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        FileHandler.resize_image_if_needed(file_path)
        
        # Run detection
        start_time = time.time()
        annotated_image, detections, inference_time = rcnn_detector.detect_image(file_path)
        
        # Save annotated image
        output_path = str(settings.RESULTS_DIR / f"rcnn_result_{int(time.time())}.jpg")
        ImageProcessor.save_detection_result(annotated_image, output_path)
        
        # Get system metrics
        system_metrics = MetricsCalculator.get_system_metrics()
        
        # Save results to database
        result = DetectionResult(
            filename=file.filename,
            file_type="image",
            file_path=file_path,
            model_type="rcnn",
            model_name=settings.RCNN_MODEL_NAME,
            detected_objects=[{**d} for d in detections],
            detections_count=len(detections),
            inference_time=inference_time,
            output_image_path=output_path,
            cpu_usage=system_metrics['cpu_percent'],
            memory_usage=system_metrics['memory_mb'],
            gpu_usage=system_metrics.get('gpu_percent')
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "result_id": result.id,
            "filename": file.filename,
            "model": "rcnn",
            "detections": detections,
            "detections_count": len(detections),
            "inference_time": inference_time,
            "output_image": f"/api/v1/results/image/{result.id}",
            "system_metrics": system_metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/api/v1/detect/image/yolo")
async def detect_image_yolo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Detect objects in image using YOLO
    
    Args:
        file: Image file to detect objects in
        
    Returns:
        Detection results with annotated image
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="YOLO model not available")
    
    try:
        # Read file
        content = await file.read()
        
        # Save file
        file_path = FileHandler.save_upload_file(content, file.filename, "image")
        
        # Validate and resize if needed
        if not FileHandler.validate_image(file_path):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        FileHandler.resize_image_if_needed(file_path)
        
        # Run detection
        annotated_image, detections, inference_time = yolo_detector.detect_image(file_path)
        
        # Save annotated image
        output_path = str(settings.RESULTS_DIR / f"yolo_result_{int(time.time())}.jpg")
        ImageProcessor.save_detection_result(annotated_image, output_path)
        
        # Get system metrics
        system_metrics = MetricsCalculator.get_system_metrics()
        
        # Save results to database
        result = DetectionResult(
            filename=file.filename,
            file_type="image",
            file_path=file_path,
            model_type="yolo",
            model_name="yolov8n",
            detected_objects=[{**d} for d in detections],
            detections_count=len(detections),
            inference_time=inference_time,
            output_image_path=output_path,
            cpu_usage=system_metrics['cpu_percent'],
            memory_usage=system_metrics['memory_mb'],
            gpu_usage=system_metrics.get('gpu_percent')
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "result_id": result.id,
            "filename": file.filename,
            "model": "yolo",
            "detections": detections,
            "detections_count": len(detections),
            "inference_time": inference_time,
            "output_image": f"/api/v1/results/image/{result.id}",
            "system_metrics": system_metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

# ==================== VIDEO DETECTION ENDPOINTS ====================

@app.post("/api/v1/detect/video/rcnn")
async def detect_video_rcnn(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Detect objects in video using RCNN
    
    Args:
        file: Video file to process
        
    Returns:
        Task information for video processing
    """
    if not rcnn_detector:
        raise HTTPException(status_code=503, detail="RCNN model not available")
    
    try:
        # Read file
        content = await file.read()
        
        # Save file
        file_path = FileHandler.save_upload_file(content, file.filename, "video")
        
        # Validate video
        if not FileHandler.validate_video(file_path):
            raise HTTPException(status_code=400, detail="Invalid video file")
        
        # Get video info
        video_info = FileHandler.get_video_info(file_path)
        
        # Run detection (this should be async in production)
        output_path, all_detections, total_time, fps = rcnn_detector.detect_video(file_path)
        
        # Calculate average metrics
        total_detections = sum(len(f['detections']) for f in all_detections)
        avg_detections_per_frame = total_detections / len(all_detections) if all_detections else 0
        
        # Save results to database
        result = DetectionResult(
            filename=file.filename,
            file_type="video",
            file_path=file_path,
            model_type="rcnn",
            model_name=settings.RCNN_MODEL_NAME,
            detections_count=int(total_detections),
            inference_time=total_time,
            fps=fps,
            output_video_path=output_path
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "result_id": result.id,
            "filename": file.filename,
            "model": "rcnn",
            "video_info": video_info,
            "output_video": f"/api/v1/results/video/{result.id}",
            "total_detections": int(total_detections),
            "avg_detections_per_frame": avg_detections_per_frame,
            "total_inference_time": total_time,
            "fps": fps,
            "frames_processed": len(all_detections)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

@app.post("/api/v1/detect/video/yolo")
async def detect_video_yolo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Detect objects in video using YOLO
    """
    if not yolo_detector:
        raise HTTPException(status_code=503, detail="YOLO model not available")
    
    try:
        # Read file
        content = await file.read()
        
        # Save file
        file_path = FileHandler.save_upload_file(content, file.filename, "video")
        
        # Validate video
        if not FileHandler.validate_video(file_path):
            raise HTTPException(status_code=400, detail="Invalid video file")
        
        # Get video info
        video_info = FileHandler.get_video_info(file_path)
        
        # Run detection
        output_path, all_detections, total_time, fps = yolo_detector.detect_video(file_path)
        
        # Calculate average metrics
        total_detections = sum(len(f['detections']) for f in all_detections)
        avg_detections_per_frame = total_detections / len(all_detections) if all_detections else 0
        
        # Save results to database
        result = DetectionResult(
            filename=file.filename,
            file_type="video",
            file_path=file_path,
            model_type="yolo",
            model_name="yolov8n",
            detections_count=int(total_detections),
            inference_time=total_time,
            fps=fps,
            output_video_path=output_path
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "result_id": result.id,
            "filename": file.filename,
            "model": "yolo",
            "video_info": video_info,
            "output_video": f"/api/v1/results/video/{result.id}",
            "total_detections": int(total_detections),
            "avg_detections_per_frame": avg_detections_per_frame,
            "total_inference_time": total_time,
            "fps": fps,
            "frames_processed": len(all_detections)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

# ==================== RESULTS ENDPOINTS ====================

@app.get("/api/v1/results/image/{result_id}")
async def get_result_image(result_id: int, db: Session = Depends(get_db)):
    """Get detected image result"""
    result = db.query(DetectionResult).filter(DetectionResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return FileResponse(result.output_image_path, media_type="image/jpeg")

@app.get("/api/v1/results/video/{result_id}")
async def get_result_video(result_id: int, db: Session = Depends(get_db)):
    """Get detected video result"""
    result = db.query(DetectionResult).filter(DetectionResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return FileResponse(result.output_video_path, media_type="video/mp4")

@app.get("/api/v1/results/{result_id}")
async def get_result_details(result_id: int, db: Session = Depends(get_db)):
    """Get detailed results"""
    result = db.query(DetectionResult).filter(DetectionResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "id": result.id,
        "filename": result.filename,
        "file_type": result.file_type,
        "model_type": result.model_type,
        "detections_count": result.detections_count,
        "inference_time": result.inference_time,
        "fps": result.fps,
        "precision": result.precision,
        "recall": result.recall,
        "map": result.map_score,
        "cpu_usage": result.cpu_usage,
        "memory_usage": result.memory_usage,
        "gpu_usage": result.gpu_usage,
        "created_at": result.created_at
    }

@app.get("/api/v1/history")
async def get_detection_history(
    skip: int = 0,
    limit: int = 10,
    model_type: Optional[str] = None,
    file_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get detection history"""
    query = db.query(DetectionResult)
    
    if model_type:
        query = query.filter(DetectionResult.model_type == model_type)
    
    if file_type:
        query = query.filter(DetectionResult.file_type == file_type)
    
    results = query.order_by(DetectionResult.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [
            {
                "id": r.id,
                "filename": r.filename,
                "file_type": r.file_type,
                "model_type": r.model_type,
                "detections_count": r.detections_count,
                "inference_time": r.inference_time,
                "fps": r.fps,
                "created_at": r.created_at
            }
            for r in results
        ]
    }

# ==================== COMPARISON ENDPOINTS ====================

@app.post("/api/v1/compare")
async def compare_results(
    rcnn_result_id: int,
    yolo_result_id: int,
    db: Session = Depends(get_db)
):
    """Compare RCNN and YOLO results"""
    rcnn_result = db.query(DetectionResult).filter(DetectionResult.id == rcnn_result_id).first()
    yolo_result = db.query(DetectionResult).filter(DetectionResult.id == yolo_result_id).first()
    
    if not rcnn_result or not yolo_result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # Create comparison
    comparison = MetricsCalculator.compare_detections(
        {
            "detections": rcnn_result.detected_objects or [],
            "inference_time": rcnn_result.inference_time
        },
        {
            "detections": yolo_result.detected_objects or [],
            "inference_time": yolo_result.inference_time
        }
    )
    
    # Save comparison to database
    db_comparison = ComparisonResult(
        filename=rcnn_result.filename,
        file_type=rcnn_result.file_type,
        rcnn_result_id=rcnn_result_id,
        rcnn_inference_time=rcnn_result.inference_time,
        rcnn_detections=rcnn_result.detections_count,
        rcnn_fps=rcnn_result.fps,
        rcnn_memory=rcnn_result.memory_usage,
        yolo_result_id=yolo_result_id,
        yolo_inference_time=yolo_result.inference_time,
        yolo_detections=yolo_result.detections_count,
        yolo_fps=yolo_result.fps,
        yolo_memory=yolo_result.memory_usage,
        faster_model=comparison['faster_model'],
        speed_advantage=comparison['speed_advantage_percent']
    )
    db.add(db_comparison)
    db.commit()
    
    return {
        "comparison_id": db_comparison.id,
        "filename": db_comparison.filename,
        "file_type": db_comparison.file_type,
        "rcnn": {
            "inference_time": rcnn_result.inference_time,
            "detections": rcnn_result.detections_count,
            "fps": rcnn_result.fps,
            "memory_mb": rcnn_result.memory_usage
        },
        "yolo": {
            "inference_time": yolo_result.inference_time,
            "detections": yolo_result.detections_count,
            "fps": yolo_result.fps,
            "memory_mb": yolo_result.memory_usage
        },
        "comparison": comparison
    }

@app.get("/api/v1/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_detections = db.query(DetectionResult).count()
    rcnn_count = db.query(DetectionResult).filter(DetectionResult.model_type == "rcnn").count()
    yolo_count = db.query(DetectionResult).filter(DetectionResult.model_type == "yolo").count()
    
    rcnn_avg_time = db.query(DetectionResult).filter(
        DetectionResult.model_type == "rcnn"
    ).count()
    
    return {
        "total_detections": total_detections,
        "rcnn_count": rcnn_count,
        "yolo_count": yolo_count,
        "comparisons": db.query(ComparisonResult).count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

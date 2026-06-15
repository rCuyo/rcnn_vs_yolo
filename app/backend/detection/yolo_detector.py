"""
YOLO (YOLOv8) object detection module
"""
from ultralytics import YOLO
import cv2
import numpy as np
import time
from typing import Tuple, List, Dict
from pathlib import Path
from config import settings

class YOLODetector:
    """YOLOv8 detector for object detection"""
    
    def __init__(self, model_name: str = "yolov8n.pt", device: str = None, 
                 confidence_threshold: float = 0.5):
        """
        Initialize YOLO detector
        
        Args:
            model_name: YOLO model size ('nano', 'small', 'medium', 'large', 'xlarge')
            device: 'cpu' or 'cuda'
            confidence_threshold: Minimum confidence score for detections
        """
        self.device = device or settings.DEVICE
        self.confidence_threshold = confidence_threshold
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        print(f"Loading YOLO model ({self.model_name}) on {self.device}...")
        
        # Map model names to Ultralytics format
        model_map = {
            "yolov8n": "yolov8n.pt",
            "yolov8s": "yolov8s.pt",
            "yolov8m": "yolov8m.pt",
            "yolov8l": "yolov8l.pt",
            "yolov8x": "yolov8x.pt"
        }
        
        model_path = model_map.get(self.model_name, self.model_name)
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        print("YOLO model loaded successfully")
    
    def detect_image(self, image_path: str) -> Tuple[np.ndarray, List[Dict], float]:
        """
        Detect objects in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (annotated_image, detections, inference_time)
        """
        # Read image
        image = cv2.imread(image_path)
        
        # Run inference
        start_time = time.time()
        results = self.model.predict(image, conf=self.confidence_threshold, verbose=False)
        inference_time = time.time() - start_time
        
        # Extract detections
        detections = self._extract_detections(results[0])
        
        # Annotate image
        annotated_image = self._annotate_image(image, detections)
        
        return annotated_image, detections, inference_time
    
    def detect_frame(self, frame: np.ndarray) -> Tuple[List[Dict], float]:
        """Run detection on a single numpy BGR frame (from webcam)."""
        start_time = time.time()
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        inference_time = time.time() - start_time
        detections = self._extract_detections(results[0])
        return detections, inference_time

    def detect_video(self, video_path: str, callback=None) -> Tuple[str, List[Dict], float, float]:
        """
        Detect objects in video frames
        
        Args:
            video_path: Path to video file
            callback: Callback function for progress updates
            
        Returns:
            Tuple of (output_video_path, all_detections, total_inference_time, fps)
        """
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer
        output_path = str(settings.RESULTS_DIR / f"yolo_{int(time.time())}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        all_detections = []
        total_inference_time = 0
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run inference
            start_time = time.time()
            results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
            inference_time = time.time() - start_time
            total_inference_time += inference_time
            
            # Extract and annotate detections
            detections = self._extract_detections(results[0])
            annotated_frame = self._annotate_image(frame, detections)
            
            # Save detections with frame info
            frame_detections = {
                'frame_idx': frame_idx,
                'detections': detections,
                'inference_time': inference_time
            }
            all_detections.append(frame_detections)
            
            # Write frame
            out.write(annotated_frame)
            
            frame_idx += 1
            if callback and frame_idx % 30 == 0:
                callback({"progress": (frame_idx / frame_count) * 100})
        
        cap.release()
        out.release()
        
        avg_fps = frame_idx / total_inference_time if total_inference_time > 0 else 0
        
        return output_path, all_detections, total_inference_time, avg_fps
    
    def _extract_detections(self, results) -> List[Dict]:
        """
        Extract detection information from model results
        
        Args:
            results: YOLO model results object
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        if results.boxes is not None:
            for box in results.boxes:
                conf = float(box.conf)
                cls_id = int(box.cls)
                
                # Get class name
                class_name = self.model.names[cls_id]
                
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                detection = {
                    'class_name': class_name,
                    'class_id': cls_id,
                    'confidence': conf,
                    'bbox': {
                        'x1': float(x1),
                        'y1': float(y1),
                        'x2': float(x2),
                        'y2': float(y2),
                        'width': float(x2 - x1),
                        'height': float(y2 - y1)
                    }
                }
                detections.append(detection)
        
        return sorted(detections, key=lambda x: x['confidence'], reverse=True)
    
    def _annotate_image(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Prepare label
            label = f"{detection['class_name']} ({detection['confidence']:.2f})"
            
            # Draw label background
            (text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            cv2.rectangle(annotated, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 0, 255), -1)
            
            # Draw label text
            cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return annotated

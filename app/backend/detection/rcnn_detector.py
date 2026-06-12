"""
RCNN (Faster R-CNN) object detection module
"""
import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image
import numpy as np
import cv2
import time
from typing import Tuple, List, Dict, Any
from config import settings

class RCNNDetector:
    """Faster R-CNN detector for object detection"""
    
    COCO_CLASSES = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
        'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
        'stop sign', 'parking meter', 'bench', 'cat', 'dog', 'horse', 'sheep',
        'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
        'umbrella', 'N/A', 'N/A', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
        'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle',
        'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
        'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A',
        'dining table', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse',
        'remote', 'keyboard', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'N/A', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    def __init__(self, device: str = None, confidence_threshold: float = 0.5):
        """
        Initialize RCNN detector
        
        Args:
            device: 'cpu' or 'cuda'
            confidence_threshold: Minimum confidence score for detections
        """
        self.device = device or settings.DEVICE
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Faster R-CNN model"""
        print(f"Loading Faster R-CNN model on {self.device}...")
        self.model = fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.to(self.device)
        self.model.eval()
        print("Faster R-CNN model loaded successfully")
    
    def detect_image(self, image_path: str) -> Tuple[np.ndarray, List[Dict], float]:
        """
        Detect objects in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (annotated_image, detections, inference_time)
        """
        # Read image
        image = Image.open(image_path).convert('RGB')
        image_cv = cv2.imread(image_path)
        
        # Start timing
        start_time = time.time()
        
        # Prepare image for model
        image_tensor = F.to_tensor(image).to(self.device)
        
        # Run inference
        with torch.no_grad():
            predictions = self.model([image_tensor])
        
        inference_time = time.time() - start_time
        
        # Extract detections
        detections = self._extract_detections(predictions[0], image_cv.shape[:2])
        
        # Annotate image
        annotated_image = self._annotate_image(image_cv, detections)
        
        return annotated_image, detections, inference_time
    
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
        output_path = str(settings.RESULTS_DIR / f"rcnn_{int(time.time())}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        all_detections = []
        total_inference_time = 0
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB for the model
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(frame_rgb)
            
            # Run inference
            start_time = time.time()
            image_tensor = F.to_tensor(image_pil).to(self.device)
            
            with torch.no_grad():
                predictions = self.model([image_tensor])
            
            inference_time = time.time() - start_time
            total_inference_time += inference_time
            
            # Extract and annotate detections
            detections = self._extract_detections(predictions[0], frame.shape[:2])
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
    
    def _extract_detections(self, predictions: Dict, image_shape: Tuple) -> List[Dict]:
        """
        Extract detection information from model predictions
        
        Args:
            predictions: Model output predictions
            image_shape: Original image shape (height, width)
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        boxes = predictions['boxes'].cpu().numpy()
        scores = predictions['scores'].cpu().numpy()
        labels = predictions['labels'].cpu().numpy()
        
        for box, score, label in zip(boxes, scores, labels):
            if score >= self.confidence_threshold:
                detection = {
                    'class_name': self.COCO_CLASSES[label],
                    'class_id': int(label),
                    'confidence': float(score),
                    'bbox': {
                        'x1': float(box[0]),
                        'y1': float(box[1]),
                        'x2': float(box[2]),
                        'y2': float(box[3]),
                        'width': float(box[2] - box[0]),
                        'height': float(box[3] - box[1])
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
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Prepare label
            label = f"{detection['class_name']} ({detection['confidence']:.2f})"
            
            # Draw label background
            (text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            cv2.rectangle(annotated, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        return annotated

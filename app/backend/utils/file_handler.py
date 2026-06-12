"""
Utility functions for image and video processing
"""
import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
import cv2
from PIL import Image
import numpy as np
from config import settings

class FileHandler:
    """Handle file upload and processing"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.flv', '.mkv', '.webm'}
    
    @staticmethod
    def save_upload_file(file_content: bytes, filename: str, file_type: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content in bytes
            filename: Original filename
            file_type: Type of file ('image' or 'video')
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine directory
        if file_type == 'image':
            save_dir = settings.IMAGES_DIR
        elif file_type == 'video':
            save_dir = settings.VIDEOS_DIR
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        
        # Save file
        file_path = save_dir / unique_filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return str(file_path)
    
    @staticmethod
    def validate_image(file_path: str) -> bool:
        """Validate if file is a valid image"""
        try:
            ext = Path(file_path).suffix.lower()
            if ext not in FileHandler.ALLOWED_IMAGE_EXTENSIONS:
                return False
            
            img = Image.open(file_path)
            img.verify()
            return True
        except:
            return False
    
    @staticmethod
    def validate_video(file_path: str) -> bool:
        """Validate if file is a valid video"""
        try:
            ext = Path(file_path).suffix.lower()
            if ext not in FileHandler.ALLOWED_VIDEO_EXTENSIONS:
                return False
            
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return False
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            return frame_count > 0
        except:
            return False
    
    @staticmethod
    def get_image_dimensions(file_path: str) -> Tuple[int, int]:
        """Get image dimensions"""
        img = Image.open(file_path)
        return img.size  # (width, height)
    
    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """Get video information"""
        cap = cv2.VideoCapture(file_path)
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration_seconds': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        
        cap.release()
        return info
    
    @staticmethod
    def resize_image_if_needed(file_path: str, max_size: int = 1920) -> str:
        """
        Resize image if it exceeds max size
        
        Args:
            file_path: Path to image file
            max_size: Maximum dimension size
            
        Returns:
            Path to (potentially resized) image
        """
        img = Image.open(file_path)
        
        if img.width > max_size or img.height > max_size:
            # Calculate new dimensions maintaining aspect ratio
            ratio = max_size / max(img.width, img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img.save(file_path, quality=95)
        
        return file_path

class ImageProcessor:
    """Process and manipulate images"""
    
    @staticmethod
    def save_detection_result(image: np.ndarray, output_path: str) -> str:
        """
        Save detection result image
        
        Args:
            image: Processed image with annotations
            output_path: Path to save image
            
        Returns:
            Path to saved image
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)
        return output_path
    
    @staticmethod
    def convert_image_format(input_path: str, output_format: str = 'png') -> str:
        """
        Convert image to different format
        
        Args:
            input_path: Path to input image
            output_format: Output format (png, jpg, webp, etc)
            
        Returns:
            Path to converted image
        """
        img = Image.open(input_path)
        output_path = str(Path(input_path).with_suffix(f'.{output_format}'))
        img.save(output_path, quality=95)
        return output_path
    
    @staticmethod
    def get_image_base64(image_path: str) -> str:
        """Convert image to base64 string"""
        import base64
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        return base64.b64encode(image_data).decode('utf-8')

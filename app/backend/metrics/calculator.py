"""
Metrics calculation and evaluation module
"""
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics import precision_score, recall_score, average_precision_score
import psutil
import GPUtil

class MetricsCalculator:
    """Calculate performance metrics for object detection models"""
    
    @staticmethod
    def calculate_iou(box1: Dict, box2: Dict) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes
        
        Args:
            box1, box2: Bounding boxes with 'x1', 'y1', 'x2', 'y2' keys
            
        Returns:
            IoU value (0-1)
        """
        # Calculate intersection area
        x1_inter = max(box1['x1'], box2['x1'])
        y1_inter = max(box1['y1'], box2['y1'])
        x2_inter = min(box1['x2'], box2['x2'])
        y2_inter = min(box1['y2'], box2['y2'])
        
        if x2_inter < x1_inter or y2_inter < y1_inter:
            return 0.0
        
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        
        # Calculate union area
        box1_area = (box1['x2'] - box1['x1']) * (box1['y2'] - box1['y1'])
        box2_area = (box2['x2'] - box2['x1']) * (box2['y2'] - box2['y1'])
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    @staticmethod
    def calculate_ap(detections: List[Dict], ground_truth: List[Dict], 
                    iou_threshold: float = 0.5) -> float:
        """
        Calculate Average Precision for a class
        
        Args:
            detections: List of predicted detections
            ground_truth: List of ground truth annotations
            iou_threshold: IoU threshold for match
            
        Returns:
            Average Precision value
        """
        if len(ground_truth) == 0:
            return 0.0
        
        # Sort detections by confidence
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        tp = np.zeros(len(sorted_dets))
        fp = np.zeros(len(sorted_dets))
        
        gt_matched = np.zeros(len(ground_truth))
        
        for i, det in enumerate(sorted_dets):
            best_iou = 0
            best_gt_idx = -1
            
            for j, gt in enumerate(ground_truth):
                if gt_matched[j]:
                    continue
                
                iou = MetricsCalculator.calculate_iou(det['bbox'], gt['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = j
            
            if best_iou >= iou_threshold:
                tp[i] = 1
                gt_matched[best_gt_idx] = 1
            else:
                fp[i] = 1
        
        # Calculate precision and recall
        tp_cumsum = np.cumsum(tp)
        fp_cumsum = np.cumsum(fp)
        
        recalls = tp_cumsum / len(ground_truth)
        precisions = tp_cumsum / (tp_cumsum + fp_cumsum)
        
        # Calculate AP
        ap = 0
        prev_recall = 0
        for i in range(len(precisions)):
            if recalls[i] != prev_recall:
                ap += precisions[i] * (recalls[i] - prev_recall)
                prev_recall = recalls[i]
        
        return ap
    
    @staticmethod
    def calculate_precision_recall(detections: List[Dict], 
                                   ground_truth: List[Dict]) -> Tuple[float, float]:
        """
        Calculate precision and recall
        
        Args:
            detections: List of predicted detections
            ground_truth: List of ground truth annotations
            
        Returns:
            Tuple of (precision, recall)
        """
        if len(ground_truth) == 0:
            return 0.0, 0.0
        
        if len(detections) == 0:
            return 0.0, 0.0
        
        # Simple matching: match detections to GT based on IoU
        gt_matched = np.zeros(len(ground_truth))
        matches = 0
        
        for det in detections:
            for i, gt in enumerate(ground_truth):
                if gt_matched[i]:
                    continue
                
                iou = MetricsCalculator.calculate_iou(det['bbox'], gt['bbox'])
                if iou >= 0.5:
                    matches += 1
                    gt_matched[i] = 1
                    break
        
        precision = matches / len(detections) if detections else 0
        recall = matches / len(ground_truth) if ground_truth else 0
        
        return precision, recall
    
    @staticmethod
    def get_system_metrics() -> Dict:
        """
        Get current system resource usage metrics
        
        Returns:
            Dictionary with CPU, memory, and GPU metrics
        """
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_mb': psutil.virtual_memory().used / (1024 ** 2),
            'memory_percent': psutil.virtual_memory().percent
        }
        
        # Try to get GPU metrics
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                metrics['gpu_available'] = True
                metrics['gpu_percent'] = gpu.load * 100
                metrics['gpu_memory_mb'] = gpu.memoryUsed
            else:
                metrics['gpu_available'] = False
        except:
            metrics['gpu_available'] = False
        
        return metrics
    
    @staticmethod
    def calculate_map(detections_list: List[List[Dict]], 
                     ground_truth_list: List[List[Dict]]) -> float:
        """
        Calculate mean Average Precision across multiple images/frames
        
        Args:
            detections_list: List of detection lists for each image
            ground_truth_list: List of ground truth lists for each image
            
        Returns:
            Mean Average Precision
        """
        aps = []
        
        for detections, ground_truth in zip(detections_list, ground_truth_list):
            ap = MetricsCalculator.calculate_ap(detections, ground_truth)
            aps.append(ap)
        
        return np.mean(aps) if aps else 0.0
    
    @staticmethod
    def compare_detections(rcnn_results: Dict, yolo_results: Dict) -> Dict:
        """
        Compare RCNN and YOLO detection results
        
        Args:
            rcnn_results: RCNN detection results
            yolo_results: YOLO detection results
            
        Returns:
            Comparison analysis dictionary
        """
        comparison = {
            'inference_time_ratio': yolo_results['inference_time'] / rcnn_results['inference_time']
            if rcnn_results['inference_time'] > 0 else 0,
            'detection_count_diff': len(yolo_results['detections']) - len(rcnn_results['detections']),
            'faster_model': 'yolo' if yolo_results['inference_time'] < rcnn_results['inference_time'] else 'rcnn',
            'speed_advantage_percent': abs(
                (yolo_results['inference_time'] - rcnn_results['inference_time']) / 
                max(rcnn_results['inference_time'], yolo_results['inference_time']) * 100
            ) if max(rcnn_results['inference_time'], yolo_results['inference_time']) > 0 else 0
        }
        
        return comparison

"""
Tracking utility functions.

This module provides utility functions for tracking operations,
including bounding box conversions, IoU calculations, and detection filtering.
"""

import numpy as np
from typing import List, Tuple, Optional
from app.detectors.detection import Detection


def detection_to_xywh(detection: Detection) -> Tuple[float, float, float, float]:
    """
    Convert detection bounding box to (x, y, w, h) format.
    
    Args:
        detection: Detection object with (x1, y1, x2, y2) bounding box
        
    Returns:
        Tuple of (x, y, width, height)
    """
    x1, y1, x2, y2 = detection.bounding_box
    return (float(x1), float(y1), float(x2 - x1), float(y2 - y1))


def detection_to_xyxy(detection: Detection) -> Tuple[float, float, float, float]:
    """
    Convert detection bounding box to (x1, y1, x2, y2) format.
    
    Args:
        detection: Detection object
        
    Returns:
        Tuple of (x1, y1, x2, y2)
    """
    return tuple(float(coord) for coord in detection.bounding_box)


def detections_to_numpy_array(detections: List[Detection]) -> np.ndarray:
    """
    Convert list of detections to numpy array for ByteTrack.
    
    ByteTrack expects format: [[x1, y1, w, h, confidence], ...]
    
    Args:
        detections: List of Detection objects
        
    Returns:
        Numpy array of shape (N, 5) with [x, y, w, h, conf]
    """
    if not detections:
        return np.zeros((0, 5), dtype=np.float32)
    
    array = []
    for detection in detections:
        x, y, w, h = detection_to_xywh(detection)
        array.append([x, y, w, h, detection.confidence])
    
    return np.array(array, dtype=np.float32)


def filter_detections_by_class(
    detections: List[Detection],
    class_names: List[str]
) -> List[Detection]:
    """
    Filter detections by class name.
    
    Args:
        detections: List of Detection objects
        class_names: List of class names to keep
        
    Returns:
        Filtered list of detections
    """
    return [d for d in detections if d.class_name in class_names]


def filter_detections_by_confidence(
    detections: List[Detection],
    min_confidence: float
) -> List[Detection]:
    """
    Filter detections by minimum confidence.
    
    Args:
        detections: List of Detection objects
        min_confidence: Minimum confidence threshold
        
    Returns:
        Filtered list of detections
    """
    return [d for d in detections if d.confidence >= min_confidence]


def calculate_iou(
    box1: Tuple[float, float, float, float],
    box2: Tuple[float, float, float, float]
) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        box1: First bounding box (x1, y1, x2, y2)
        box2: Second bounding box (x1, y1, x2, y2)
        
    Returns:
        IoU value between 0 and 1
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i <= x1_i or y2_i <= y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_area(box: Tuple[float, float, float, float]) -> float:
    """
    Calculate area of bounding box.
    
    Args:
        box: Bounding box (x1, y1, x2, y2)
        
    Returns:
        Area of the box
    """
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)


def calculate_center(box: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """
    Calculate center point of bounding box.
    
    Args:
        box: Bounding box (x1, y1, x2, y2)
        
    Returns:
        Center point (x, y)
    """
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def merge_overlapping_detections(
    detections: List[Detection],
    iou_threshold: float = 0.5
) -> List[Detection]:
    """
    Merge overlapping detections of the same class.
    
    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold for merging
        
    Returns:
        List of merged detections
    """
    if len(detections) <= 1:
        return detections
    
    # Group by class
    class_groups = {}
    for detection in detections:
        if detection.class_name not in class_groups:
            class_groups[detection.class_name] = []
        class_groups[detection.class_name].append(detection)
    
    merged = []
    
    for class_name, class_detections in class_groups.items():
        # Sort by confidence (highest first)
        class_detections.sort(key=lambda d: d.confidence, reverse=True)
        
        # Merge overlapping detections
        keep = []
        for detection in class_detections:
            should_keep = True
            for kept in keep:
                iou = calculate_iou(detection.bounding_box, kept.bounding_box)
                if iou > iou_threshold:
                    should_keep = False
                    break
            if should_keep:
                keep.append(detection)
        
        merged.extend(keep)
    
    return merged


def validate_bounding_box(box: Tuple[int, int, int, int]) -> bool:
    """
    Validate that bounding box coordinates are valid.
    
    Args:
        box: Bounding box (x1, y1, x2, y2)
        
    Returns:
        True if valid, False otherwise
    """
    x1, y1, x2, y2 = box
    return (
        x1 >= 0 and y1 >= 0 and
        x2 > x1 and y2 > y1 and
        isinstance(x1, (int, float)) and
        isinstance(y1, (int, float)) and
        isinstance(x2, (int, float)) and
        isinstance(y2, (int, float))
    )

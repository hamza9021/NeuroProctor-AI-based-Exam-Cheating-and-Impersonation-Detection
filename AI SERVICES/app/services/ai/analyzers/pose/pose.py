"""Pose result data model."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PoseResult:
    """Result of pose estimation for a tracked person.
    
    Attributes:
        track_id: Associated DeepSORT track ID.
        bbox: Bounding box [x1, y1, x2, y2].
        keypoints: List of (x, y) keypoint coordinates.
        keypoint_confidences: List of keypoint confidence values.
        confidence: Overall pose confidence.
        is_valid: Whether pose passed validation.
        visible_keypoints: Number of visible keypoints.
    """
    
    track_id: int
    bbox: Tuple[float, float, float, float]
    keypoints: List[Tuple[float, float]]
    keypoint_confidences: List[float]
    confidence: float
    is_valid: bool
    visible_keypoints: int = 0

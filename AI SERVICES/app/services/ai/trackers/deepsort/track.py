"""Track model for DeepSORT tracking results."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Track:
    """Represents a tracked object in a frame.
    
    This model stores tracking information for a detected object.
    Future modules will append pose, head_pose, face, and risk_score.
    """
    
    track_id: int
    """Unique identifier for this track."""
    
    bbox: Tuple[int, int, int, int]
    """Bounding box as (x1, y1, x2, y2)."""
    
    center: Tuple[float, float]
    """Center point as (x, y)."""
    
    confidence: float
    """Detection confidence score."""
    
    is_confirmed: bool
    """Whether the track is confirmed (stable)."""
    
    age: int
    """Number of frames since track creation."""
    
    hits: int
    """Number of successful detections for this track."""
    
    time_since_update: int
    """Frames since last update."""
    
    class_name: str
    """Class name of the detected object."""

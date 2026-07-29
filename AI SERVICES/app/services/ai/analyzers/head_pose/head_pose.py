"""Head pose result model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HeadPoseResult:
    """Result of head pose estimation for a single track.
    
    Attributes:
        track_id: DeepSORT track ID.
        face_bbox: Face bounding box (x1, y1, x2, y2).
        yaw: Yaw angle in degrees (left-right rotation).
        pitch: Pitch angle in degrees (up-down rotation).
        roll: Roll angle in degrees (tilt rotation).
        confidence: Optional confidence score.
        is_valid: Whether the result passed validation.
    """
    
    track_id: int
    face_bbox: tuple[float, float, float, float]
    yaw: float
    pitch: float
    roll: float
    confidence: Optional[float] = None
    is_valid: bool = True

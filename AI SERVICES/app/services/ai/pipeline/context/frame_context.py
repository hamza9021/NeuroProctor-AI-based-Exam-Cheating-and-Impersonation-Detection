"""Frame context data structure for pipeline processing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Detection:
    """Single object detection result.
    
    Attributes:
        track_id: Optional tracking ID (None until tracking stage).
        class_name: Human-readable class name.
        class_id: Original YOLO class ID.
        confidence: Detection confidence score (0-1).
        bbox: Bounding box [x1, y1, x2, y2].
        center: Center point [x, y].
        width: Bounding box width.
        height: Bounding box height.
    """
    track_id: Optional[int] = None
    class_name: str = ""
    class_id: int = 0
    confidence: float = 0.0
    bbox: List[float] = field(default_factory=list)
    center: List[float] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0


@dataclass
class FrameContext:
    """Context for a single frame in the processing pipeline.
    
    This dataclass stores information about a frame as it passes through
    the pipeline stages. It is designed to be immutable and passed between
    stages without modification.
    
    Attributes:
        frame: The frame data (numpy array or similar).
        frame_number: Sequential number of the frame in the video.
        timestamp: Timestamp when the frame was captured.
        metadata: Additional metadata about the frame.
        detections: List of object detections for this frame.
        tracks: List of tracking results for this frame.
        poses: Dictionary of pose results keyed by track_id.
    """
    
    frame: Any
    frame_number: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    detections: List[Detection] = field(default_factory=list)
    tracks: List[Any] = field(default_factory=list)
    poses: Dict[int, Any] = field(default_factory=dict)

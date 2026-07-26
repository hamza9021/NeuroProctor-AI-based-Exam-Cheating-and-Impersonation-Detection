"""Frame context data structure for pipeline processing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


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
    """
    
    frame: Any
    frame_number: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

"""
FrameContext - Data container for frame information.

This dataclass stores all information related to a single video frame
as it passes through the AI pipeline. It serves as a pure data container
with no business logic, following the Single Responsibility Principle.

The context is passed between pipeline stages, with each stage adding
or modifying relevant fields. This design enables loose coupling between
stages - each stage only needs to know about the fields it uses.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FrameContext:
    """
    Data container for frame-level information in the AI pipeline.

    This class holds all data related to a single frame as it progresses
    through processing stages. Each stage can add or modify fields without
    affecting other stages, enabling modular and extensible pipeline design.

    Attributes:
        frame: The raw frame data (numpy array or similar).
        frame_number: Sequential index of the frame in the video.
        timestamp: Timestamp when the frame was captured or processed.
        metadata: Additional metadata about the frame or video source.
        detections: Object detection results from YOLO or similar.
        tracks: Tracking information from DeepSORT or similar.
        poses: Pose estimation results from pose models.
        head_pose: Head orientation and direction information.
        faces: Face recognition results and embeddings.
        events: Detected events (e.g., cheating behaviors).
        suspicion_score: Computed suspicion level for this frame.
        annotations: Visualization data for output rendering.
        stage_outputs: Raw outputs from individual pipeline stages.
    """

    # Core frame data
    frame: Optional[Any] = None
    frame_number: int = 0
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # AI processing results
    detections: List[Any] = field(default_factory=list)
    tracks: List[Any] = field(default_factory=list)
    poses: List[Any] = field(default_factory=list)
    head_pose: Dict[str, Any] = field(default_factory=dict)
    faces: List[Any] = field(default_factory=list)


    # Analysis results
    events: List[Dict[str, Any]] = field(default_factory=list)
    suspicion_score: float = 0.0
    annotations: Dict[str, Any] = field(default_factory=dict)

    # Stage-specific outputs (for debugging and analysis)
    stage_outputs: Dict[str, Any] = field(default_factory=dict)

    def add_detection(self, detection: Any) -> None:
        """Add a detection to the context."""
        self.detections.append(detection)

    def add_track(self, track: Any) -> None:
        """Add a track to the context."""
        self.tracks.append(track)

    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the context."""
        self.events.append(event)

    def set_stage_output(self, stage_name: str, output: Any) -> None:
        """Store the output of a specific pipeline stage."""
        self.stage_outputs[stage_name] = output

    def get_stage_output(self, stage_name: str) -> Optional[Any]:
        """Retrieve the output of a specific pipeline stage."""
        return self.stage_outputs.get(stage_name)

    def reset_frame_data(self) -> None:
        """Reset frame-specific data while preserving metadata."""
        self.detections.clear()
        self.tracks.clear()
        self.poses.clear()
        self.faces.clear()
        self.events.clear()
        self.suspicion_score = 0.0
        self.annotations.clear()
        self.stage_outputs.clear()
        logger.debug("FrameContext data reset for frame %d", self.frame_number)

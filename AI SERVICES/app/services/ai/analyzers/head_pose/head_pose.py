"""Head pose result model."""

import time
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class HeadPoseResult:
    """Result of head pose estimation for a single track.

    Attributes:
        track_id: DeepSORT track ID.
        face_bbox: Tight face/head bounding box (x1, y1, x2, y2) in frame
            pixel coordinates.
        yaw: Smoothed yaw angle in degrees (left-right rotation).
        pitch: Smoothed pitch angle in degrees (up-down rotation).
        roll: Smoothed roll angle in degrees (tilt rotation).
        raw_yaw: Raw yaw angle in degrees from SixDRepNet (unsmoothed).
        raw_pitch: Raw pitch angle in degrees from SixDRepNet (unsmoothed).
        raw_roll: Raw roll angle in degrees from SixDRepNet (unsmoothed).
        confidence: Optional confidence score.
        is_valid: Whether the result passed validation.
        person_bbox: Full DeepSORT person bounding box (x1, y1, x2, y2)
            used for positioning text overlays relative to the student's
            silhouette rather than the narrow face crop.
        axis_origin: Pre-clamped (cx, cy) pixel coordinates for the 3-D
            head-pose axis origin (nose keypoint or face-bbox centre).
        frame_index: The ``FrameContext.frame_number`` this result was
            produced for.  Used by the annotator to reject stale results
            that belong to a different frame.  ``None`` means unknown.
        source_timestamp: Wall-clock time (``time.monotonic()``) when
            inference finished.  Used for async out-of-order detection.
        quality_score: Frame quality score (0.0 to 1.0) from quality evaluator.
        quality_valid_for_smoothing: Whether frame quality is sufficient for temporal smoothing.
        quality_valid_for_rules: Whether frame quality is sufficient for cheating rule evaluation.
        quality_reason: Human-readable reason for quality decision.
    """

    track_id: int
    face_bbox: Tuple[float, float, float, float]
    yaw: float
    pitch: float
    roll: float
    raw_yaw: Optional[float] = None
    raw_pitch: Optional[float] = None
    raw_roll: Optional[float] = None
    confidence: Optional[float] = None
    is_valid: bool = True
    person_bbox: Optional[Tuple[float, float, float, float]] = None
    axis_origin: Optional[Tuple[int, int]] = None
    frame_index: Optional[int] = None
    source_timestamp: Optional[float] = None
    quality_score: float = 1.0
    quality_valid_for_smoothing: bool = True
    quality_valid_for_rules: bool = True
    quality_reason: Optional[str] = None


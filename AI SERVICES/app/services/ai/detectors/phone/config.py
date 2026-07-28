"""Phone detection configuration."""

from dataclasses import dataclass
from typing import List


@dataclass
class PhoneDetectionConfig:
    """Configuration for phone detection.
    
    Attributes:
        enabled: Whether phone detection is enabled.
        model_path: Path to dedicated phone model (empty to use main YOLO).
        class_name: Phone class name to detect.
        confidence: Phone-specific confidence threshold.
        image_size: Phone inference image size.
        fallback_image_sizes: Fallback image sizes for GPU memory constraints.
        min_box_area: Minimum phone bounding box area.
        roi_enabled: Enable student ROI phone detection.
        roi_expansion: ROI expansion factor.
        temporal_confirm_frames: Frames to confirm a phone detection.
        temporal_max_missed_frames: Max missed frames before expiration.
        association_iou: IoU threshold for student-phone association.
        deduplication_iou: IoU threshold for phone deduplication.
        debug_enabled: Debug mode for phone detection.
        debug_max_frames: Max debug frames to save.
        raw_debug_confidence: Raw diagnostic mode confidence threshold.
        raw_debug_image_size: Raw diagnostic mode image size.
        test_max_frames: Test configuration: max frames to process (0 = unlimited).
        test_start_frame: Test configuration: start frame.
        test_end_frame: Test configuration: end frame (0 = end of video).
        test_frame_step: Test configuration: frame step.
    """
    
    enabled: bool = True
    model_path: str = ""
    class_name: str = "cell phone"
    confidence: float = 0.10
    image_size: int = 960
    fallback_image_sizes: List[int] = None
    min_box_area: int = 10
    roi_enabled: bool = True
    roi_expansion: float = 0.15
    temporal_confirm_frames: int = 3
    temporal_max_missed_frames: int = 2
    association_iou: float = 0.10
    deduplication_iou: float = 0.50
    debug_enabled: bool = False
    debug_max_frames: int = 20
    raw_debug_confidence: float = 0.01
    raw_debug_image_size: int = 1280
    test_max_frames: int = 0
    test_start_frame: int = 0
    test_end_frame: int = 0
    test_frame_step: int = 1
    # Association configuration
    association_switch_confirm_frames: int = 3
    association_switch_margin: float = 0.20
    max_centre_distance: float = 100.0
    min_association_score: float = 0.3
    
    def __post_init__(self):
        """Initialize default values."""
        if self.fallback_image_sizes is None:
            self.fallback_image_sizes = [768, 640]

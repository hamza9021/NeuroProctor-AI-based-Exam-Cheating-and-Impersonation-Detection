"""YOLO26 pose estimation configuration."""

from dataclasses import dataclass


@dataclass
class YoloPoseConfig:
    """Configuration for YOLO26 pose estimation."""

    model_path: str = "yolo26m-pose.pt"
    """Official Ultralytics YOLO26 medium pose model."""

    device: str = "cuda:0"
    """Use the first CUDA GPU explicitly."""

    confidence: float = 0.15
    """
    Minimum person-pose detection confidence.

    0.15 provides better recall for distant students while rejecting
    extremely weak detections.
    """

    iou: float = 0.50
    """
    NMS IoU threshold.

    Note: this only affects inference when end2end=False because YOLO26
    uses end-to-end, NMS-free inference by default.
    """

    image_size: int = 640
    """
    Inference resolution.

    640 is the recommended balance between pose accuracy, GPU memory,
    and processing speed for a GTX 1650 Ti.
    """

    keypoint_confidence: float = 0.20
    """
    Minimum confidence for individual body keypoints.

    Slightly lower than 0.25 to retain partially visible keypoints
    for seated or occluded students.
    """

    track_iou_threshold: float = 0.10
    """
    Minimum overlap between tracking and pose bounding boxes.

    Prevents almost unrelated boxes from being associated while still
    allowing moderate differences between detector and pose boxes.
    """

    use_half_precision: bool = True
    """
    Enable FP16 inference on CUDA to reduce GPU memory usage and improve speed.
    """

    socket_log_detail_level: str = "summary"
    """Use summary logging during normal video processing."""

    frame_log_interval: int = 30
    """
    Emit frame-level logs approximately once per second for 30 FPS video.
    """

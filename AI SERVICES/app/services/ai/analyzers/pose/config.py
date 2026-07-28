"""YOLO pose estimation configuration."""

from dataclasses import dataclass


@dataclass
class YoloPoseConfig:
    """Configuration for YOLO pose estimation.
    
    Stores only configuration parameters. No logic.
    """
    
    model_path: str = "yolo26m-pose.pt"
    """Path to YOLO pose model. Note: This is a custom model - ensure file exists locally."""
    
    device: str = "auto"
    """Device for inference: 'auto', 'cuda', or 'cpu'."""
    
    confidence: float = 0.05
    """Confidence threshold for pose detection."""
    
    iou: float = 0.45
    """IOU threshold for NMS."""
    
    image_size: int = 640
    """Image size for inference."""
    
    keypoint_confidence: float = 0.25
    """Minimum confidence for keypoints."""
    
    track_iou_threshold: float = 0.01
    """IoU threshold for track-to-pose association."""
    
    use_half_precision: bool = True
    """Use half precision for faster inference."""
    
    socket_log_detail_level: str = "detailed"
    """Log level: 'summary', 'detailed', or 'debug'."""
    
    frame_log_interval: int = 10
    """Emit detailed frame logs every N frames."""

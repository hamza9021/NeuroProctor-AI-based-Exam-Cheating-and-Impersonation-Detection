"""YOLO detection configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class YOLOConfig:
    """Configuration for YOLO detection.
    
    Attributes:
        model_path: Path to YOLO model weights.
        confidence: Confidence threshold for detections.
        iou: IOU threshold for NMS.
        image_size: Image size for inference.
        device: Device to use ('cpu', 'cuda', or 'auto').
    """
    
    model_path: str
    confidence: float = 0.25
    iou: float = 0.45
    image_size: int = 640
    device: str = "auto"

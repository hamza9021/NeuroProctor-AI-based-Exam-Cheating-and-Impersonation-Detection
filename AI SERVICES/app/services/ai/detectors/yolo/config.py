"""YOLO detection configuration."""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class YOLOConfig:
    """Configuration for YOLO detection.
    
    Attributes:
        model_path: Path to YOLO model weights.
        confidence: Default confidence threshold for detections.
        iou: IOU threshold for NMS.
        image_size: Image size for inference.
        device: Device to use ('cpu', 'cuda', or 'auto').
        class_confidence: Class-specific confidence thresholds.
    """
    
    model_path: str
    confidence: float = 0.25
    iou: float = 0.45
    image_size: int = 640
    device: str = "auto"
    class_confidence: Dict[str, float] = None
    
    def __post_init__(self):
        """Initialize default class-specific confidence thresholds."""
        if self.class_confidence is None:
            self.class_confidence = {
                "person": 0.25,
                "cell phone": 0.10,
            }
    
    def get_class_confidence(self, class_name: str) -> float:
        """Get confidence threshold for a specific class.
        
        Args:
            class_name: Name of the class.
            
        Returns:
            Confidence threshold for the class.
        """
        return self.class_confidence.get(class_name, self.confidence)

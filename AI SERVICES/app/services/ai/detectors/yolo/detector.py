"""YOLO detector."""

import logging
import numpy as np
from ultralytics import YOLO

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.exceptions import InferenceError, InvalidFrameError

logger = logging.getLogger(__name__)


class Detector:
    """YOLO object detector."""
    
    def __init__(self, model: YOLO, config: YOLOConfig):
        """Initialize detector with loaded model.
        
        Args:
            model: Loaded YOLO model.
            config: YOLO configuration.
        """
        self._model = model
        self._config = config
    
    def detect(self, frame: np.ndarray):
        """Run object detection on frame.
        
        Args:
            frame: Input frame (numpy array).
            
        Returns:
            Raw YOLO detection results.
            
        Raises:
            InvalidFrameError: If frame is invalid.
            InferenceError: If inference fails.
        """
        if frame is None or frame.size == 0:
            raise InvalidFrameError("Frame is empty or invalid")
        
        try:
            results = self._model(
                frame,
                conf=self._config.confidence,
                iou=self._config.iou,
                imgsz=self._config.image_size,
                verbose=False,
            )
            return results
        except Exception as e:
            raise InferenceError(f"Detection failed: {e}") from e

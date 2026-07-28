"""YOLO pose inference adapter."""

import logging
import numpy as np

from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.exceptions import PoseInferenceError

logger = logging.getLogger(__name__)


class PoseEstimator:
    """Adapter for YOLO pose inference."""
    
    def __init__(self, model, config: YoloPoseConfig):
        """Initialize estimator with model and config.
        
        Args:
            model: Loaded YOLO pose model.
            config: Pose configuration.
        """
        self._model = model
        self._config = config
    
    def estimate(self, frame: np.ndarray) -> list:
        """Run pose inference on frame.
        
        Args:
            frame: Input frame as numpy array.
            
        Returns:
            Raw pose results from YOLO model.
            
        Raises:
            PoseInferenceError: If inference fails.
        """
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
            raise PoseInferenceError(f"Pose inference failed: {e}") from e

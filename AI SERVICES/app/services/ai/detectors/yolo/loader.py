"""YOLO model loader."""

import logging
import torch
from ultralytics import YOLO

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.exceptions import (
    ModelLoadError,
    ModelNotFoundError,
    DeviceError,
)

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads and initializes YOLO model."""
    
    def __init__(self, config: YOLOConfig):
        """Initialize loader with configuration.
        
        Args:
            config: YOLO configuration.
        """
        self._config = config
        self._model = None
    
    def load(self) -> YOLO:
        """Load YOLO model.
        
        Returns:
            Loaded YOLO model.
            
        Raises:
            ModelNotFoundError: If model file not found.
            ModelLoadError: If model fails to load.
            DeviceError: If device unavailable.
        """
        try:
            device = self._get_device()
            logger.info(f"Loading YOLO model on device: {device}")
            
            self._model = YOLO(self._config.model_path)
            self._model.to(device)
            
            # Warm up model
            self._warm_up()
            
            logger.info("YOLO model loaded successfully")
            return self._model
            
        except FileNotFoundError as e:
            raise ModelNotFoundError(f"Model not found: {self._config.model_path}") from e
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {e}") from e
    
    def _get_device(self) -> str:
        """Determine device to use.
        
        Returns:
            Device string ('cuda' or 'cpu').
            
        Raises:
            DeviceError: If device unavailable.
        """
        if self._config.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        
        if self._config.device == "cuda" and not torch.cuda.is_available():
            raise DeviceError("CUDA requested but not available")
        
        return self._config.device
    
    def _warm_up(self):
        """Warm up model with dummy inference."""
        dummy_input = torch.zeros(1, 3, 640, 640)
        self._model(dummy_input)

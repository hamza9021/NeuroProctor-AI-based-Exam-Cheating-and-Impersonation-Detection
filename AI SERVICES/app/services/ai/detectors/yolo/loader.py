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
from app.services.ai.common.device_resolver import resolve_device

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
            device = resolve_device(self._config.device)
            logger.info(f"Loading YOLO model on device: {device}")
            
            self._model = YOLO(self._config.model_path)
            self._model.to(device)
            
            # Warm up model
            self._warm_up(device)
            
            logger.info("YOLO model loaded successfully")
            return self._model
            
        except FileNotFoundError as e:
            raise ModelNotFoundError(f"Model not found: {self._config.model_path}") from e
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {e}") from e
    
    def _warm_up(self, device: str):
        """Warm up model with dummy inference.
        
        Args:
            device: Device to run warm-up on.
        """
        dummy_input = torch.zeros(1, 3, 640, 640)
        if device.startswith("cuda"):
            dummy_input = dummy_input.cuda()
        self._model(dummy_input)

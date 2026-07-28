"""YOLO pose model loader."""

import logging
import torch
from ultralytics import YOLO

from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.constants import (
    EVENT_POSE_DEVICE_SELECTED,
    EVENT_POSE_INITIALIZED,
    EVENT_POSE_MODEL_LOADING,
)
from app.services.ai.analyzers.pose.exceptions import PoseInitializationError
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class PoseModelLoader:
    """Loads and initializes YOLO pose model."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize loader with configuration.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._model = None
    
    async def load(self) -> YOLO:
        """Load YOLO pose model.
        
        Returns:
            Loaded YOLO pose model.
            
        Raises:
            PoseInitializationError: If model fails to load.
        """
        try:
            device = self._get_device()
            
            await self._logger.info(
                f"Loading pose model: {self._config.model_path}",
                emit_event=EVENT_POSE_MODEL_LOADING,
                data={"model": self._config.model_path},
            )
            
            await self._logger.info(
                f"Pose inference device selected: {device}",
                emit_event=EVENT_POSE_DEVICE_SELECTED,
                data={"device": device},
            )
            
            self._model = YOLO(self._config.model_path)
            self._model.to(device)
            
            if self._config.use_half_precision:
                self._model.half()
            
            await self._logger.info(
                "YOLO pose model initialized successfully",
                emit_event=EVENT_POSE_INITIALIZED,
            )
            
            return self._model
            
        except Exception as e:
            raise PoseInitializationError(f"Failed to load pose model: {e}") from e
    
    def _get_device(self) -> str:
        """Determine device to use.
        
        Returns:
            Device string ('cuda' or 'cpu').
        """
        if self._config.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        
        if self._config.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, using CPU")
            return "cpu"
        
        return self._config.device

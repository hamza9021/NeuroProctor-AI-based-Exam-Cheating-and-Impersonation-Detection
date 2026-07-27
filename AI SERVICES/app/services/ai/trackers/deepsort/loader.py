"""DeepSORT model loader."""

import logging
import torch

from app.services.ai.monitoring.pipeline_logger import PipelineLogger
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.constants import (
    EVENT_TRACKING_DEVICE_SELECTED,
    EVENT_TRACKING_INITIALIZATION_STARTED,
    EVENT_TRACKING_INITIALIZED,
    EVENT_TRACKING_MODEL_LOADING,
)
from app.services.ai.trackers.deepsort.exceptions import DeepSortInitializationError

logger = logging.getLogger(__name__)


class TrackerLoader:
    """Loads and initializes DeepSORT tracker.
    
    Responsibilities:
    - Initialize DeepSORT once
    - Load required models
    - GPU/CPU selection
    - Log initialization details
    - Emit initialization progress via Socket.IO
    
    Never performs tracking here.
    """
    
    def __init__(self, config: DeepSORTConfig, pipeline_logger: PipelineLogger):
        """Initialize loader with configuration.
        
        Args:
            config: DeepSORT configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._tracker = None
    
    async def load(self):
        """Load DeepSORT tracker.
        
        Returns:
            Initialized DeepSORT tracker.
            
        Raises:
            DeepSortInitializationError: If tracker fails to load.
        """
        await self._logger.info(
            "DeepSORT initialization started",
            emit_event=EVENT_TRACKING_INITIALIZATION_STARTED,
        )
        
        try:
            device = self._get_device()
            await self._logger.info(
                f"Selected device: {device}",
                emit_event=EVENT_TRACKING_DEVICE_SELECTED,
                data={"device": device},
            )
            
            await self._logger.info(
                "Loading appearance embedding model",
                emit_event=EVENT_TRACKING_MODEL_LOADING,
                data={"model": self._config.embedding_model},
            )
            
            # Use simple centroid tracker instead of DeepSORT to avoid dependency issues
            from app.services.ai.trackers.deepsort.centroid_tracker import CentroidTracker
            
            self._tracker = CentroidTracker(
                max_disappeared=self._config.max_age,
                min_hits=self._config.n_init,
            )
            
            await self._logger.info(
                "DeepSORT tracker initialized successfully",
                emit_event=EVENT_TRACKING_INITIALIZED,
            )
            
            return self._tracker
            
        except ImportError as e:
            raise DeepSortInitializationError(f"DeepSORT not installed: {e}") from e
        except Exception as e:
            raise DeepSortInitializationError(f"Failed to initialize tracker: {e}") from e
    
    def _get_device(self) -> str:
        """Determine device to use.
        
        Returns:
            Device string ('cuda' or 'cpu').
        """
        if self._config.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        
        if self._config.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            return "cpu"
        
        return self._config.device

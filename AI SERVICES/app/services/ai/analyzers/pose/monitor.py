"""Monitor for pose estimation Socket.IO events."""

import logging
from typing import Dict, Any

from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class PoseMonitor:
    """Adapter for emitting pose-related Socket.IO events."""
    
    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialize monitor with pipeline logger.
        
        Args:
            pipeline_logger: Centralized pipeline logger.
        """
        self._logger = pipeline_logger
    
    async def emit_pose_initialized(self):
        """Emit pose initialization completed event."""
        await self._logger.info(
            "YOLO pose model initialized successfully",
        )
    
    async def emit_pose_warning(self, message: str, data: Dict[str, Any] = None):
        """Emit pose warning event.
        
        Args:
            message: Warning message.
            data: Optional event data.
        """
        await self._logger.warning(message, data=data)
    
    async def emit_pose_failed(self, message: str, data: Dict[str, Any] = None):
        """Emit pose failure event.
        
        Args:
            message: Failure message.
            data: Optional event data.
        """
        await self._logger.error(message, data=data)

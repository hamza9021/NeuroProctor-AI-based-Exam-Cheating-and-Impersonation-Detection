"""Monitor adapter for head pose Socket.IO logging."""

import logging

from app.services.ai.analyzers.head_pose.constants import (
    EVENT_FAILED,
    EVENT_WARNING,
)
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseMonitor:
    """Monitor adapter for head pose logging."""
    
    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialize monitor.
        
        Args:
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._logger = pipeline_logger
    
    async def emit_warning(self, message: str, data: dict = None) -> None:
        """Emit warning event.
        
        Args:
            message: Warning message.
            data: Optional event data.
        """
        await self._logger.warning(
            message,
            emit_event=EVENT_WARNING,
            data=data or {"message": message},
        )
    
    async def emit_failed(self, message: str, data: dict = None) -> None:
        """Emit failure event.
        
        Args:
            message: Failure message.
            data: Optional event data.
        """
        await self._logger.error(
            message,
            emit_event=EVENT_FAILED,
            data=data or {"message": message},
        )

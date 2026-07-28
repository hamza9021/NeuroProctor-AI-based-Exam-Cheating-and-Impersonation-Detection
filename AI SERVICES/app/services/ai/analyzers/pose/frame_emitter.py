"""Frame completion emitter for pose estimation."""

import logging
import time

from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.constants import (
    EVENT_POSE_FRAME_COMPLETED,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_DETAILED,
    LOG_LEVEL_SUMMARY,
)
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext

logger = logging.getLogger(__name__)


class FrameEmitter:
    """Emits frame completion events with configurable logging."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize emitter with configuration.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
    
    async def emit_completion(self, context: FrameContext, frame_count: int):
        """Emit frame completion event.
        
        Args:
            context: FrameContext.
            frame_count: Current frame count.
        """
        log_level = self._config.socket_log_detail_level
        frame_interval = self._config.frame_log_interval
        
        should_emit = (
            frame_count == 1
            or frame_count % frame_interval == 0
            or log_level == LOG_LEVEL_DEBUG
        )
        
        if not should_emit and log_level == LOG_LEVEL_SUMMARY:
            return
        
        start_time = time.time()
        processing_time = (time.time() - start_time) * 1000
        
        await self._logger.info(
            f"Frame {context.frame_number} pose estimation completed",
            emit_event=EVENT_POSE_FRAME_COMPLETED,
            data={
                "frame_number": context.frame_number,
                "valid_poses": len(context.poses),
                "processing_time_ms": round(processing_time, 2),
            },
        )

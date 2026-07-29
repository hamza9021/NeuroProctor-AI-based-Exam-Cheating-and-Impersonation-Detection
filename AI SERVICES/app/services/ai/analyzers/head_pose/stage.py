"""6DRepNet head pose estimation pipeline stage."""

import logging
import time

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.interfaces.pipeline_stage import PipelineStage
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_STAGE_COMPLETED,
    EVENT_STAGE_STARTED,
)
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseError
from app.services.ai.analyzers.head_pose.monitor import HeadPoseMonitor
from app.services.ai.analyzers.head_pose.service import HeadPoseService

logger = logging.getLogger(__name__)


class SixDRepNetHeadPoseStage(PipelineStage):
    """Pipeline stage for 6DRepNet head pose estimation."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize head pose stage.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = HeadPoseMonitor(pipeline_logger)
        self._service = HeadPoseService(config, pipeline_logger)
        self._initialized = False
    
    async def process(self, context: FrameContext) -> FrameContext:
        """Process frame through head pose estimation.
        
        Args:
            context: FrameContext with tracks and poses.
            
        Returns:
            Updated FrameContext with head poses and annotations.
        """
        try:
            # Initialize service on first frame
            if not self._initialized:
                await self._logger.info(
                    "6DRepNet head-pose stage started",
                    emit_event=EVENT_STAGE_STARTED,
                )
                await self._service.initialize()
                self._initialized = True
            
            # Estimate head poses
            start_time = time.time()
            context = await self._service.estimate(context)
            processing_time = (time.time() - start_time) * 1000
            
            await self._logger.info(
                "6DRepNet head-pose stage completed",
                emit_event=EVENT_STAGE_COMPLETED,
                data={
                    "frame_number": context.frame_number,
                    "head_poses_count": len(context.head_pose),
                    "processing_time_ms": round(processing_time, 2),
                },
            )
            
            return context
            
        except HeadPoseError as e:
            logger.error(f"Head pose estimation failed: {e}", exc_info=True)
            await self._monitor.emit_failed(
                f"Head pose estimation failed: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            context.head_pose = {}
            return context
        except Exception as e:
            logger.error(f"Unexpected error in head pose stage: {e}", exc_info=True)
            await self._monitor.emit_failed(
                f"Unexpected error: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            context.head_pose = {}
            return context

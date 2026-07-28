"""YOLO pose estimation pipeline stage."""

import logging
import time

from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.interfaces.pipeline_stage import PipelineStage
from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.constants import (
    EVENT_POSE_FRAME_RECEIVED,
    EVENT_POSE_STAGE_COMPLETED,
    EVENT_POSE_STAGE_STARTED,
)
from app.services.ai.analyzers.pose.exceptions import PoseError
from app.services.ai.analyzers.pose.monitor import PoseMonitor
from app.services.ai.analyzers.pose.service import YoloPoseService

logger = logging.getLogger(__name__)


class YoloPoseStage(PipelineStage):
    """Pipeline stage for YOLO pose estimation."""
    
    def __init__(self, config: YoloPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize pose stage.
        
        Args:
            config: Pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = PoseMonitor(pipeline_logger)
        self._service = YoloPoseService(config, pipeline_logger)
        self._initialized = False
    
    async def process(self, context: FrameContext) -> FrameContext:
        """Process frame through pose estimation.
        
        Args:
            context: FrameContext with tracks.
            
        Returns:
            Updated FrameContext with poses and annotations.
        """
        try:
            await self._logger.info(
                f"Pose stage received frame {context.frame_number}",
                emit_event=EVENT_POSE_FRAME_RECEIVED,
                data={"frame_number": context.frame_number},
            )
            
            # Initialize service on first frame
            if not self._initialized:
                await self._logger.info(
                    "YOLO pose stage started",
                    emit_event=EVENT_POSE_STAGE_STARTED,
                )
                await self._service.initialize()
                self._initialized = True
            
            # Estimate poses
            start_time = time.time()
            context = await self._service.estimate(context)
            processing_time = (time.time() - start_time) * 1000
            
            await self._logger.info(
                f"YOLO pose stage completed for frame {context.frame_number}",
                emit_event=EVENT_POSE_STAGE_COMPLETED,
                data={
                    "frame_number": context.frame_number,
                    "poses_count": len(context.poses),
                    "processing_time_ms": round(processing_time, 2),
                },
            )
            
            return context
            
        except PoseError as e:
            logger.error(f"Pose estimation failed: {e}", exc_info=True)
            await self._monitor.emit_pose_failed(
                f"Pose estimation failed: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            context.poses = {}
            return context
        except Exception as e:
            logger.error(f"Unexpected error in pose stage: {e}", exc_info=True)
            await self._monitor.emit_pose_failed(
                f"Unexpected error: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            context.poses = {}
            return context

"""Mapper for storing head pose results in FrameContext."""

import logging

from app.services.ai.analyzers.head_pose.constants import EVENT_RESULT_MAPPED
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext

logger = logging.getLogger(__name__)


class HeadPoseMapper:
    """Maps head pose results to FrameContext."""
    
    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialize mapper.
        
        Args:
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._logger = pipeline_logger
    
    async def map(
        self, context: FrameContext, results: list[HeadPoseResult]
    ) -> FrameContext:
        """Map head pose results to context.
        
        Args:
            context: FrameContext to update.
            results: List of head pose results.
            
        Returns:
            Updated FrameContext.
        """
        # Clear previous head pose data
        context.head_pose = {}
        
        # Map results by track ID
        for result in results:
            if result.is_valid:
                context.head_pose[result.track_id] = result
                logger.info(
                    "[HEAD-POSE MAPPER TRACE] frame=%s track_id=%d result_mapped=True result_id=%d",
                    context.frame_number, result.track_id, id(result),
                )
                await self._logger.info(
                    f"Head-pose result stored for Track #{result.track_id}",
                    emit_event=EVENT_RESULT_MAPPED,
                    data={"track_id": result.track_id},
                )
        
        logger.info(
            "[HEAD-POSE MAPPER TRACE] frame=%s total_results_mapped=%d",
            context.frame_number, len(context.head_pose),
        )
        logger.debug(f"Mapped {len(results)} head pose results to context")
        return context

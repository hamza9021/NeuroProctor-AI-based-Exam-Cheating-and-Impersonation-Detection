"""Result mapper for head pose estimation."""

from app.services.ai.analyzers.head_pose.annotator import HeadPoseAnnotator
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import EVENT_RESULT_MAPPED
from app.services.ai.analyzers.head_pose.mapper import HeadPoseMapper
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext


class ResultMapper:
    """Maps and annotates head pose results."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize result mapper.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._annotator = HeadPoseAnnotator(config, pipeline_logger)
        self._mapper = HeadPoseMapper(pipeline_logger)
    
    async def map_and_annotate(
        self, context: FrameContext, results: list
    ) -> FrameContext:
        """Map results to context and annotate frame.
        
        Args:
            context: FrameContext.
            results: Head pose results.
            
        Returns:
            Updated FrameContext.
        """
        # Map results to context
        context = await self._mapper.map(context, results)

        # Annotate frame — pass frame_number for stale-result guard
        context.frame = await self._annotator.annotate(
            context.frame, results, current_frame_index=context.frame_number
        )

        return context


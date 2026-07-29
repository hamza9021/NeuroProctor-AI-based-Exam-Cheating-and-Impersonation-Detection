"""Head pose estimation service coordinator."""

import time

from app.services.ai.analyzers.head_pose.batch_processor import BatchProcessor
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_FRAME_COMPLETED,
    EVENT_FRAME_RECEIVED,
    EVENT_STAGE_STARTED,
    EVENT_TRACKS_RECEIVED,
)
from app.services.ai.analyzers.head_pose.result_mapper import ResultMapper
from app.services.ai.analyzers.head_pose.service_initializer import ServiceInitializer
from app.services.ai.monitoring import PipelineLogger
from app.services.ai.pipeline.context import FrameContext


class HeadPoseService:
    """Coordinates head pose estimation workflow."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        self._config = config
        self._logger = pipeline_logger
        self._initializer = ServiceInitializer(config, pipeline_logger)
        self._result_mapper = ResultMapper(config, pipeline_logger)
        self._track_processor = None
        self._track_selector = None
        self._batch_processor = None
        self._model = None
        self._initialized = False
    
    async def initialize(self) -> None:
        self._model, estimator, self._track_processor = await self._initializer.initialize_components()
        components = self._initializer.get_components()
        self._track_selector = components["track_selector"]
        self._batch_processor = BatchProcessor(components["monitor"])
        self._initialized = True
    
    async def estimate(self, context: FrameContext) -> FrameContext:
        await self._logger.info(
            f"Head-pose stage received frame {context.frame_number}",
            emit_event=EVENT_FRAME_RECEIVED,
            data={"frame_number": context.frame_number},
        )
        
        if not self._initialized:
            await self._logger.info(
                "6DRepNet head-pose stage started",
                emit_event=EVENT_STAGE_STARTED,
            )
            await self.initialize()
        
        eligible_tracks = self._track_selector.select(context)
        
        await self._logger.info(
            f"Eligible tracks for head-pose estimation: {len(eligible_tracks)}",
            emit_event=EVENT_TRACKS_RECEIVED,
            data={"eligible_tracks": len(eligible_tracks)},
        )
        
        if not eligible_tracks:
            context.head_pose = {}
            return context
        
        start_time = time.time()
        results = await self._batch_processor.process(context, eligible_tracks, self._track_processor)
        context = await self._result_mapper.map_and_annotate(context, results)
        processing_time = (time.time() - start_time) * 1000
        
        await self._logger.info(
            f"Frame {context.frame_number} head-pose estimation completed",
            emit_event=EVENT_FRAME_COMPLETED,
            data={
                "frame_number": context.frame_number,
                "eligible_tracks": len(eligible_tracks),
                "valid_results": len(results),
                "processing_time_ms": round(processing_time, 2),
            },
        )
        
        return context

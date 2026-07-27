"""DeepSORT tracking pipeline stage."""

import logging
import time

from app.services.ai.monitoring.pipeline_logger import PipelineLogger
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.interfaces.pipeline_stage import PipelineStage
from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.constants import (
    EVENT_TRACKING_FRAME_RECEIVED,
    EVENT_TRACKING_STAGE_COMPLETED,
    EVENT_TRACKING_STAGE_STARTED,
)
from app.services.ai.trackers.deepsort.exceptions import DeepSortTrackingError
from app.services.ai.trackers.deepsort.monitor import TrackingMonitor
from app.services.ai.trackers.deepsort.service import DeepSORTService

logger = logging.getLogger(__name__)


class DeepSORTStage(PipelineStage):
    """Pipeline stage for DeepSORT tracking.
    
    Implements the existing PipelineStage interface.
    
    Responsibilities:
    - Receive FrameContext
    - Emit stage-start monitoring events
    - Call the tracking service
    - Emit detailed results and timing
    - Return the updated FrameContext
    - Handle recoverable tracking errors without terminating pipeline
    """
    
    def __init__(self, config: DeepSORTConfig, pipeline_logger: PipelineLogger):
        """Initialize DeepSORT stage.
        
        Args:
            config: DeepSORT configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._monitor = TrackingMonitor(pipeline_logger)
        self._service = DeepSORTService(config, pipeline_logger)
        self._initialized = False
    
    async def process(self, context: FrameContext) -> FrameContext:
        """Process frame through DeepSORT tracking.
        
        Args:
            context: FrameContext with detections.
            
        Returns:
            Updated FrameContext with tracks and annotations.
        """
        try:
            await self._logger.info(
                f"Tracking received frame {context.frame_number}",
                emit_event=EVENT_TRACKING_FRAME_RECEIVED,
                data={"frame_number": context.frame_number},
            )
            
            # Initialize service on first frame
            if not self._initialized:
                await self._logger.info(
                    "DeepSORT tracking stage started",
                    emit_event=EVENT_TRACKING_STAGE_STARTED,
                )
                await self._service.initialize()
                self._initialized = True
            
            # Track frame
            start_time = time.time()
            context = await self._service.track(context)
            processing_time = (time.time() - start_time) * 1000
            
            await self._logger.info(
                f"DeepSORT tracking stage completed for frame {context.frame_number}",
                emit_event=EVENT_TRACKING_STAGE_COMPLETED,
                data={
                    "frame_number": context.frame_number,
                    "tracks_count": len(context.tracks),
                    "processing_time_ms": round(processing_time, 2),
                },
            )
            
            return context
            
        except DeepSortTrackingError as e:
            logger.error(f"DeepSORT tracking failed: {e}", exc_info=True)
            await self._monitor.emit_tracking_failed(
                f"DeepSORT tracking failed: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            # Return context without tracking to preserve pipeline
            return context
        except Exception as e:
            logger.error(f"Unexpected error in DeepSORT stage: {e}", exc_info=True)
            await self._monitor.emit_tracking_failed(
                f"Unexpected error: {str(e)}",
                data={"frame_number": context.frame_number},
            )
            # Return context without tracking to preserve pipeline
            return context

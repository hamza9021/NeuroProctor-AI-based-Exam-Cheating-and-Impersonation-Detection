"""YOLO detection pipeline stage."""

import logging

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.service import YOLODetectionService
from app.services.ai.pipeline.interfaces.pipeline_stage import PipelineStage
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.monitoring import EventEmitter, PipelineLogger

logger = logging.getLogger(__name__)


class YOLODetectionStage(PipelineStage):
    """YOLO object detection pipeline stage."""
    
    def __init__(self, config: YOLOConfig, pipeline_logger: PipelineLogger):
        """Initialize YOLO detection stage.
        
        Args:
            config: YOLO configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._service = YOLODetectionService(config)
        self._event_emitter = EventEmitter(pipeline_logger)
        self._initialized = False
    
    async def process(self, context: FrameContext) -> FrameContext:
        """Process frame through YOLO detection.
        
        Args:
            context: Frame context to process.
            
        Returns:
            Updated frame context with detections.
        """
        try:
            # Initialize on first use
            if not self._initialized:
                await self._event_emitter.emit_info("Initializing YOLO detection")
                self._service.initialize()
                self._initialized = True
                await self._event_emitter.emit_info("YOLO detection initialized")
            
            # Emit frame processing start
            await self._event_emitter.emit_info(
                f"Processing frame {context.frame_number}",
                data={"frame_number": context.frame_number}
            )
            
            # Run detection
            context = self._service.detect(context)
            
            # Emit detection results
            await self._event_emitter.emit_info(
                f"Frame {context.frame_number} processed",
                data={
                    "frame_number": context.frame_number,
                    "detections_count": len(context.detections)
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}", exc_info=True)
            await self._event_emitter.emit_error(f"YOLO detection failed: {str(e)}")
            raise

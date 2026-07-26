"""Offline pipeline implementation for video processing."""

import logging

from app.services.ai.pipeline.base import BasePipeline
from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.manager import PipelineManager

logger = logging.getLogger(__name__)


class OfflinePipeline(BasePipeline):
    """Offline pipeline for processing pre-recorded videos.
    
    This pipeline processes frames sequentially through registered stages.
    It is designed for batch processing of video files.
    """
    
    def __init__(self) -> None:
        """Initialize the offline pipeline with a pipeline manager."""
        self._manager = PipelineManager()
        logger.info("OfflinePipeline created")
    
    def initialize(self) -> None:
        """Initialize the pipeline and its resources."""
        logger.info("OfflinePipeline initialized")
    
    def process_frame(self, context: FrameContext) -> FrameContext:
        """Process a single frame through the pipeline.
        
        Args:
            context: The frame context to process.
            
        Returns:
            The processed frame context.
        """
        logger.debug("Processing frame %d", context.frame_number)
        return self._manager.execute(context)
    
    def shutdown(self) -> None:
        """Shutdown the pipeline and release resources."""
        self._manager.clear()
        logger.info("OfflinePipeline shutdown")
    
    @property
    def manager(self) -> PipelineManager:
        """Get the pipeline manager.
        
        Returns:
            The pipeline manager instance.
        """
        return self._manager

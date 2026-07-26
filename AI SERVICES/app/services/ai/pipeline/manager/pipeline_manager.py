"""Pipeline manager for executing processing stages."""

import logging
from typing import List

from app.services.ai.pipeline.context import FrameContext
from app.services.ai.pipeline.interfaces import PipelineStage

logger = logging.getLogger(__name__)


class PipelineManager:
    """Manages and executes pipeline stages sequentially.
    
    This class is responsible for registering, removing, and executing
    pipeline stages in the order they were registered.
    """
    
    def __init__(self) -> None:
        """Initialize the pipeline manager with an empty stage list."""
        self._stages: List[PipelineStage] = []
        logger.debug("PipelineManager initialized")
    
    def register_stage(self, stage: PipelineStage) -> None:
        """Register a pipeline stage.
        
        Args:
            stage: The pipeline stage to register.
        """
        self._stages.append(stage)
        logger.info("Stage registered: %s", stage.__class__.__name__)
    
    def remove_stage(self, stage: PipelineStage) -> None:
        """Remove a pipeline stage.
        
        Args:
            stage: The pipeline stage to remove.
        """
        if stage in self._stages:
            self._stages.remove(stage)
            logger.info("Stage removed: %s", stage.__class__.__name__)
    
    def execute(self, context: FrameContext) -> FrameContext:
        """Execute all registered stages sequentially.
        
        Args:
            context: The frame context to process.
            
        Returns:
            The processed frame context after all stages.
        """
        current_context = context
        
        for stage in self._stages:
            current_context = stage.process(current_context)
            logger.debug(
                "Frame %d processed by %s",
                context.frame_number,
                stage.__class__.__name__,
            )
        
        logger.debug("Frame %d processed through %d stages", context.frame_number, len(self._stages))
        return current_context
    
    def clear(self) -> None:
        """Clear all registered stages."""
        self._stages.clear()
        logger.info("All stages cleared from pipeline")
    
    @property
    def stage_count(self) -> int:
        """Get the number of registered stages.
        
        Returns:
            The number of stages.
        """
        return len(self._stages)

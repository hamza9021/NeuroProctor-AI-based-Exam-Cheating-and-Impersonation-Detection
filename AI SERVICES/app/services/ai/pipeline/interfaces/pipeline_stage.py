"""Abstract base class for pipeline stages."""

from abc import ABC, abstractmethod

from app.services.ai.pipeline.context import FrameContext


class PipelineStage(ABC):
    """Abstract base class for all pipeline stages.
    
    Every AI module that processes frames must implement this interface.
    The stage receives a FrameContext and returns an updated FrameContext.
    
    Example:
        class MyStage(PipelineStage):
            def process(self, context: FrameContext) -> FrameContext:
                # Process the frame
                return context
    """
    
    @abstractmethod
    def process(self, context: FrameContext) -> FrameContext:
        """Process a frame context.
        
        Args:
            context: The frame context to process.
            
        Returns:
            The updated frame context.
        """
        pass

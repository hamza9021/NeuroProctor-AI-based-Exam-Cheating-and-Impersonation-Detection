"""Abstract base class for pipeline implementations."""

from abc import ABC, abstractmethod

from app.services.ai.pipeline.context import FrameContext


class BasePipeline(ABC):
    """Abstract base class for all pipeline implementations.
    
    Defines the interface that all pipelines must implement.
    Concrete implementations (e.g., OfflinePipeline) inherit from this.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the pipeline and its resources.
        
        Called once before processing begins.
        """
        pass
    
    @abstractmethod
    def process_frame(self, context: FrameContext) -> FrameContext:
        """Process a single frame through the pipeline.
        
        Args:
            context: The frame context to process.
            
        Returns:
            The processed frame context.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the pipeline and release resources.
        
        Called once after processing completes.
        """
        pass

"""
BasePipeline - Abstract base class for all pipeline implementations.

This module defines the interface that all pipeline implementations must follow.
It enforces the contract for processing FrameContext objects through the pipeline.

The BasePipeline follows the Dependency Inversion Principle - it depends on
abstractions (PipelineStage interface) rather than concrete implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from app.services.ai.pipeline.frame_context import FrameContext

logger = logging.getLogger(__name__)


class PipelineStage(ABC):
    """
    Abstract interface for all pipeline processing stages.

    Every AI module (detector, tracker, analyzer, etc.) must implement this
    interface to be compatible with the pipeline framework. This ensures that
    the PipelineManager can work with any stage without knowing its internals.

    The interface is intentionally minimal - stages only need to implement the
    process() method that takes a FrameContext and returns an updated FrameContext.

    Example:
        class YOLODetector(PipelineStage):
            def process(self, context: FrameContext) -> FrameContext:
                # Perform detection
                context.add_detection(detection_result)
                return context
    """

    @abstractmethod
    def process(self, context: FrameContext) -> FrameContext:
        """
        Process a frame through this pipeline stage.

        Args:
            context: The FrameContext containing frame data and previous stage outputs.

        Returns:
            The updated FrameContext with this stage's results added.

        Raises:
            ServiceException: If processing fails.
        """
        pass

    @property
    def name(self) -> str:
        """Return the name of this pipeline stage."""
        return self.__class__.__name__


class BasePipeline(ABC):
    """
    Abstract base class for all pipeline implementations.

    This class defines the contract that all pipeline types must implement.
    It provides the structure for processing FrameContext objects through
    a sequence of registered stages.

    Concrete implementations (OfflinePipeline, LivePipeline) inherit from this
    base class and implement the specific execution logic for their use case.

    The pipeline follows the Single Responsibility Principle - it only handles
    stage orchestration, not the actual AI processing logic.
    """

    def __init__(self, stages: Optional[List[PipelineStage]] = None):
        """
        Initialize the pipeline with a list of stages.

        Args:
            stages: List of PipelineStage instances to execute in order.
                    If None, pipeline starts with no stages.
        """
        self._stages: List[PipelineStage] = stages or []
        logger.info(
            "Initialized %s with %d stages",
            self.__class__.__name__,
            len(self._stages),
        )

    @abstractmethod
    def process(self, context: FrameContext) -> FrameContext:
        """
        Process a FrameContext through the pipeline.

        This method must be implemented by concrete pipeline classes to define
        how stages are executed (sequentially, in parallel, with error handling,
        etc.).

        Args:
            context: The FrameContext to process.

        Returns:
            The processed FrameContext with all stage outputs.

        Raises:
            ServiceException: If pipeline processing fails.
        """
        pass

    def add_stage(self, stage: PipelineStage) -> None:
        """
        Add a stage to the end of the pipeline.

        Args:
            stage: The PipelineStage to add.
        """
        self._stages.append(stage)
        logger.debug("Added stage '%s' to pipeline", stage.name)

    def remove_stage(self, stage_name: str) -> bool:
        """
        Remove a stage from the pipeline by name.

        Args:
            stage_name: Name of the stage to remove.

        Returns:
            True if stage was removed, False if not found.
        """
        for i, stage in enumerate(self._stages):
            if stage.name == stage_name:
                removed = self._stages.pop(i)
                logger.debug("Removed stage '%s' from pipeline", removed.name)
                return True
        logger.warning("Stage '%s' not found in pipeline", stage_name)
        return False

    def get_stages(self) -> List[PipelineStage]:
        """
        Get the list of registered stages.

        Returns:
            List of PipelineStage instances in execution order.
        """
        return self._stages.copy()

    def clear_stages(self) -> None:
        """Remove all stages from the pipeline."""
        self._stages.clear()
        logger.debug("Cleared all stages from pipeline")

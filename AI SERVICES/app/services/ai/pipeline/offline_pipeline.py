"""
OfflinePipeline - Pipeline for pre-recorded video processing.

This pipeline is designed for processing pre-recorded video files where
frames can be processed sequentially without real-time constraints. It
executes all registered stages in order for each frame.

The OfflinePipeline is ideal for batch processing, analysis of recorded
exam sessions, and generating detailed reports.
"""

import logging
from typing import List, Optional

from app.core.exceptions import ServiceException
from app.services.ai.pipeline.base_pipeline import BasePipeline, PipelineStage
from app.services.ai.pipeline.frame_context import FrameContext

logger = logging.getLogger(__name__)


class OfflinePipeline(BasePipeline):
    """
    Pipeline for processing pre-recorded video files.

    This pipeline executes all registered stages sequentially for each frame.
    It is designed for offline processing where real-time performance is not
    a constraint, allowing for thorough analysis and detailed output.

    The pipeline maintains execution order and ensures each stage receives
    the FrameContext with outputs from previous stages.

    Example:
        pipeline = OfflinePipeline(stages=[detector, tracker, analyzer])
        for frame in video_reader:
            context = FrameContext(frame=frame, frame_number=i)
            processed = pipeline.process(context)
            # Save or analyze processed context
    """

    def __init__(
        self,
        stages: Optional[List[PipelineStage]] = None,
        continue_on_error: bool = False,
    ):
        """
        Initialize the offline pipeline.

        Args:
            stages: List of PipelineStage instances to execute in order.
            continue_on_error: If True, continue processing remaining stages
                             even if one stage fails. If False, stop on error.
        """
        super().__init__(stages)
        self._continue_on_error = continue_on_error
        logger.info(
            "OfflinePipeline initialized with continue_on_error=%s",
            continue_on_error,
        )

    def process(self, context: FrameContext) -> FrameContext:
        """
        Process a FrameContext through all registered stages sequentially.

        Each stage receives the FrameContext with outputs from previous stages.
        The context is updated in-place and returned for further processing.

        Args:
            context: The FrameContext to process.

        Returns:
            The processed FrameContext with all stage outputs.

        Raises:
            ServiceException: If a stage fails and continue_on_error is False.
        """
        if not self._stages:
            logger.warning("No stages registered in pipeline, returning context as-is")
            return context

        logger.debug(
            "Processing frame %d through %d stages",
            context.frame_number,
            len(self._stages),
        )

        for stage in self._stages:
            try:
                logger.debug("Executing stage '%s' for frame %d", stage.name, context.frame_number)
                context = stage.process(context)
                context.set_stage_output(stage.name, True)
                logger.debug("Stage '%s' completed for frame %d", stage.name, context.frame_number)
            except Exception as exc:
                context.set_stage_output(stage.name, exc)
                if self._continue_on_error:
                    logger.error(
                        "Stage '%s' failed for frame %d: %s. Continuing due to continue_on_error=True",
                        stage.name,
                        context.frame_number,
                        exc,
                    )
                    continue
                else:
                    logger.error(
                        "Stage '%s' failed for frame %d: %s. Aborting pipeline.",
                        stage.name,
                        context.frame_number,
                        exc,
                    )
                    raise ServiceException(
                        f"Pipeline stage '{stage.name}' failed: {str(exc)}"
                    ) from exc

        logger.debug("Completed processing frame %d", context.frame_number)
        return context

    def process_batch(
        self,
        contexts: List[FrameContext],
    ) -> List[FrameContext]:
        """
        Process a batch of FrameContext objects.

        This is a convenience method for processing multiple frames efficiently.
        Each context is processed independently through the pipeline.

        Args:
            contexts: List of FrameContext objects to process.

        Returns:
            List of processed FrameContext objects in the same order.
        """
        logger.info("Processing batch of %d contexts", len(contexts))
        results = []
        for context in contexts:
            processed = self.process(context)
            results.append(processed)
        logger.info("Batch processing complete")
        return results

"""
LivePipeline - Pipeline for real-time video processing.

This pipeline is designed for processing live video streams where
real-time performance is critical. It executes registered stages
sequentially with optimizations for low-latency processing.

The LivePipeline is ideal for real-time monitoring during live exams,
with support for frame skipping and performance monitoring.
"""

import logging
import time
from typing import List, Optional

from app.core.exceptions import ServiceException
from app.services.ai.pipeline.base_pipeline import BasePipeline, PipelineStage
from app.services.ai.pipeline.frame_context import FrameContext

logger = logging.getLogger(__name__)


class LivePipeline(BasePipeline):
    """
    Pipeline for processing live video streams in real-time.

    This pipeline executes all registered stages sequentially for each frame,
    with optimizations for low-latency processing. It supports frame skipping
    to maintain real-time performance when processing cannot keep up with the
    input frame rate.

    The pipeline monitors processing time per frame and can skip frames if
    necessary to maintain a target frame rate.
    """

    def __init__(
        self,
        stages: Optional[List[PipelineStage]] = None,
        target_fps: Optional[float] = None,
        skip_frames: bool = False,
        continue_on_error: bool = True,
    ):
        """
        Initialize the live pipeline.

        Args:
            stages: List of PipelineStage instances to execute in order.
            target_fps: Target frames per second for processing. If None,
                       processes all frames without timing constraints.
            skip_frames: If True, skip frames to maintain target_fps.
            continue_on_error: If True, continue processing remaining stages
                             even if one stage fails.
        """
        super().__init__(stages)
        self._target_fps = target_fps
        self._skip_frames = skip_frames
        self._continue_on_error = continue_on_error
        self._frame_interval = 1.0 / target_fps if target_fps else None
        self._last_process_time = 0.0
        self._frames_processed = 0
        self._frames_skipped = 0

        logger.info(
            "LivePipeline initialized with target_fps=%s, skip_frames=%s, continue_on_error=%s",
            target_fps,
            skip_frames,
            continue_on_error,
        )

    def process(self, context: FrameContext) -> FrameContext:
        """
        Process a FrameContext through all registered stages sequentially.

        If frame skipping is enabled and processing is falling behind,
        this method may skip processing to maintain the target frame rate.

        Args:
            context: The FrameContext to process.

        Returns:
            The processed FrameContext with all stage outputs, or the original
            context if the frame was skipped.

        Raises:
            ServiceException: If a stage fails and continue_on_error is False.
        """
        if not self._stages:
            logger.warning("No stages registered in pipeline, returning context as-is")
            return context

        # Check if we should skip this frame
        if self._should_skip_frame():
            self._frames_skipped += 1
            logger.debug(
                "Skipping frame %d (total skipped: %d)",
                context.frame_number,
                self._frames_skipped,
            )
            return context

        start_time = time.perf_counter()

        logger.debug(
            "Processing frame %d through %d stages",
            context.frame_number,
            len(self._stages),
        )

        for stage in self._stages:
            try:
                logger.debug(
                    "Executing stage '%s' for frame %d",
                    stage.name,
                    context.frame_number,
                )
                context = stage.process(context)
                context.set_stage_output(stage.name, True)
                logger.debug(
                    "Stage '%s' completed for frame %d",
                    stage.name,
                    context.frame_number,
                )
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

        process_time = time.perf_counter() - start_time
        self._frames_processed += 1
        self._last_process_time = time.perf_counter()

        logger.debug(
            "Completed processing frame %d in %.3fms",
            context.frame_number,
            process_time * 1000,
        )

        return context

    def _should_skip_frame(self) -> bool:
        """
        Determine if the current frame should be skipped.

        Returns:
            True if frame should be skipped, False otherwise.
        """
        if not self._skip_frames or self._frame_interval is None:
            return False

        if self._last_process_time == 0.0:
            return False

        time_since_last = time.perf_counter() - self._last_process_time
        return time_since_last < self._frame_interval

    def get_performance_stats(self) -> dict:
        """
        Get pipeline performance statistics.

        Returns:
            Dictionary with performance metrics.
        """
        total_frames = self._frames_processed + self._frames_skipped
        skip_rate = (
            self._frames_skipped / total_frames if total_frames > 0 else 0.0
        )

        return {
            "frames_processed": self._frames_processed,
            "frames_skipped": self._frames_skipped,
            "skip_rate": skip_rate,
            "target_fps": self._target_fps,
        }

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self._frames_processed = 0
        self._frames_skipped = 0
        self._last_process_time = 0.0
        logger.debug("Performance statistics reset")

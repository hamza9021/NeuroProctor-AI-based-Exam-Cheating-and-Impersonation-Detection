"""Annotator for head pose visualization."""

import logging
from typing import Optional

import numpy as np

from app.services.ai.analyzers.head_pose.axis_drawer import AxisDrawer
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_ANNOTATION_COMPLETED,
    EVENT_ANNOTATION_STARTED,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.text_drawer import TextDrawer
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseAnnotator:
    """Annotates frame with head pose information."""

    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize annotator.

        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._axis_drawer = AxisDrawer(config)
        self._text_drawer = TextDrawer()

    async def annotate(
        self,
        frame: np.ndarray,
        results: list[HeadPoseResult],
        current_frame_index: Optional[int] = None,
    ) -> np.ndarray:
        """Annotate frame with head pose information.

        Args:
            frame: Input frame.
            results: List of head pose results.
            current_frame_index: The FrameContext.frame_number for this render
                call.  When provided and ``config.debug_reject_stale_results``
                is True, any result whose ``frame_index`` differs from this
                value is skipped with a WARNING log.

        Returns:
            Annotated frame.
        """
        if not self._config.annotation_enabled:
            return frame

        annotated = frame.copy()

        await self._logger.info(
            "Drawing head-pose annotations",
            emit_event=EVENT_ANNOTATION_STARTED,
        )

        for result in results:
            if not result.is_valid:
                continue

            # ---------------------------------------------------------------- #
            # Stale-result guard                                               #
            # ---------------------------------------------------------------- #
            if (
                self._config.debug_reject_stale_results
                and current_frame_index is not None
                and result.frame_index is not None
                and result.frame_index != current_frame_index
            ):
                logger.warning(
                    "Skipping stale head-pose result: "
                    "track_id=%s  result_frame=%s  render_frame=%s  "
                    "result_object_id=%d",
                    result.track_id,
                    result.frame_index,
                    current_frame_index,
                    id(result),
                )
                continue

            logger.debug(
                "Rendering  track_id=%s  render_frame=%s  result_frame=%s  "
                "yaw=%.2f  pitch=%.2f  roll=%.2f  result_object_id=%d",
                result.track_id,
                current_frame_index,
                result.frame_index,
                result.yaw,
                result.pitch,
                result.roll,
                id(result),
            )

            try:
                self._text_drawer.draw(annotated, result)
                if self._config.draw_axis:
                    self._axis_drawer.draw(annotated, result)
            except Exception as exc:
                logger.warning(
                    "Failed to annotate Track #%s: %s", result.track_id, exc
                )

        await self._logger.info(
            "Head-pose annotation completed",
            emit_event=EVENT_ANNOTATION_COMPLETED,
        )

        return annotated

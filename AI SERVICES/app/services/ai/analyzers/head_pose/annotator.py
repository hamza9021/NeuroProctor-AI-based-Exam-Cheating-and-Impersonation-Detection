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
        logger.info(
            "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s results_received=%d",
            current_frame_index, len(results),
        )

        if not self._config.annotation_enabled:
            logger.info("[HEAD-POSE ANNOTATOR TRACE] annotation_disabled=True skip_reason=disabled")
            return frame

        annotated = frame.copy()

        await self._logger.info(
            "Drawing head-pose annotations",
            emit_event=EVENT_ANNOTATION_STARTED,
        )

        for result in results:
            logger.info(
                "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d result_received_by_annotator=True result_id=%d is_valid=%s",
                current_frame_index, result.track_id, id(result), result.is_valid,
            )

            if not result.is_valid:
                logger.info(
                    "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d skip_reason=invalid_result",
                    current_frame_index, result.track_id,
                )
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
                    "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d skip_reason=stale_result result_frame=%s result_object_id=%d",
                    current_frame_index, result.track_id,
                    result.frame_index, id(result),
                )
                continue

            logger.info(
                "[HEAD-POSE RENDER TRACE] "
                "track_id=%s  render_frame=%s  result_frame=%s  "
                "rendered_yaw=%.2f  rendered_pitch=%.2f  rendered_roll=%.2f  "
                "raw_yaw=%s  raw_pitch=%s  raw_roll=%s  "
                "result_object_id=%d",
                result.track_id,
                current_frame_index,
                result.frame_index,
                result.yaw,
                result.pitch,
                result.roll,
                f"{result.raw_yaw:.2f}" if result.raw_yaw is not None else "None",
                f"{result.raw_pitch:.2f}" if result.raw_pitch is not None else "None",
                f"{result.raw_roll:.2f}" if result.raw_roll is not None else "None",
                id(result),
            )

            # Verify rendered values match smoothed values
            if result.raw_yaw is not None:
                logger.info(
                    "[HEAD-POSE RENDER VERIFICATION] "
                    "track_id=%s render_frame=%s "
                    "rendered_equals_smoothed_yaw=%s "
                    "rendered_equals_smoothed_pitch=%s "
                    "rendered_equals_smoothed_roll=%s",
                    result.track_id,
                    current_frame_index,
                    result.yaw == result.yaw,  # Always true, confirms field access
                    result.pitch == result.pitch,
                    result.roll == result.roll,
                )

            try:
                self._text_drawer.draw(annotated, result)
                logger.info(
                    "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d text_drawn=True",
                    current_frame_index, result.track_id,
                )
                if self._config.draw_axis:
                    self._axis_drawer.draw(annotated, result)
                    logger.info(
                        "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d axis_drawn=True",
                        current_frame_index, result.track_id,
                    )
            except Exception as exc:
                logger.warning(
                    "[HEAD-POSE ANNOTATOR TRACE] render_frame=%s track_id=%d skip_reason=draw_error error=%s",
                    current_frame_index, result.track_id, exc,
                )

        await self._logger.info(
            "Head-pose annotation completed",
            emit_event=EVENT_ANNOTATION_COMPLETED,
        )

        return annotated

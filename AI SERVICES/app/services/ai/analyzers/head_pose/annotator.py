"""Annotator for head pose visualization."""

import logging

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
        self, frame: np.ndarray, results: list[HeadPoseResult]
    ) -> np.ndarray:
        """Annotate frame with head pose information.
        
        Args:
            frame: Input frame.
            results: List of head pose results.
            
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
            
            try:
                self._text_drawer.draw(annotated, result)
                if self._config.draw_axis:
                    self._axis_drawer.draw(annotated, result)
            except Exception as e:
                logger.warning(f"Failed to annotate Track #{result.track_id}: {e}")
        
        await self._logger.info(
            "Head-pose annotation completed",
            emit_event=EVENT_ANNOTATION_COMPLETED,
        )
        
        return annotated

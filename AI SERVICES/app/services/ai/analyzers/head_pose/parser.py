"""Parser for 6DRepNet model output."""

import logging
from typing import Tuple

import numpy as np

from app.services.ai.analyzers.head_pose.constants import (
    AXIS_PITCH,
    AXIS_ROLL,
    AXIS_YAW,
    EVENT_RESULT_PARSED,
)
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseParsingError
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseParser:
    """Parses 6DRepNet output into yaw, pitch, roll."""
    
    def __init__(self, pipeline_logger: PipelineLogger):
        """Initialize parser.
        
        Args:
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._logger = pipeline_logger
    
    async def parse(
        self, raw_output: np.ndarray, track_id: int
    ) -> Tuple[float, float, float]:
        """Parse raw model output into angles.
        
        Args:
            raw_output: Raw model output tensor.
            track_id: Track ID for logging.
            
        Returns:
            Yaw, pitch, roll in degrees.
            
        Raises:
            HeadPoseParsingError: If parsing fails.
        """
        try:
            # 6DRepNet outputs: [pitch, yaw, roll] in radians
            # Convert to degrees
            angles = np.degrees(raw_output)
            
            # Extract angles (order: pitch, yaw, roll)
            pitch = float(angles[0])
            yaw = float(angles[1])
            roll = float(angles[2])
            
            await self._logger.info(
                f"Yaw: {yaw:.1f}°, Pitch: {pitch:.1f}°, Roll: {roll:.1f}°",
                emit_event=EVENT_RESULT_PARSED,
                data={
                    "track_id": track_id,
                    AXIS_YAW: yaw,
                    AXIS_PITCH: pitch,
                    AXIS_ROLL: roll,
                },
            )
            
            return yaw, pitch, roll
            
        except Exception as e:
            logger.error(f"Parsing failed for Track #{track_id}: {e}", exc_info=True)
            raise HeadPoseParsingError(f"Parsing failed: {e}")

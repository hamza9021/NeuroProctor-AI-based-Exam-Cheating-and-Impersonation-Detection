"""Validator for head pose results."""

import logging
from typing import Tuple

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import EVENT_RESULT_VALIDATED
from app.services.ai.analyzers.head_pose.exceptions import HeadPoseValidationError
from app.services.ai.analyzers.head_pose.result_validator import ResultValidator
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class HeadPoseValidator:
    """Validates head pose estimation results."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize validator.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._result_validator = ResultValidator()
    
    async def validate(
        self,
        track_id: int,
        face_bbox: Tuple[float, float, float, float],
        yaw: float,
        pitch: float,
        roll: float,
    ) -> bool:
        """Validate head pose result.
        
        Args:
            track_id: DeepSORT track ID.
            face_bbox: Face bounding box.
            yaw: Yaw angle in degrees.
            pitch: Pitch angle in degrees.
            roll: Roll angle in degrees.
            
        Returns:
            True if valid, False otherwise.
        """
        try:
            # Check for NaN or infinite values
            if not self._result_validator.is_valid_number(yaw):
                raise HeadPoseValidationError(f"Invalid yaw: {yaw}")
            if not self._result_validator.is_valid_number(pitch):
                raise HeadPoseValidationError(f"Invalid pitch: {pitch}")
            if not self._result_validator.is_valid_number(roll):
                raise HeadPoseValidationError(f"Invalid roll: {roll}")
            
            # Check angle limits
            if abs(yaw) > self._config.max_abs_angle:
                raise HeadPoseValidationError(f"Yaw exceeds limit: {yaw}")
            if abs(pitch) > self._config.max_abs_angle:
                raise HeadPoseValidationError(f"Pitch exceeds limit: {pitch}")
            if abs(roll) > self._config.max_abs_angle:
                raise HeadPoseValidationError(f"Roll exceeds limit: {roll}")
            
            # Check track ID
            if track_id < 0:
                raise HeadPoseValidationError(f"Invalid track ID: {track_id}")
            
            # Check face bbox
            if not self._result_validator.is_valid_bbox(face_bbox):
                raise HeadPoseValidationError(f"Invalid face bbox: {face_bbox}")
            
            await self._logger.info(
                f"Head-pose result validated for Track #{track_id}",
                emit_event=EVENT_RESULT_VALIDATED,
                data={"track_id": track_id},
            )
            
            return True
            
        except HeadPoseValidationError as e:
            logger.warning(f"Validation failed for Track #{track_id}: {e}")
            return False

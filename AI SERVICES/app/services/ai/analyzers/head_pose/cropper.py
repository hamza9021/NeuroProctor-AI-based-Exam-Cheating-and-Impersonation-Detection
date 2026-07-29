"""Crop validator and cropper for face regions."""

import logging
from typing import Tuple

import numpy as np

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import EVENT_CROP_CREATED
from app.services.ai.analyzers.head_pose.exceptions import InvalidFaceCropError
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class FaceCropper:
    """Validates and crops face regions."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize cropper.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
    
    async def crop(
        self,
        frame: np.ndarray,
        face_bbox: Tuple[float, float, float, float],
        track_id: int,
    ) -> np.ndarray:
        """Validate and crop face region.
        
        Args:
            frame: Input frame.
            face_bbox: Face bounding box (x1, y1, x2, y2).
            track_id: Track ID for logging.
            
        Returns:
            Cropped face image.
            
        Raises:
            InvalidFaceCropError: If crop is invalid.
        """
        # Validate and clip bbox
        x1, y1, x2, y2 = self._validate_bbox(face_bbox, frame.shape)
        
        # Extract crop
        crop = frame[int(y1) : int(y2), int(x1) : int(x2)]
        
        # Validate crop
        if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
            raise InvalidFaceCropError(f"Empty crop for Track #{track_id}")
        
        await self._logger.info(
            f"Face crop created for Track #{track_id}",
            emit_event=EVENT_CROP_CREATED,
            data={"track_id": track_id, "crop_shape": crop.shape},
        )
        
        return crop
    
    def _validate_bbox(
        self, bbox: Tuple[float, float, float, float], frame_shape: Tuple[int, int, int]
    ) -> Tuple[float, float, float, float]:
        """Validate and clip bounding box.
        
        Args:
            bbox: Input bounding box.
            frame_shape: Frame shape (height, width, channels).
            
        Returns:
            Clipped bounding box.
            
        Raises:
            InvalidFaceCropError: If bbox is invalid.
        """
        x1, y1, x2, y2 = bbox
        height, width = frame_shape[:2]
        
        # Check for invalid coordinates
        if x2 <= x1 or y2 <= y1:
            raise InvalidFaceCropError(f"Invalid bbox: {bbox}")
        
        # Clip to frame boundaries
        x1 = max(0, min(x1, width))
        y1 = max(0, min(y1, height))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))
        
        # Check minimum size
        crop_width = x2 - x1
        crop_height = y2 - y1
        
        if crop_width < self._config.min_face_size:
            raise InvalidFaceCropError(f"Crop too small: {crop_width}px")
        
        if crop_height < self._config.min_face_size:
            raise InvalidFaceCropError(f"Crop too small: {crop_height}px")
        
        return (x1, y1, x2, y2)

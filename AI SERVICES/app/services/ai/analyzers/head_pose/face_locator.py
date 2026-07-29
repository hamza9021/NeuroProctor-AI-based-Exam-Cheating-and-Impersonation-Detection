"""Locates face/head region for head pose estimation."""

import logging
from typing import Optional, Tuple

from app.services.ai.analyzers.head_pose.bbox_locator import BboxLocator
from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import (
    EVENT_FACE_LOCATION_STARTED,
    EVENT_FACE_REGION_FOUND,
    EVENT_FACE_REGION_MISSING,
)
from app.services.ai.analyzers.head_pose.exceptions import FaceRegionNotFoundError
from app.services.ai.analyzers.head_pose.keypoint_locator import KeypointLocator
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class FaceLocator:
    """Locates face/head region from pose keypoints or track bbox."""
    
    def __init__(self, config: HeadPoseConfig, pipeline_logger: PipelineLogger):
        """Initialize locator.
        
        Args:
            config: Head pose configuration.
            pipeline_logger: Pipeline logger for Socket.IO events.
        """
        self._config = config
        self._logger = pipeline_logger
        self._keypoint_locator = KeypointLocator(config)
        self._bbox_locator = BboxLocator(config)
    
    async def locate(
        self,
        track_id: int,
        track_bbox: Tuple[float, float, float, float],
        pose_data: Optional[dict],
        frame_shape: Tuple[int, int],
    ) -> Tuple[float, float, float, float]:
        """Locate face/head region for a track.
        
        Args:
            track_id: DeepSORT track ID.
            track_bbox: Track bounding box (x1, y1, x2, y2).
            pose_data: Pose data with keypoints.
            frame_shape: Frame shape (height, width).
            
        Returns:
            Face bounding box (x1, y1, x2, y2).
            
        Raises:
            FaceRegionNotFoundError: If no valid region found.
        """
        await self._logger.info(
            f"Locating head region for Track #{track_id}",
            emit_event=EVENT_FACE_LOCATION_STARTED,
            data={"track_id": track_id},
        )
        
        # Try pose keypoints first
        if pose_data and "keypoints" in pose_data:
            face_bbox = self._keypoint_locator.locate(
                pose_data["keypoints"], frame_shape
            )
            if face_bbox:
                await self._logger.info(
                    f"Head region found using pose facial keypoints for Track #{track_id}",
                    emit_event=EVENT_FACE_REGION_FOUND,
                    data={"track_id": track_id, "method": "keypoints"},
                )
                return face_bbox
        
        # Fallback to upper portion of track bbox
        face_bbox = self._bbox_locator.locate(track_bbox)
        if face_bbox:
            await self._logger.info(
                f"Head region found using track bbox for Track #{track_id}",
                emit_event=EVENT_FACE_REGION_FOUND,
                data={"track_id": track_id, "method": "track_bbox"},
            )
            return face_bbox
        
        raise FaceRegionNotFoundError(f"No valid head region for Track #{track_id}")

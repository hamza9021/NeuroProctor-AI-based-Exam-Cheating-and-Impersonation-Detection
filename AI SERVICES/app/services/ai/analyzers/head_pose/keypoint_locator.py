"""Keypoint-based face region locator."""

from typing import Optional, Tuple

import numpy as np

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig


class KeypointLocator:
    """Locates face region from pose keypoints."""
    
    def __init__(self, config: HeadPoseConfig):
        """Initialize keypoint locator.
        
        Args:
            config: Head pose configuration.
        """
        self._config = config
    
    def locate(
        self, keypoints: np.ndarray, frame_shape: Tuple[int, int]
    ) -> Optional[Tuple[float, float, float, float]]:
        """Locate face from pose keypoints.
        
        Args:
            keypoints: Keypoint array (17, 3).
            frame_shape: Frame shape (height, width).
            
        Returns:
            Face bbox or None.
        """
        # Facial keypoints: nose(0), eyes(1,2), ears(3,4)
        facial_indices = [0, 1, 2, 3, 4]
        facial_points = keypoints[facial_indices]
        
        # Filter by confidence
        valid_points = facial_points[facial_points[:, 2] > 0.5]
        if len(valid_points) < 2:
            return None
        
        # Get bounding box
        x_coords = valid_points[:, 0]
        y_coords = valid_points[:, 1]
        
        x1, y1 = x_coords.min(), y_coords.min()
        x2, y2 = x_coords.max(), y_coords.max()
        
        # Add padding
        padding = self._config.face_padding
        width = x2 - x1
        height = y2 - y1
        
        x1 = max(0, x1 - width * padding)
        y1 = max(0, y1 - height * padding)
        x2 = min(frame_shape[1], x2 + width * padding)
        y2 = min(frame_shape[0], y2 + height * padding)
        
        return (x1, y1, x2, y2)

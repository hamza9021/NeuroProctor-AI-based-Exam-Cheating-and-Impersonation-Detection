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

        # Get bounding box of valid keypoints
        x_coords = valid_points[:, 0]
        y_coords = valid_points[:, 1]

        x1, y1 = x_coords.min(), y_coords.min()
        x2, y2 = x_coords.max(), y_coords.max()

        # Calculate centre and dimensions of keypoint box
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        keypoint_width = x2 - x1
        keypoint_height = y2 - y1

        # Calculate stable square head size
        side = max(
            keypoint_width,
            keypoint_height,
            self._config.minimum_head_size,
        )
        side *= self._config.head_padding_scale

        # Create square crop with vertical offset
        # vertical_center_ratio=0.4 means the centre is at 40% from top,
        # leaving more space above for hair/forehead
        square_x1 = center_x - side / 2.0
        square_y1 = center_y - side * self._config.vertical_center_ratio
        square_x2 = square_x1 + side
        square_y2 = square_y1 + side

        # Clamp to frame boundaries
        frame_h, frame_w = frame_shape
        square_x1 = max(0.0, square_x1)
        square_y1 = max(0.0, square_y1)
        square_x2 = min(float(frame_w), square_x2)
        square_y2 = min(float(frame_h), square_y2)

        return (square_x1, square_y1, square_x2, square_y2)

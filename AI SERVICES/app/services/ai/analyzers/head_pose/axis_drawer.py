"""Orientation axis drawer for head pose visualization."""

import numpy as np
import cv2

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult


class AxisDrawer:
    """Draws 3D orientation axis for head pose."""
    
    def __init__(self, config: HeadPoseConfig):
        """Initialize axis drawer.
        
        Args:
            config: Head pose configuration.
        """
        self._config = config
    
    def draw(self, frame: np.ndarray, result: HeadPoseResult) -> None:
        """Draw 3D orientation axis.
        
        Args:
            frame: Input frame.
            result: Head pose result.
        """
        x1, y1, x2, y2 = result.face_bbox
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        
        # Convert angles to radians
        yaw_rad = np.radians(result.yaw)
        pitch_rad = np.radians(result.pitch)
        roll_rad = np.radians(result.roll)
        
        # Calculate axis endpoints
        length = self._config.axis_length
        
        # X-axis (red) - points right
        x_end = center_x + int(length * np.cos(yaw_rad))
        y_end = center_y + int(length * np.sin(yaw_rad))
        cv2.line(frame, (center_x, center_y), (x_end, y_end), (0, 0, 255), 2)
        
        # Y-axis (green) - points down
        y_end = center_y + int(length * np.sin(pitch_rad))
        cv2.line(frame, (center_x, center_y), (center_x, y_end), (0, 255, 0), 2)
        
        # Z-axis (blue) - points forward (roll)
        z_end_x = center_x + int(length * np.sin(roll_rad))
        z_end_y = center_y - int(length * np.cos(roll_rad))
        cv2.line(frame, (center_x, center_y), (z_end_x, z_end_y), (255, 0, 0), 2)

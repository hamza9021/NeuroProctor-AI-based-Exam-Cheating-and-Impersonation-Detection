"""Orientation axis drawer for head pose visualization."""

import numpy as np
import cv2

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult


class AxisDrawer:
    """Draws 3D orientation axis for head pose.

    The axis origin is taken from ``HeadPoseResult.axis_origin`` (nose
    keypoint or face-bbox centre, pre-clamped to frame boundaries).
    """

    def __init__(self, config: HeadPoseConfig):
        """Initialize axis drawer.

        Args:
            config: Head pose configuration.
        """
        self._config = config

    def draw(self, frame: np.ndarray, result: HeadPoseResult) -> None:
        """Draw 3D orientation axis.

        Args:
            frame: BGR frame to draw on (modified in-place).
            result: Head pose result containing angles and the pre-clamped
                axis origin.
        """
        # ------------------------------------------------------------------ #
        # Determine draw origin: use stored axis_origin if available           #
        # ------------------------------------------------------------------ #
        if result.axis_origin is not None:
            center_x, center_y = result.axis_origin
        else:
            # Legacy fallback: face-bbox centre
            x1, y1, x2, y2 = result.face_bbox
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

        # ------------------------------------------------------------------ #
        # Convert angles to radians                                            #
        # ------------------------------------------------------------------ #
        yaw_rad = np.radians(result.yaw)
        pitch_rad = np.radians(result.pitch)
        roll_rad = np.radians(result.roll)

        length = self._config.axis_length

        # X-axis (red) — points right with yaw
        x_end = center_x + int(length * np.cos(yaw_rad))
        y_end = center_y + int(length * np.sin(yaw_rad))
        cv2.line(frame, (center_x, center_y), (x_end, y_end), (0, 0, 255), 2)

        # Y-axis (green) — points down with pitch
        y_end = center_y + int(length * np.sin(pitch_rad))
        cv2.line(frame, (center_x, center_y), (center_x, y_end), (0, 255, 0), 2)

        # Z-axis (blue) — forward vector (roll)
        z_end_x = center_x + int(length * np.sin(roll_rad))
        z_end_y = center_y - int(length * np.cos(roll_rad))
        cv2.line(frame, (center_x, center_y), (z_end_x, z_end_y), (255, 0, 0), 2)


"""Text drawer for head pose annotations."""

import cv2

from app.services.ai.analyzers.head_pose.constants import (
    LABEL_PITCH,
    LABEL_ROLL,
    LABEL_YAW,
)
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult


class TextDrawer:
    """Draws text labels for head pose results."""
    
    def draw(self, frame, result: HeadPoseResult) -> None:
        """Draw head pose text on frame.
        
        Args:
            frame: Input frame.
            result: Head pose result.
        """
        x1, y1, x2, y2 = [int(coord) for coord in result.face_bbox]
        
        # Draw text label
        label = f"ID: {result.track_id}"
        label += f"\n{LABEL_YAW}: {result.yaw:.1f}°"
        label += f"\n{LABEL_PITCH}: {result.pitch:.1f}°"
        label += f"\n{LABEL_ROLL}: {result.roll:.1f}°"
        
        # Draw text
        y_offset = y1 - 10
        for line in label.split("\n"):
            cv2.putText(
                frame,
                line,
                (x1, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
            y_offset -= 20

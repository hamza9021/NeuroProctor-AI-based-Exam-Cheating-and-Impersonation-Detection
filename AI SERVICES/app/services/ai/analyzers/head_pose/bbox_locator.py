"""Bounding box-based face region locator."""

from typing import Optional, Tuple

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig


class BboxLocator:
    """Locates face region from track bounding box."""
    
    def __init__(self, config: HeadPoseConfig):
        """Initialize bbox locator.
        
        Args:
            config: Head pose configuration.
        """
        self._config = config
    
    def locate(
        self, track_bbox: Tuple[float, float, float, float]
    ) -> Optional[Tuple[float, float, float, float]]:
        """Locate face from track bounding box.

        Uses a centred upper-person crop as fallback when facial keypoints
        are not available. Does not use the complete person width.

        Args:
            track_bbox: Track bounding box (x1, y1, x2, y2).

        Returns:
            Face bbox or None.
        """
        x1, y1, x2, y2 = track_bbox
        width = x2 - x1
        height = y2 - y1

        # Use upper 30% of track bbox for head region
        head_height = height * 0.30
        head_y2 = y1 + head_height

        # Use centred upper-person crop (exclude 20% from each side)
        # This prevents using nearly the whole person width
        head_x1 = x1 + 0.20 * width
        head_x2 = x2 - 0.20 * width

        face_bbox = (head_x1, y1, head_x2, head_y2)

        # Check minimum size
        face_width = head_x2 - head_x1
        face_height = head_y2 - y1
        if face_width < self._config.min_face_size or face_height < self._config.min_face_size:
            return None

        return face_bbox

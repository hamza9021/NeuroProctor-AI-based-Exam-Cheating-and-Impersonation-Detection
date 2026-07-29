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
        
        Args:
            track_bbox: Track bounding box (x1, y1, x2, y2).
            
        Returns:
            Face bbox or None.
        """
        x1, y1, x2, y2 = track_bbox
        width = x2 - x1
        height = y2 - y1
        
        # Use upper 40% of track bbox for head region
        head_height = height * 0.4
        head_y2 = y1 + head_height
        
        # Add horizontal padding
        padding = self._config.face_padding
        head_x1 = max(0, x1 - width * padding)
        head_x2 = x2 + width * padding
        
        face_bbox = (head_x1, y1, head_x2, head_y2)
        
        # Check minimum size
        face_width = head_x2 - head_x1
        if face_width < self._config.min_face_size:
            return None
        
        return face_bbox

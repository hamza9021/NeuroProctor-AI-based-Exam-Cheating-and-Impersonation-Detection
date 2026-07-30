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

        # Calculate centre and create square crop for stable inference
        center_x = (head_x1 + head_x2) / 2.0
        center_y = (y1 + head_y2) / 2.0

        keypoint_width = head_x2 - head_x1
        keypoint_height = head_y2 - y1

        # Calculate stable square head size
        # For fallback, use a more conservative size based on person height
        # to avoid oversized crops from wide person bboxes
        head_size_estimate = height * 0.20  # Head is typically 20% of person height
        side = max(
            head_size_estimate,
            80.0,  # minimum_head_size
        )
        # Use smaller padding for fallback to avoid oversized crops
        side *= 1.3  # head_padding_scale for fallback

        # Create square crop with vertical offset
        square_x1 = center_x - side / 2.0
        square_y1 = center_y - side * 0.4  # vertical_center_ratio
        square_x2 = square_x1 + side
        square_y2 = square_y1 + side

        # Clamp to frame boundaries before returning
        # Use person bbox extent as frame boundary estimate for fallback
        frame_h, frame_w = y2, x2
        square_x1 = max(0.0, square_x1)
        square_y1 = max(0.0, square_y1)
        square_x2 = min(float(frame_w), square_x2)
        square_y2 = min(float(frame_h), square_y2)

        face_bbox = (square_x1, square_y1, square_x2, square_y2)

        # Check minimum size
        face_width = square_x2 - square_x1
        face_height = square_y2 - square_y1
        if face_width < self._config.min_face_size or face_height < self._config.min_face_size:
            return None

        return face_bbox

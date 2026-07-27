"""Annotator for DeepSORT tracking visualization."""

import cv2
import logging
from typing import List

import numpy as np

from app.services.ai.trackers.deepsort.constants import (
    MAX_TIME_SINCE_UPDATE,
    MIN_HITS_TO_CONFIRM,
)
from app.services.ai.trackers.deepsort.exceptions import TrackingAnnotationError
from app.services.ai.trackers.deepsort.track import Track

logger = logging.getLogger(__name__)


class TrackAnnotator:
    """Draws tracking visualization on processed frames.
    
    For every confirmed tracked person, displays:
    - Bounding box
    - Persistent Track ID
    - Optional confidence
    
    Requirements:
    - Keep labels readable
    - Clip boxes to frame boundaries
    - Do not draw invalid or stale tracks
    - Preserve same visual identity for same Track ID
    """
    
    def __init__(self):
        """Initialize annotator with color map."""
        self._color_map = self._generate_color_map()
    
    def annotate(self, frame: np.ndarray, tracks: List[Track]) -> np.ndarray:
        """Draw tracking annotations on frame.
        
        Args:
            frame: Input frame.
            tracks: List of Track objects.
            
        Returns:
            Annotated frame.
            
        Raises:
            TrackingAnnotationError: If annotation fails.
        """
        try:
            annotated = frame.copy()
            frame_height, frame_width = frame.shape[:2]
            
            for track in tracks:
                if not self._should_draw_track(track):
                    continue
                
                self._draw_track(annotated, track, frame_width, frame_height)
            
            return annotated
            
        except Exception as e:
            raise TrackingAnnotationError(f"Annotation failed: {e}") from e
    
    def _should_draw_track(self, track: Track) -> bool:
        """Check if track should be drawn.
        
        Args:
            track: Track to check.
            
        Returns:
            True if track should be drawn, False otherwise.
        """
        # Don't draw lost tracks
        if track.time_since_update > MAX_TIME_SINCE_UPDATE:
            return False
        
        # Only draw confirmed tracks or tracks with enough hits
        if not track.is_confirmed and track.hits < MIN_HITS_TO_CONFIRM:
            return False
        
        return True
    
    def _draw_track(
        self,
        frame: np.ndarray,
        track: Track,
        frame_width: int,
        frame_height: int,
    ):
        """Draw track bounding box and label.
        
        Args:
            frame: Frame to draw on.
            track: Track to draw.
            frame_width: Frame width for clipping.
            frame_height: Frame height for clipping.
        """
        x1, y1, x2, y2 = track.bbox
        
        # Clip to frame boundaries
        x1 = max(0, min(x1, frame_width - 1))
        y1 = max(0, min(y1, frame_height - 1))
        x2 = max(0, min(x2, frame_width - 1))
        y2 = max(0, min(y2, frame_height - 1))
        
        # Get color for this track ID
        color = self._get_track_color(track.track_id)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = self._create_label(track)
        self._draw_label(frame, label, (x1, y1), color)
    
    def _create_label(self, track: Track) -> str:
        """Create label text for track.
        
        Args:
            track: Track to create label for.
            
        Returns:
            Label string.
        """
        if track.is_confirmed:
            return f"Person #{track.track_id}"
        return f"#{track.track_id}"
    
    def _draw_label(
        self,
        frame: np.ndarray,
        label: str,
        position: tuple,
        color: tuple,
    ):
        """Draw label on frame.
        
        Args:
            frame: Frame to draw on.
            label: Label text.
            position: Position (x, y).
            color: Color tuple.
        """
        x, y = position
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x, y - text_height - baseline - 5),
            (x + text_width + 10, y),
            color,
            -1,
        )
        
        # Draw text
        cv2.putText(
            frame,
            label,
            (x + 5, y - baseline - 2),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )
    
    def _get_track_color(self, track_id: int) -> tuple:
        """Get color for track ID.
        
        Args:
            track_id: Track ID.
            
        Returns:
            RGB color tuple.
        """
        if not self._color_map:
            return (0, 255, 0)
        
        index = int(track_id) % len(self._color_map)
        return self._color_map[index]
    
    def _generate_color_map(self) -> List[tuple]:
        """Generate color map for track IDs.
        
        Returns:
            List of RGB color tuples.
        """
        colors = [
            (0, 255, 0),      # Green
            (255, 0, 0),      # Red
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (128, 0, 128),    # Purple
            (255, 165, 0),    # Orange
            (0, 128, 128),    # Teal
            (128, 128, 0),    # Olive
        ]
        return colors

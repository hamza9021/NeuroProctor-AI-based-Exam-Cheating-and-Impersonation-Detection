"""
Tracking Processor module.

This module provides a processor that integrates ByteTrack multi-object tracking
with the video processing pipeline.
"""

import numpy as np
import cv2
from typing import Optional, List, Tuple

from app.processors.base_processor import BaseProcessor
from app.tracking.tracker import MultiObjectTracker
from app.tracking.tracking_models import FrameTracks, Track, TrackState
from app.detectors.detection import FrameDetections
from app.config.settings import settings
from app.utils.logger import get_logger


class TrackingProcessor(BaseProcessor):
    """Processor for ByteTrack multi-object tracking in video frames."""

    def __init__(
        self,
        track_thresh: Optional[float] = None,
        track_buffer: Optional[int] = None,
        match_thresh: Optional[float] = None,
        frame_rate: Optional[int] = None,
    ):
        """
        Initialize tracking processor.

        Args:
            track_thresh: Detection confidence threshold for tracking
            track_buffer: Buffer size for track management
            match_thresh: IoU threshold for track matching
            frame_rate: Video frame rate for time calculations
        """
        super().__init__("TrackingProcessor")
        
        self.logger = get_logger(__name__)
        
        self.tracker = MultiObjectTracker(
            track_thresh=track_thresh,
            track_buffer=track_buffer,
            match_thresh=match_thresh,
            frame_rate=frame_rate,
        )
        
        self.current_frame_number: int = 0
        self.current_timestamp: float = 0.0
        self.last_frame_tracks: Optional[FrameTracks] = None
        self.last_detections: Optional[FrameDetections] = None
        
        # Visualization settings
        self.track_id_color = (0, 255, 255)  # Yellow (BGR)
        self.track_id_font = cv2.FONT_HERSHEY_SIMPLEX
        self.track_id_font_scale = 0.6
        self.track_id_thickness = 2
        self.track_id_bg_color = (0, 0, 0)  # Black background for text
        
        # Track state colors
        self.state_colors = {
            TrackState.NEW: (0, 255, 0),  # Green
            TrackState.ACTIVE: (0, 255, 255),  # Yellow
            TrackState.TEMPORARILY_LOST: (0, 165, 255),  # Orange
            TrackState.REMOVED: (0, 0, 255),  # Red
        }
    
    def initialize(self) -> None:
        """Initialize the tracker."""
        self.tracker.initialize()
        self.logger.info("TrackingProcessor initialized")
    
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame with tracking.

        Args:
            frame: Input frame

        Returns:
            Frame with tracking visualization
        """
        # Store original frame for DeepSORT embeddings
        original_frame = frame.copy()
        
        # Get detections from previous processor
        if self.last_detections is None:
            self.logger.warning("No detections available for tracking")
            return frame
        
        # Process frame with tracker using original frame for embeddings
        try:
            self.logger.debug(f"TrackingProcessor process: original_frame type={type(original_frame)}, original_frame is None={original_frame is None}")
            frame_tracks = self.tracker.process_frame(self.last_detections, frame=original_frame)
            self.last_frame_tracks = frame_tracks
        except Exception as e:
            self.logger.error(f"Error in tracking: {e}")
            return frame
        
        # Draw tracks on frame (use the input frame which may have previous annotations)
        annotated_frame = self._draw_tracks(frame, frame_tracks)
        
        # Log summary
        active_tracks = frame_tracks.get_active_tracks()
        if active_tracks and self.current_frame_number % 30 == 0:
            class_counts = frame_tracks.get_class_counts()
            self.logger.info(
                f"Frame {self.current_frame_number}: "
                f"Active Tracks: {len(active_tracks)}, "
                f"Classes: {class_counts}, "
                f"Processing Time: {frame_tracks.processing_time_ms:.2f}ms"
            )
        
        return annotated_frame
    
    def _draw_tracks(self, frame: np.ndarray, frame_tracks: FrameTracks) -> np.ndarray:
        """
        Draw track IDs and information on frame.

        Args:
            frame: Input frame
            frame_tracks: FrameTracks object with tracks

        Returns:
            Frame with track visualization
        """
        annotated_frame = frame.copy()
        
        for track in frame_tracks.tracks:
            if not track.is_active():
                continue
            
            track_id = track.track_id
            class_name = track.class_name
            confidence = track.confidence
            x1, y1, x2, y2 = track.bounding_box
            
            # Get color based on track state
            color = self.state_colors.get(track.state, self.track_id_color)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Create label text
            label = f"ID: {track_id}"
            label_class = f"{class_name}"
            label_conf = f"{confidence:.0%}"
            
            # Calculate label position
            label_y = y1 - 10 if y1 > 30 else y1 + 20
            
            # Draw track ID
            (text_width, text_height), baseline = cv2.getTextSize(
                label, self.track_id_font, self.track_id_font_scale, self.track_id_thickness
            )
            
            # Draw background for track ID
            cv2.rectangle(
                annotated_frame,
                (x1, label_y - text_height - baseline - 5),
                (x1 + text_width + 10, label_y + baseline + 5),
                self.track_id_bg_color,
                -1,
            )
            
            # Draw track ID text
            cv2.putText(
                annotated_frame,
                label,
                (x1 + 5, label_y),
                self.track_id_font,
                self.track_id_font_scale,
                color,
                self.track_id_thickness,
            )
            
            # Draw class and confidence below track ID
            label_combined = f"{label_class} {label_conf}"
            (text_width2, text_height2), baseline2 = cv2.getTextSize(
                label_combined, self.track_id_font, self.track_id_font_scale - 0.1, 1
            )
            
            label_y2 = label_y + text_height + baseline + 10
            
            cv2.rectangle(
                annotated_frame,
                (x1, label_y2 - text_height2 - baseline2 - 5),
                (x1 + text_width2 + 10, label_y2 + baseline2 + 5),
                self.track_id_bg_color,
                -1,
            )
            
            cv2.putText(
                annotated_frame,
                label_combined,
                (x1 + 5, label_y2),
                self.track_id_font,
                self.track_id_font_scale - 0.1,
                (255, 255, 255),
                1,
            )
        
        return annotated_frame
    
    def set_detections(self, detections: FrameDetections) -> None:
        """
        Set detections from object detection processor.

        Args:
            detections: FrameDetections object
        """
        self.last_detections = detections
        self.current_frame_number = detections.frame_number
        self.current_timestamp = detections.timestamp
    
    def get_last_frame_tracks(self) -> Optional[FrameTracks]:
        """
        Get tracks from the last processed frame.

        Returns:
            FrameTracks object or None
        """
        return self.last_frame_tracks
    
    def get_active_tracks(self) -> List[Track]:
        """
        Get all active tracks from the last frame.

        Returns:
            List of active Track objects
        """
        if self.last_frame_tracks:
            return self.last_frame_tracks.get_active_tracks()
        return []
    
    def get_person_tracks(self) -> List[Track]:
        """
        Get all person tracks from the last frame.

        Returns:
            List of Track objects with class_name="person"
        """
        if self.last_frame_tracks:
            return self.last_frame_tracks.get_tracks_by_class("person")
        return []
    
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """
        Get a specific track by ID from the last frame.

        Args:
            track_id: Track ID to retrieve

        Returns:
            Track object or None if not found
        """
        if self.last_frame_tracks:
            return self.last_frame_tracks.get_track_by_id(track_id)
        return None
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.tracker.cleanup()
        self.last_frame_tracks = None
        self.last_detections = None
        self.logger.info("TrackingProcessor cleaned up")

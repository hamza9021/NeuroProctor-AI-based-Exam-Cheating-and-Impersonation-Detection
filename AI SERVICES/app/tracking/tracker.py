"""
Multi-object tracker wrapper.

This module provides a high-level tracker interface that wraps DeepSORT
and provides a clean API for the video processing pipeline.
"""

from typing import List, Optional
from app.detectors.detection import Detection, FrameDetections
from app.tracking.bytetrack_service import ByteTrackService
from app.tracking.tracking_models import FrameTracks, Track, TrackState
from app.config.settings import settings
from app.utils.logger import get_logger


class MultiObjectTracker:
    """
    High-level multi-object tracker for video processing pipeline.
    
    This class provides a clean interface for tracking objects across frames
    using DeepSORT as the underlying tracking algorithm with re-identification.
    """
    
    def __init__(
        self,
        track_thresh: Optional[float] = None,
        track_buffer: Optional[int] = None,
        match_thresh: Optional[float] = None,
        frame_rate: Optional[int] = None,
    ):
        """
        Initialize multi-object tracker.
        
        Args:
            track_thresh: Detection confidence threshold for tracking
            track_buffer: Buffer size for track management
            match_thresh: IoU threshold for track matching
            frame_rate: Video frame rate for time calculations
        """
        self.logger = get_logger(__name__)
        
        # Use settings defaults if not provided
        track_thresh = track_thresh if track_thresh is not None else getattr(settings, 'TRACK_THRESH', 0.5)
        track_buffer = track_buffer if track_buffer is not None else getattr(settings, 'TRACK_BUFFER', 30)
        match_thresh = match_thresh if match_thresh is not None else getattr(settings, 'MATCH_THRESH', 0.8)
        frame_rate = frame_rate if frame_rate is not None else getattr(settings, 'FRAME_RATE', 30)
        
        self.bytetrack_service = ByteTrackService(
            track_thresh=track_thresh,
            track_buffer=track_buffer,
            match_thresh=match_thresh,
            frame_rate=frame_rate,
        )
        
        self.last_frame_tracks: Optional[FrameTracks] = None
        self.is_initialized = False
        
        self.logger.info("MultiObjectTracker initialized")
    
    def initialize(self) -> None:
        """
        Initialize the tracker.
        
        This method should be called before processing frames.
        """
        if self.is_initialized:
            self.logger.warning("Tracker already initialized")
            return
        
        self.bytetrack_service._initialize_tracker()
        self.is_initialized = True
        self.logger.info("MultiObjectTracker ready")
    
    def process_frame(
        self,
        frame_detections: FrameDetections,
        frame: Optional = None,
    ) -> FrameTracks:
        """
        Process a frame with detections to update tracks.
        
        Args:
            frame_detections: FrameDetections object with detections for current frame
            frame: Current frame as numpy array (needed for DeepSORT embeddings)
            
        Returns:
            FrameTracks object with all active tracks
            
        Raises:
            RuntimeError: If tracker is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Tracker not initialized. Call initialize() first.")
        
        # Filter detections to only include persons for tracking
        person_detections = [
            d for d in frame_detections.detections
            if d.class_name == "person"
        ]
        
        # Log frame availability
        if frame is None:
            self.logger.warning("Frame is None in process_frame - DeepSORT will not work properly")
        else:
            self.logger.debug(f"Frame received in process_frame: shape={frame.shape}, dtype={frame.dtype}")
        
        # Update tracker
        frame_tracks = self.bytetrack_service.update(
            detections=person_detections,
            frame=frame,
            frame_number=frame_detections.frame_number,
            timestamp=frame_detections.timestamp,
        )
        
        self.last_frame_tracks = frame_tracks
        
        # Log summary
        class_counts = frame_tracks.get_class_counts()
        if class_counts:
            self.logger.debug(
                f"Frame {frame_detections.frame_number}: "
                f"Tracks: {len(frame_tracks.get_active_tracks())}, "
                f"Classes: {class_counts}, "
                f"Time: {frame_tracks.processing_time_ms:.2f}ms"
            )
        
        return frame_tracks
    
    def get_last_tracks(self) -> Optional[FrameTracks]:
        """
        Get tracks from the last processed frame.
        
        Returns:
            FrameTracks object or None if no frame processed yet
        """
        return self.last_frame_tracks
    
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
    
    def get_statistics(self):
        """
        Get tracking statistics.
        
        Returns:
            TrackingStatistics object
        """
        return self.bytetrack_service.get_statistics()
    
    def reset(self) -> None:
        """Reset tracker state."""
        self.bytetrack_service.reset()
        self.last_frame_tracks = None
        self.logger.info("MultiObjectTracker reset")
    
    def cleanup(self) -> None:
        """Clean up tracker resources."""
        self.bytetrack_service.cleanup()
        self.last_frame_tracks = None
        self.is_initialized = False
        self.logger.info("MultiObjectTracker cleaned up")

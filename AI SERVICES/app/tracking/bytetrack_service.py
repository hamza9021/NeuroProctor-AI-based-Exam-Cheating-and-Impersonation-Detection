"""
Multi-Object Tracking service using DeepSORT.

This module provides a service wrapper for DeepSORT, a multi-object tracking
algorithm that associates detections across frames using Kalman filtering
and appearance features for re-identification.
"""

import numpy as np
import cv2
from typing import List, Optional, Tuple
import time

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False

# Try to import ByteTrack as fallback
try:
    from bytetracker import BYTETracker
    BYTETRACK_AVAILABLE = True
except ImportError:
    BYTETRACK_AVAILABLE = False

from app.detectors.detection import Detection
from app.tracking.tracking_models import Track, TrackState, FrameTracks, TrackingStatistics
from app.tracking.tracking_utils import detections_to_numpy_array, detection_to_xyxy
from app.utils.logger import get_logger


class ByteTrackService:
    """
    Service for multi-object tracking using DeepSORT.
    
    This service wraps DeepSORT functionality and provides a clean interface
    for tracking objects across video frames with persistent track IDs.
    Note: Named ByteTrackService for API compatibility, but uses DeepSORT internally.
    """
    
    def __init__(
        self,
        track_thresh: float = 0.5,
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        frame_rate: int = 30,
    ):
        """
        Initialize tracking service.
        
        Args:
            track_thresh: Detection confidence threshold for tracking
            track_buffer: Buffer size for track management
            match_thresh: IoU threshold for track matching
            frame_rate: Video frame rate for time calculations
        """
        self.logger = get_logger(__name__)
        
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.frame_rate = frame_rate
        
        self.tracker: Optional["MultiObjectTracker"] = None
        self.is_initialized = False
        
        # Tracking statistics
        self.stats = TrackingStatistics()
        
        # Track ID counter
        self._next_track_id = 1
        
        # Track history for state management
        self._track_history: dict = {}  # track_id -> Track
        
        self._initialize_tracker()
    
    def _initialize_tracker(self) -> None:
        """
        Initialize DeepSORT tracker.
        
        Raises:
            RuntimeError: If DeepSORT is not available
        """
        if not DEEPSORT_AVAILABLE:
            self.logger.error("DeepSORT library not available. Install with: pip install deep-sort-realtime")
            raise RuntimeError("DeepSORT library not available")
        
        try:
            # Initialize with embedder to avoid embedding errors
            self.tracker = DeepSort(
                max_age=self.track_buffer,
                n_init=3,
                nn_budget=100,
                embedder='mobilenet',  # Use MobileNet embedder
            )
            
            self.is_initialized = True
            self.logger.info("DeepSORT tracking service initialized successfully")
            self.logger.info(f"Track threshold: {self.track_thresh}")
            self.logger.info(f"Track buffer: {self.track_buffer}")
            self.logger.info(f"Match threshold: {self.match_thresh}")
        except Exception as e:
            self.logger.error(f"Failed to initialize DeepSORT tracker: {e}")
            self.logger.error("This may be due to pkg_resources import error. Try: pip install setuptools")
            # Don't raise error - allow pipeline to continue without tracking
            self.logger.warning("Tracking will be disabled")
            self.tracker = None
            self.is_initialized = False
    
    def update(
        self,
        detections: List[Detection],
        frame: np.ndarray,
        frame_number: int,
        timestamp: float,
    ) -> FrameTracks:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detections for current frame
            frame: Current frame as numpy array (needed for DeepSORT embeddings)
            frame_number: Current frame number
            timestamp: Current timestamp in seconds
            
        Returns:
            FrameTracks object with all active tracks
        """
        if not self.is_initialized or self.tracker is None:
            self.logger.warning("Tracker not initialized, returning empty tracks")
            return FrameTracks(
                frame_number=frame_number,
                timestamp=timestamp,
                tracks=[],
                processing_time_ms=0.0,
            )
        
        start_time = time.time()
        
        # Convert detections to DeepSORT format
        # DeepSORT expects: List[Tuple[[left, top, width, height], confidence, class_name]]
        deepsort_detections = []
        for det in detections:
            if det.confidence >= self.track_thresh:
                x1, y1, x2, y2 = det.bounding_box
                # Convert from xyxy to ltwh format
                left = x1
                top = y1
                width = x2 - x1
                height = y2 - y1
                
                # Validate bbox dimensions
                if width <= 0 or height <= 0:
                    self.logger.warning(f"Invalid bbox dimensions: {det.bounding_box}, skipping detection")
                    continue
                
                # DeepSORT format: ([left, top, width, height], confidence, class_name)
                deepsort_detections.append((
                    [left, top, width, height],
                    det.confidence,
                    det.class_name
                ))
        
        self.logger.debug(f"Number of detections for tracking: {len(deepsort_detections)}")
        
        # Validate detection format before calling DeepSORT
        if len(deepsort_detections) > 0:
            for i, det in enumerate(deepsort_detections):
                if not isinstance(det, tuple) or len(det) != 3:
                    self.logger.error(f"Malformed detection at index {i}: {det}, expected tuple of (bbox, conf, class)")
                    deepsort_detections = []
                    break
                bbox, conf, cls = det
                if not isinstance(bbox, list) or len(bbox) != 4:
                    self.logger.error(f"Invalid bbox format at index {i}: {bbox}, expected list of 4 elements")
                    deepsort_detections = []
                    break
                if not isinstance(conf, (int, float)):
                    self.logger.error(f"Invalid confidence at index {i}: {conf}, expected float")
                    deepsort_detections = []
                    break
                if not isinstance(cls, str):
                    self.logger.error(f"Invalid class name at index {i}: {cls}, expected string")
                    deepsort_detections = []
                    break
        
        # Update tracker using DeepSORT's update_tracks method
        if len(deepsort_detections) > 0:
            self.logger.debug(f"DeepSORT detections count: {len(deepsort_detections)}")
            self.logger.debug(f"Frame is None: {frame is None}")
            self.logger.debug(f"Frame shape: {frame.shape if frame is not None else 'N/A'}")
            
            try:
                # DeepSORT expects frame in BGR format (default)
                online_targets = self.tracker.update_tracks(deepsort_detections, frame=frame)
            except Exception as e:
                self.logger.error(f"Error calling DeepSORT update_tracks: {e}")
                self.logger.error(f"Detections count: {len(deepsort_detections)}")
                self.logger.error(f"Detections type: {type(deepsort_detections)}")
                self.logger.error(f"Frame is None: {frame is None}")
                if len(deepsort_detections) > 0:
                    self.logger.error(f"First detection: {deepsort_detections[0]}")
                online_targets = []
        else:
            online_targets = []
        
        # Convert DeepSORT results to Track objects
        tracks = self._convert_to_tracks(online_targets, detections, frame_number, timestamp)
        
        # Update track history and manage states
        self._update_track_history(tracks)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Update statistics
        self.stats.total_frames_processed += 1
        self.stats.average_processing_time_ms = (
            (self.stats.average_processing_time_ms * (self.stats.total_frames_processed - 1) + processing_time)
            / self.stats.total_frames_processed
        )
        self.stats.active_tracks = len([t for t in tracks if t.is_active()])
        self.stats.lost_tracks = len([t for t in tracks if t.is_lost()])
        
        # Calculate average track age
        active_tracks = [t for t in tracks if t.is_active()]
        if active_tracks:
            self.stats.average_track_age = sum(t.age for t in active_tracks) / len(active_tracks)
        
        # Create FrameTracks result
        frame_tracks = FrameTracks(
            frame_number=frame_number,
            timestamp=timestamp,
            tracks=tracks,
            processing_time_ms=processing_time,
        )
        
        # Log statistics
        if frame_number % 30 == 0:  # Log every 30 frames
            self._log_statistics()
        
        return frame_tracks
    
    def _convert_to_tracks(
        self,
        online_targets: List,
        detections: List[Detection],
        frame_number: int,
        timestamp: float,
    ) -> List[Track]:
        """
        Convert DeepSORT results to Track objects.
        
        Args:
            online_targets: DeepSORT output targets
            detections: Original detections
            frame_number: Current frame number
            timestamp: Current timestamp
            
        Returns:
            List of Track objects
        """
        tracks = []
        
        for target in online_targets:
            # DeepSORT track object has track_id attribute
            if not hasattr(target, 'track_id'):
                self.logger.warning(f"Target missing track_id attribute: {target}")
                continue
                
            track_id = int(target.track_id)
            
            # Get bounding box - DeepSORT uses tlwh format (top, left, width, height)
            if hasattr(target, 'tlwh'):
                bbox = target.tlwh
                t, l, w, h = bbox
                x1, y1 = l, t
                x2, y2 = x1 + w, y1 + h
            elif hasattr(target, 'to_tlwh'):
                bbox = target.to_tlwh()
                t, l, w, h = bbox
                x1, y1 = l, t
                x2, y2 = x1 + w, y1 + h
            else:
                self.logger.warning(f"Target missing bbox attributes: {target}")
                continue
            
            # Get confidence
            confidence = getattr(target, 'confidence', 0.0)
            
            # Get class name if available
            class_name = getattr(target, 'class_name', 'person')
            
            # Get track state
            if hasattr(target, 'is_confirmed'):
                is_confirmed = target.is_confirmed()
                is_deleted = getattr(target, 'is_deleted', lambda: False)()
                is_tentative = getattr(target, 'is_tentative', lambda: False)()
                
                if is_deleted:
                    state = TrackState.REMOVED
                elif is_tentative:
                    state = TrackState.NEW
                elif is_confirmed:
                    state = TrackState.ACTIVE
                else:
                    state = TrackState.TEMPORARILY_LOST
            else:
                state = TrackState.ACTIVE
            
            # Get track history if exists
            history = self._track_history.get(track_id)
            
            if history:
                # Update existing track
                age = history.age + 1
                hit_count = history.hit_count + 1
                time_since_update = 0
            else:
                # New track
                age = 0
                hit_count = 1
                time_since_update = 0
                state = TrackState.NEW
                self.stats.total_tracks_created += 1
                self.logger.info(f"New track created: ID {track_id}, Class: {class_name}")
            
            track = Track(
                track_id=track_id,
                class_name=class_name,
                confidence=confidence,
                bounding_box=(int(x1), int(y1), int(x2), int(y2)),
                frame_number=frame_number,
                timestamp=timestamp,
                state=state,
                age=age,
                hit_count=hit_count,
                time_since_update=time_since_update,
            )
            
            tracks.append(track)
        
        return tracks
    
    def _find_best_detection(
        self,
        bbox: Tuple[float, float, float, float],
        detections: List[Detection],
        iou_threshold: float = 0.3,
    ) -> Optional[Detection]:
        """
        Find the best matching detection for a bounding box.
        
        Args:
            bbox: Bounding box to match
            detections: List of detections
            iou_threshold: Minimum IoU threshold
            
        Returns:
            Best matching detection or None
        """
        from app.tracking.tracking_utils import calculate_iou
        
        best_detection = None
        best_iou = iou_threshold
        
        for detection in detections:
            iou = calculate_iou(bbox, detection.bounding_box)
            if iou > best_iou:
                best_iou = iou
                best_detection = detection
        
        return best_detection
    
    def _update_track_history(self, current_tracks: List[Track]) -> None:
        """
        Update track history and manage track states.
        
        Args:
            current_tracks: Tracks from current frame
        """
        current_ids = {track.track_id for track in current_tracks}
        
        # Update or add current tracks
        for track in current_tracks:
            self._track_history[track.track_id] = track
        
        # Mark tracks not in current frame as temporarily lost
        for track_id, track in self._track_history.items():
            if track_id not in current_ids and track.is_active():
                track.time_since_update += 1
                if track.time_since_update > self.track_buffer:
                    track.state = TrackState.REMOVED
                    self.stats.total_tracks_removed += 1
                    self.logger.info(f"Track removed: ID {track_id}, Age: {track.age}")
                else:
                    track.state = TrackState.TEMPORARILY_LOST
                    if track.time_since_update == 1:
                        self.logger.info(f"Track temporarily lost: ID {track_id}")
    
    def _log_statistics(self) -> None:
        """Log tracking statistics."""
        self.logger.info(
            f"Tracking Stats - Active: {self.stats.active_tracks}, "
            f"Lost: {self.stats.lost_tracks}, "
            f"Created: {self.stats.total_tracks_created}, "
            f"Removed: {self.stats.total_tracks_removed}, "
            f"Avg Age: {self.stats.average_track_age:.1f}, "
            f"Avg Time: {self.stats.average_processing_time_ms:.2f}ms"
        )
    
    def get_statistics(self) -> TrackingStatistics:
        """
        Get current tracking statistics.
        
        Returns:
            TrackingStatistics object
        """
        return self.stats
    
    def reset(self) -> None:
        """Reset tracker state."""
        self._initialize_tracker()
        
        self._track_history.clear()
        self._next_track_id = 1
        self.stats = TrackingStatistics()
        
        self.logger.info("Tracking service reset")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.tracker = None
        self._track_history.clear()
        self.is_initialized = False
        self.logger.info("Tracking service cleaned up")

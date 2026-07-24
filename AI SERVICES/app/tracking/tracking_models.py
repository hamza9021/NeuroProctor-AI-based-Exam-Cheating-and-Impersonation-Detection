"""
Tracking data models for multi-object tracking.

This module defines the data structures used for tracking objects across video frames,
including track states, individual tracks, and frame-level tracking results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional, List
from datetime import datetime


class TrackState(Enum):
    """Track lifecycle states."""
    NEW = "new"
    ACTIVE = "active"
    TEMPORARILY_LOST = "temporarily_lost"
    REMOVED = "removed"


@dataclass
class Track:
    """
    Represents a single tracked object across frames.
    
    Attributes:
        track_id: Unique identifier for this track
        class_name: Detection class (e.g., "person")
        confidence: Detection confidence score
        bounding_box: Bounding box coordinates (x1, y1, x2, y2)
        frame_number: Current frame number
        timestamp: Current timestamp in seconds
        state: Current track state
        age: Number of frames this track has been active
        hit_count: Number of successful detections for this track
        time_since_update: Frames since last successful update
    """
    track_id: int
    class_name: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]
    frame_number: int
    timestamp: float
    state: TrackState = TrackState.NEW
    age: int = 0
    hit_count: int = 1
    time_since_update: int = 0
    
    def to_dict(self) -> dict:
        """Convert track to dictionary representation."""
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "state": self.state.value,
            "age": self.age,
            "hit_count": self.hit_count,
            "time_since_update": self.time_since_update,
        }
    
    def is_active(self) -> bool:
        """Check if track is currently active."""
        return self.state in (TrackState.NEW, TrackState.ACTIVE)
    
    def is_lost(self) -> bool:
        """Check if track is temporarily lost."""
        return self.state == TrackState.TEMPORARILY_LOST


@dataclass
class FrameTracks:
    """
    Represents all tracks for a single frame.
    
    Attributes:
        frame_number: Frame number
        timestamp: Frame timestamp in seconds
        tracks: List of active tracks in this frame
        processing_time_ms: Time taken to process tracking for this frame
    """
    frame_number: int
    timestamp: float
    tracks: List[Track] = field(default_factory=list)
    processing_time_ms: float = 0.0
    
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """Get a track by its ID."""
        for track in self.tracks:
            if track.track_id == track_id:
                return track
        return None
    
    def get_tracks_by_class(self, class_name: str) -> List[Track]:
        """Get all tracks of a specific class."""
        return [track for track in self.tracks if track.class_name == class_name]
    
    def get_active_tracks(self) -> List[Track]:
        """Get all active tracks."""
        return [track for track in self.tracks if track.is_active()]
    
    def get_lost_tracks(self) -> List[Track]:
        """Get all temporarily lost tracks."""
        return [track for track in self.tracks if track.is_lost()]
    
    def get_class_counts(self) -> dict:
        """Get count of tracks per class."""
        counts = {}
        for track in self.tracks:
            if track.is_active():
                counts[track.class_name] = counts.get(track.class_name, 0) + 1
        return counts
    
    def to_dict(self) -> dict:
        """Convert frame tracks to dictionary representation."""
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "tracks": [track.to_dict() for track in self.tracks],
            "processing_time_ms": self.processing_time_ms,
            "active_count": len(self.get_active_tracks()),
            "lost_count": len(self.get_lost_tracks()),
        }


@dataclass
class TrackingStatistics:
    """
    Statistics for tracking performance.
    
    Attributes:
        total_tracks_created: Total number of tracks created
        total_tracks_removed: Total number of tracks removed
        active_tracks: Current number of active tracks
        lost_tracks: Current number of lost tracks
        average_track_age: Average age of active tracks
        total_frames_processed: Total frames processed
        average_processing_time_ms: Average processing time per frame
    """
    total_tracks_created: int = 0
    total_tracks_removed: int = 0
    active_tracks: int = 0
    lost_tracks: int = 0
    average_track_age: float = 0.0
    total_frames_processed: int = 0
    average_processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert statistics to dictionary representation."""
        return {
            "total_tracks_created": self.total_tracks_created,
            "total_tracks_removed": self.total_tracks_removed,
            "active_tracks": self.active_tracks,
            "lost_tracks": self.lost_tracks,
            "average_track_age": self.average_track_age,
            "total_frames_processed": self.total_frames_processed,
            "average_processing_time_ms": self.average_processing_time_ms,
        }

"""
Head pose estimation data schemas.

This module defines structured data classes for head pose estimation results,
ensuring type safety and consistency throughout the pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class HeadPoseResult:
    """
    Head pose estimation result for a single tracked person.
    
    This data class represents the 6D head orientation (yaw, pitch, roll)
    for a specific track at a specific frame.
    
    Attributes:
        track_id: DeepSORT Track ID for persistent identity
        frame_number: Frame number in the video
        timestamp: Timestamp in seconds from video start
        yaw: Left/right rotation in degrees (-90 to 90)
        pitch: Up/down rotation in degrees (-90 to 90)
        roll: Head tilt in degrees (-90 to 90)
        confidence: Model confidence score (0.0 to 1.0)
        face_crop_bbox: Bounding box of the face crop used (x1, y1, x2, y2)
        metadata: Additional metadata for extensibility
    """
    track_id: int
    frame_number: int
    timestamp: float
    yaw: float
    pitch: float
    roll: float
    confidence: float
    face_crop_bbox: Optional[tuple] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the head pose result
        """
        return {
            'track_id': self.track_id,
            'frame_number': self.frame_number,
            'timestamp': self.timestamp,
            'yaw': self.yaw,
            'pitch': self.pitch,
            'roll': self.roll,
            'confidence': self.confidence,
            'face_crop_bbox': self.face_crop_bbox,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeadPoseResult':
        """
        Create from dictionary for deserialization.
        
        Args:
            data: Dictionary containing head pose data
            
        Returns:
            HeadPoseResult instance
        """
        return cls(
            track_id=data['track_id'],
            frame_number=data['frame_number'],
            timestamp=data['timestamp'],
            yaw=data['yaw'],
            pitch=data['pitch'],
            roll=data['roll'],
            confidence=data['confidence'],
            face_crop_bbox=data.get('face_crop_bbox'),
            metadata=data.get('metadata', {}),
        )
    
    def get_orientation_vector(self) -> tuple:
        """
        Get orientation as a 3D vector for visualization.
        
        Returns:
            Tuple of (yaw, pitch, roll) in degrees
        """
        return (self.yaw, self.pitch, self.roll)
    
    def is_looking_away(self, yaw_threshold: float = 30.0) -> bool:
        """
        Check if the person is looking away based on yaw angle.
        
        Args:
            yaw_threshold: Yaw angle threshold in degrees
            
        Returns:
            True if looking away, False otherwise
        """
        return abs(self.yaw) > yaw_threshold
    
    def is_looking_down(self, pitch_threshold: float = 20.0) -> bool:
        """
        Check if the person is looking down based on pitch angle.
        
        Args:
            pitch_threshold: Pitch angle threshold in degrees
            
        Returns:
            True if looking down, False otherwise
        """
        return self.pitch > pitch_threshold


@dataclass
class FrameHeadPoses:
    """
    Container for all head pose results in a single frame.
    
    This data class aggregates head pose estimates for all tracked
    persons in a specific frame.
    
    Attributes:
        frame_number: Frame number in the video
        timestamp: Timestamp in seconds from video start
        head_poses: List of HeadPoseResult for this frame
        processing_time_ms: Processing time in milliseconds
    """
    frame_number: int
    timestamp: float
    head_poses: List[HeadPoseResult] = field(default_factory=list)
    processing_time_ms: float = 0.0
    
    def get_head_pose_by_track_id(self, track_id: int) -> Optional[HeadPoseResult]:
        """
        Get head pose result for a specific track ID.
        
        Args:
            track_id: Track ID to search for
            
        Returns:
            HeadPoseResult if found, None otherwise
        """
        for head_pose in self.head_poses:
            if head_pose.track_id == track_id:
                return head_pose
        return None
    
    def get_track_ids(self) -> List[int]:
        """
        Get all track IDs with head pose estimates in this frame.
        
        Returns:
            List of track IDs
        """
        return [hp.track_id for hp in self.head_poses]
    
    def filter_by_confidence(self, min_confidence: float) -> 'FrameHeadPoses':
        """
        Filter head poses by minimum confidence threshold.
        
        Args:
            min_confidence: Minimum confidence threshold
            
        Returns:
            New FrameHeadPoses with filtered results
        """
        filtered_poses = [hp for hp in self.head_poses if hp.confidence >= min_confidence]
        return FrameHeadPoses(
            frame_number=self.frame_number,
            timestamp=self.timestamp,
            head_poses=filtered_poses,
            processing_time_ms=self.processing_time_ms,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the frame head poses
        """
        return {
            'frame_number': self.frame_number,
            'timestamp': self.timestamp,
            'head_poses': [hp.to_dict() for hp in self.head_poses],
            'processing_time_ms': self.processing_time_ms,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameHeadPoses':
        """
        Create from dictionary for deserialization.
        
        Args:
            data: Dictionary containing frame head poses data
            
        Returns:
            FrameHeadPoses instance
        """
        head_poses = [HeadPoseResult.from_dict(hp_data) for hp_data in data.get('head_poses', [])]
        return cls(
            frame_number=data['frame_number'],
            timestamp=data['timestamp'],
            head_poses=head_poses,
            processing_time_ms=data.get('processing_time_ms', 0.0),
        )
    
    def __len__(self) -> int:
        """Return the number of head pose results."""
        return len(self.head_poses)

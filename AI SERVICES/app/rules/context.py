"""
Rule context for rule evaluation.

This module provides the context object that contains all the data
needed for rule evaluation.
"""

from dataclasses import dataclass
from typing import Optional, List
import numpy as np

from app.detectors.detection import FrameDetections
from app.pose.pose_result import PoseResult
from app.head_pose.schemas import FrameHeadPoses


@dataclass
class RuleContext:
    """Context object containing data for rule evaluation."""

    frame: np.ndarray
    frame_number: int
    timestamp: float
    detections: Optional[FrameDetections] = None
    pose_result: Optional[PoseResult] = None
    head_poses: Optional[FrameHeadPoses] = None
    frame_width: int = 0
    frame_height: int = 0

    def __post_init__(self):
        """Initialize frame dimensions if not provided."""
        if self.frame_width == 0 or self.frame_height == 0:
            if self.frame is not None:
                self.frame_height, self.frame_width = self.frame.shape[:2]

    def get_person_count(self) -> int:
        """
        Get number of detected persons.

        Returns:
            Number of persons
        """
        if self.detections is None:
            return 0
        
        return len([d for d in self.detections.detections if d.class_name == "person"])

    def get_detections_by_class(self, class_name: str) -> List:
        """
        Get detections of a specific class.

        Args:
            class_name: Class name to filter by

        Returns:
            List of detections of the specified class
        """
        if self.detections is None:
            return []
        
        return [d for d in self.detections.detections if d.class_name == class_name]

    def get_pose_person_count(self) -> int:
        """
        Get number of persons from pose estimation.

        Returns:
            Number of persons
        """
        if self.pose_result is None:
            return 0
        
        return self.pose_result.get_person_count()

    def has_detections(self) -> bool:
        """
        Check if there are any detections.

        Returns:
            True if detections exist
        """
        return self.detections is not None and len(self.detections.detections) > 0

    def has_poses(self) -> bool:
        """
        Check if there are any pose results.

        Returns:
            True if pose results exist
        """
        return self.pose_result is not None and len(self.pose_result.persons) > 0

    def has_head_poses(self) -> bool:
        """
        Check if there are any head pose results.

        Returns:
            True if head pose results exist
        """
        return self.head_poses is not None and len(self.head_poses.head_poses) > 0

    def get_head_pose_by_track_id(self, track_id: int):
        """
        Get head pose for a specific track ID.

        Args:
            track_id: Track ID to retrieve

        Returns:
            HeadPoseResult if found, None otherwise
        """
        if self.head_poses is None:
            return None
        return self.head_poses.get_head_pose_by_track_id(track_id)

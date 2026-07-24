"""
Pose result data model for pose estimation.

This module provides data classes for storing pose estimation results
from YOLO pose estimation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

from app.pose.keypoints import Keypoints


@dataclass
class PersonPose:
    """Data class for pose of a single person."""

    person_id: int
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    keypoints: Keypoints
    track_id: Optional[int] = None  # ByteTrack Track ID for persistent identity

    def get_center_point(self) -> Tuple[float, float]:
        """
        Get center point of person bounding box.

        Returns:
            Tuple of (x, y) center coordinates
        """
        x1, y1, x2, y2 = self.bounding_box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return (center_x, center_y)

    def to_dict(self) -> dict:
        """
        Convert person pose to dictionary.

        Returns:
            Dictionary representation of person pose
        """
        return {
            "person_id": self.person_id,
            "track_id": self.track_id,
            "bounding_box": self.bounding_box,
            "confidence": self.confidence,
            "keypoints": self.keypoints.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PersonPose":
        """
        Create PersonPose instance from dictionary.

        Args:
            data: Dictionary containing person pose data

        Returns:
            PersonPose instance
        """
        return cls(
            person_id=data.get("person_id", 0),
            track_id=data.get("track_id"),
            bounding_box=tuple(data.get("bounding_box", (0, 0, 0, 0))),
            confidence=data.get("confidence", 0.0),
            keypoints=Keypoints.from_dict(data.get("keypoints", {})),
        )


@dataclass
class PoseResult:
    """Data class for pose estimation results in a frame."""

    frame_number: int
    timestamp: float
    persons: List[PersonPose]
    inference_time_ms: float

    def get_person_count(self) -> int:
        """
        Get number of detected persons.

        Returns:
            Number of persons
        """
        return len(self.persons)

    def get_person_by_id(self, person_id: int) -> PersonPose:
        """
        Get person pose by ID.

        Args:
            person_id: Person ID

        Returns:
            PersonPose if found, raises ValueError otherwise
        """
        for person in self.persons:
            if person.person_id == person_id:
                return person
        raise ValueError(f"Person with ID {person_id} not found")

    def to_dict(self) -> dict:
        """
        Convert pose result to dictionary.

        Returns:
            Dictionary representation of pose result
        """
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "persons": [person.to_dict() for person in self.persons],
            "inference_time_ms": self.inference_time_ms,
            "person_count": self.get_person_count(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PoseResult":
        """
        Create PoseResult instance from dictionary.

        Args:
            data: Dictionary containing pose result data

        Returns:
            PoseResult instance
        """
        persons = [PersonPose.from_dict(p) for p in data.get("persons", [])]
        return cls(
            frame_number=data.get("frame_number", 0),
            timestamp=data.get("timestamp", 0.0),
            persons=persons,
            inference_time_ms=data.get("inference_time_ms", 0.0),
        )

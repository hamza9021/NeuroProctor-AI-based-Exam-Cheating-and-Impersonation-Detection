"""
Keypoints data model for pose estimation.

This module provides data classes for storing body keypoints
from YOLO pose estimation.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, List


@dataclass
class Keypoint:
    """Data class for a single body keypoint."""

    x: float
    y: float
    confidence: float
    name: str

    def is_visible(self, threshold: float = 0.5) -> bool:
        """
        Check if keypoint is visible based on confidence threshold.

        Args:
            threshold: Confidence threshold for visibility

        Returns:
            True if keypoint is visible
        """
        return self.confidence >= threshold

    def to_tuple(self) -> Tuple[float, float]:
        """
        Get keypoint coordinates as tuple.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def to_dict(self) -> dict:
        """
        Convert keypoint to dictionary.

        Returns:
            Dictionary representation of keypoint
        """
        return {
            "x": self.x,
            "y": self.y,
            "confidence": self.confidence,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Keypoint":
        """
        Create Keypoint instance from dictionary.

        Args:
            data: Dictionary containing keypoint data

        Returns:
            Keypoint instance
        """
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            confidence=data.get("confidence", 0.0),
            name=data.get("name", ""),
        )


@dataclass
class Keypoints:
    """Data class for all body keypoints of a person."""

    # COCO 17 keypoints
    nose: Optional[Keypoint] = None
    left_eye: Optional[Keypoint] = None
    right_eye: Optional[Keypoint] = None
    left_ear: Optional[Keypoint] = None
    right_ear: Optional[Keypoint] = None
    left_shoulder: Optional[Keypoint] = None
    right_shoulder: Optional[Keypoint] = None
    left_elbow: Optional[Keypoint] = None
    right_elbow: Optional[Keypoint] = None
    left_wrist: Optional[Keypoint] = None
    right_wrist: Optional[Keypoint] = None
    left_hip: Optional[Keypoint] = None
    right_hip: Optional[Keypoint] = None
    left_knee: Optional[Keypoint] = None
    right_knee: Optional[Keypoint] = None
    left_ankle: Optional[Keypoint] = None
    right_ankle: Optional[Keypoint] = None

    def get_visible_keypoints(self, threshold: float = 0.5) -> List[Keypoint]:
        """
        Get all visible keypoints.

        Args:
            threshold: Confidence threshold for visibility

        Returns:
            List of visible keypoints
        """
        visible = []
        for keypoint in [
            self.nose, self.left_eye, self.right_eye, self.left_ear, self.right_ear,
            self.left_shoulder, self.right_shoulder, self.left_elbow, self.right_elbow,
            self.left_wrist, self.right_wrist, self.left_hip, self.right_hip,
            self.left_knee, self.right_knee, self.left_ankle, self.right_ankle,
        ]:
            if keypoint and keypoint.is_visible(threshold):
                visible.append(keypoint)
        return visible

    def get_keypoint_by_name(self, name: str) -> Optional[Keypoint]:
        """
        Get keypoint by name.

        Args:
            name: Name of the keypoint

        Returns:
            Keypoint if found, None otherwise
        """
        return getattr(self, name, None)

    def to_dict(self) -> dict:
        """
        Convert keypoints to dictionary.

        Returns:
            Dictionary representation of keypoints
        """
        return {
            "nose": self.nose.to_dict() if self.nose else None,
            "left_eye": self.left_eye.to_dict() if self.left_eye else None,
            "right_eye": self.right_eye.to_dict() if self.right_eye else None,
            "left_ear": self.left_ear.to_dict() if self.left_ear else None,
            "right_ear": self.right_ear.to_dict() if self.right_ear else None,
            "left_shoulder": self.left_shoulder.to_dict() if self.left_shoulder else None,
            "right_shoulder": self.right_shoulder.to_dict() if self.right_shoulder else None,
            "left_elbow": self.left_elbow.to_dict() if self.left_elbow else None,
            "right_elbow": self.right_elbow.to_dict() if self.right_elbow else None,
            "left_wrist": self.left_wrist.to_dict() if self.left_wrist else None,
            "right_wrist": self.right_wrist.to_dict() if self.right_wrist else None,
            "left_hip": self.left_hip.to_dict() if self.left_hip else None,
            "right_hip": self.right_hip.to_dict() if self.right_hip else None,
            "left_knee": self.left_knee.to_dict() if self.left_knee else None,
            "right_knee": self.right_knee.to_dict() if self.right_knee else None,
            "left_ankle": self.left_ankle.to_dict() if self.left_ankle else None,
            "right_ankle": self.right_ankle.to_dict() if self.right_ankle else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Keypoints":
        """
        Create Keypoints instance from dictionary.

        Args:
            data: Dictionary containing keypoints data

        Returns:
            Keypoints instance
        """
        return cls(
            nose=Keypoint.from_dict(data["nose"]) if data.get("nose") else None,
            left_eye=Keypoint.from_dict(data["left_eye"]) if data.get("left_eye") else None,
            right_eye=Keypoint.from_dict(data["right_eye"]) if data.get("right_eye") else None,
            left_ear=Keypoint.from_dict(data["left_ear"]) if data.get("left_ear") else None,
            right_ear=Keypoint.from_dict(data["right_ear"]) if data.get("right_ear") else None,
            left_shoulder=Keypoint.from_dict(data["left_shoulder"]) if data.get("left_shoulder") else None,
            right_shoulder=Keypoint.from_dict(data["right_shoulder"]) if data.get("right_shoulder") else None,
            left_elbow=Keypoint.from_dict(data["left_elbow"]) if data.get("left_elbow") else None,
            right_elbow=Keypoint.from_dict(data["right_elbow"]) if data.get("right_elbow") else None,
            left_wrist=Keypoint.from_dict(data["left_wrist"]) if data.get("left_wrist") else None,
            right_wrist=Keypoint.from_dict(data["right_wrist"]) if data.get("right_wrist") else None,
            left_hip=Keypoint.from_dict(data["left_hip"]) if data.get("left_hip") else None,
            right_hip=Keypoint.from_dict(data["right_hip"]) if data.get("right_hip") else None,
            left_knee=Keypoint.from_dict(data["left_knee"]) if data.get("left_knee") else None,
            right_knee=Keypoint.from_dict(data["right_knee"]) if data.get("right_knee") else None,
            left_ankle=Keypoint.from_dict(data["left_ankle"]) if data.get("left_ankle") else None,
            right_ankle=Keypoint.from_dict(data["right_ankle"]) if data.get("right_ankle") else None,
        )

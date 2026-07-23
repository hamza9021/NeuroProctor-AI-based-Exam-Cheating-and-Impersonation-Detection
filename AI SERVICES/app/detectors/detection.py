"""
Detection data model for object detection results.

This module provides a data class to store structured detection results
from YOLO object detection.
"""

from dataclasses import dataclass
from typing import Tuple, List
import numpy as np


@dataclass
class Detection:
    """Data class for a single object detection result."""

    class_name: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center_point: Tuple[float, float]  # (x, y)

    def to_dict(self) -> dict:
        """
        Convert detection to dictionary.

        Returns:
            Dictionary representation of detection
        """
        return {
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "center_point": self.center_point,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Detection":
        """
        Create Detection instance from dictionary.

        Args:
            data: Dictionary containing detection data

        Returns:
            Detection instance
        """
        return cls(
            class_name=data.get("class_name", ""),
            confidence=data.get("confidence", 0.0),
            bounding_box=tuple(data.get("bounding_box", (0, 0, 0, 0))),
            center_point=tuple(data.get("center_point", (0.0, 0.0))),
        )


@dataclass
class FrameDetections:
    """Data class for all detections in a single frame."""

    frame_number: int
    timestamp: float
    detections: List[Detection]
    inference_time_ms: float

    def get_detections_by_class(self, class_name: str) -> List[Detection]:
        """
        Get all detections of a specific class.

        Args:
            class_name: Class name to filter by

        Returns:
            List of detections of the specified class
        """
        return [d for d in self.detections if d.class_name == class_name]

    def get_class_counts(self) -> dict:
        """
        Get count of detections per class.

        Returns:
            Dictionary with class names as keys and counts as values
        """
        counts = {}
        for detection in self.detections:
            class_name = detection.class_name
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts

    def to_dict(self) -> dict:
        """
        Convert frame detections to dictionary.

        Returns:
            Dictionary representation of frame detections
        """
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "detections": [d.to_dict() for d in self.detections],
            "inference_time_ms": self.inference_time_ms,
            "class_counts": self.get_class_counts(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FrameDetections":
        """
        Create FrameDetections instance from dictionary.

        Args:
            data: Dictionary containing frame detections data

        Returns:
            FrameDetections instance
        """
        detections = [Detection.from_dict(d) for d in data.get("detections", [])]
        return cls(
            frame_number=data.get("frame_number", 0),
            timestamp=data.get("timestamp", 0.0),
            detections=detections,
            inference_time_ms=data.get("inference_time_ms", 0.0),
        )

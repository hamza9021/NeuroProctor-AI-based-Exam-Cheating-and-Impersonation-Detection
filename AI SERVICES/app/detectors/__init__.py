"""
Detectors module for object detection.
"""

from .detection import Detection, FrameDetections
from .object_detector import ObjectDetector

__all__ = ["Detection", "FrameDetections", "ObjectDetector"]

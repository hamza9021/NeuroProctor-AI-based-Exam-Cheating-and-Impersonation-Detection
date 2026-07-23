"""
Processors module for video frame processing.
"""

from .base_processor import (
    BaseProcessor,
    PlaceholderProcessor,
    ObjectDetector,
    FaceRecognizer,
    PoseEstimator,
    BehaviorRecognizer,
    FusionProcessor,
    TemporalSmoother,
    RuleEngine,
)
from .object_detection_processor import ObjectDetectionProcessor

__all__ = [
    "BaseProcessor",
    "PlaceholderProcessor",
    "ObjectDetector",
    "FaceRecognizer",
    "PoseEstimator",
    "BehaviorRecognizer",
    "FusionProcessor",
    "TemporalSmoother",
    "RuleEngine",
    "ObjectDetectionProcessor",
]

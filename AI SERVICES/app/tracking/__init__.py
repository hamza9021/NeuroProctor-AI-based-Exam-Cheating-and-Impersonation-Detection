"""
Tracking module for multi-object tracking.

This module provides ByteTrack-based multi-object tracking functionality
for the AI Services video processing pipeline.
"""

from .tracking_models import Track, TrackState, FrameTracks, TrackingStatistics
from .tracking_utils import (
    detection_to_xywh,
    detection_to_xyxy,
    detections_to_numpy_array,
    filter_detections_by_class,
    filter_detections_by_confidence,
    calculate_iou,
    calculate_area,
    calculate_center,
    merge_overlapping_detections,
    validate_bounding_box,
)
from .bytetrack_service import ByteTrackService
from .tracker import MultiObjectTracker

__all__ = [
    # Models
    "Track",
    "TrackState",
    "FrameTracks",
    "TrackingStatistics",
    # Utilities
    "detection_to_xywh",
    "detection_to_xyxy",
    "detections_to_numpy_array",
    "filter_detections_by_class",
    "filter_detections_by_confidence",
    "calculate_iou",
    "calculate_area",
    "calculate_center",
    "merge_overlapping_detections",
    "validate_bounding_box",
    # Services
    "ByteTrackService",
    "MultiObjectTracker",
]

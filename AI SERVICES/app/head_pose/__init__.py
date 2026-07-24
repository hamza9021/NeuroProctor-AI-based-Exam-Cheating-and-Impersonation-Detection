"""
Head Pose Estimation Module.

This module provides head orientation estimation using 6DRepNet for
behavioral analysis in exam monitoring scenarios.
"""

from .schemas import HeadPoseResult, FrameHeadPoses
from .service import HeadPoseService
from .model_loader import HeadPoseModelLoader
from .face_cropper import FaceCropper

__all__ = [
    'HeadPoseResult',
    'FrameHeadPoses',
    'HeadPoseService',
    'HeadPoseModelLoader',
    'FaceCropper',
]

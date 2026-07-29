"""Custom exceptions for head pose estimation."""


class HeadPoseError(Exception):
    """Base exception for head pose estimation errors."""
    pass


class HeadPoseInitializationError(HeadPoseError):
    """Raised when head pose model initialization fails."""
    pass


class FaceRegionNotFoundError(HeadPoseError):
    """Raised when no valid face/head region is found for a track."""
    pass


class InvalidFaceCropError(HeadPoseError):
    """Raised when face crop is invalid."""
    pass


class HeadPoseInferenceError(HeadPoseError):
    """Raised when head pose inference fails."""
    pass


class HeadPoseParsingError(HeadPoseError):
    """Raised when parsing model output fails."""
    pass


class HeadPoseValidationError(HeadPoseError):
    """Raised when head pose result validation fails."""
    pass


class HeadPoseAnnotationError(HeadPoseError):
    """Raised when annotation fails."""
    pass

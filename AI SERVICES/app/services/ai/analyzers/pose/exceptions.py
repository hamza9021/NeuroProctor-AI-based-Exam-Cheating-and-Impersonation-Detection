"""Custom exceptions for YOLO pose estimation."""


class PoseError(Exception):
    """Base exception for pose estimation errors."""
    pass


class PoseInitializationError(PoseError):
    """Raised when pose model fails to initialize."""
    pass


class PoseInferenceError(PoseError):
    """Raised when pose inference fails."""
    pass


class PoseParsingError(PoseError):
    """Raised when pose parsing fails."""
    pass


class PoseValidationError(PoseError):
    """Raised when pose validation fails."""
    pass


class PoseAssociationError(PoseError):
    """Raised when track-to-pose association fails."""
    pass


class PoseAnnotationError(PoseError):
    """Raised when pose annotation fails."""
    pass

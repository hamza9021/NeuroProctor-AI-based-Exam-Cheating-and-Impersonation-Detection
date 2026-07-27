"""Custom exceptions for DeepSORT tracking."""


class DeepSortError(Exception):
    """Base exception for DeepSORT tracking errors."""
    pass


class DeepSortInitializationError(DeepSortError):
    """Raised when tracker fails to initialize."""
    pass


class DeepSortTrackingError(DeepSortError):
    """Raised when tracking operation fails."""
    pass


class InvalidTrackingDetectionError(DeepSortError):
    """Raised when detection data is invalid."""
    pass


class TrackParsingError(DeepSortError):
    """Raised when track parsing fails."""
    pass


class TrackingAnnotationError(DeepSortError):
    """Raised when annotation fails."""
    pass

"""YOLO detection exceptions."""


class YOLOError(Exception):
    """Base exception for YOLO detection errors."""
    pass


class ModelLoadError(YOLOError):
    """Raised when YOLO model fails to load."""
    pass


class ModelNotFoundError(YOLOError):
    """Raised when YOLO model file is not found."""
    pass


class InferenceError(YOLOError):
    """Raised when YOLO inference fails."""
    pass


class InvalidFrameError(YOLOError):
    """Raised when frame is invalid for inference."""
    pass


class DeviceError(YOLOError):
    """Raised when GPU/CUDA device is unavailable."""
    pass

"""
Base processor module for AI Services.

This module provides an abstract base class for all video processors.
Future processors (ObjectDetector, FaceRecognizer, etc.) will inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseProcessor(ABC):
    """Abstract base class for video frame processors."""

    def __init__(self, name: str):
        """
        Initialize base processor.

        Args:
            name: Name of the processor
        """
        self.name = name
        self._config: Dict[str, Any] = {}

    @abstractmethod
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a single frame.

        Args:
            frame: Input frame as numpy array

        Returns:
            Processed frame as numpy array
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the processor (load models, setup resources, etc.)."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up processor resources."""
        pass

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set processor configuration.

        Args:
            config: Configuration dictionary
        """
        self._config.update(config)

    def get_config(self) -> Dict[str, Any]:
        """
        Get processor configuration.

        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    def get_name(self) -> str:
        """
        Get processor name.

        Returns:
            Processor name
        """
        return self.name

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class PlaceholderProcessor(BaseProcessor):
    """
    Placeholder processor for pipeline testing.
    
    This processor simply returns the original frame without modification.
    Used for testing the pipeline infrastructure before implementing actual AI models.
    """

    def __init__(self):
        """Initialize placeholder processor."""
        super().__init__("PlaceholderProcessor")

    def initialize(self) -> None:
        """Initialize placeholder processor (no-op)."""
        pass

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame (no-op, returns original frame).

        Args:
            frame: Input frame

        Returns:
            Original frame unchanged
        """
        return frame

    def cleanup(self) -> None:
        """Cleanup placeholder processor (no-op)."""
        pass


# Future processor placeholders (not implemented in this phase)
# These will be implemented in future phases as AI models are added

class ObjectDetector(BaseProcessor):
    """Placeholder for YOLO object detection processor."""
    
    def initialize(self) -> None:
        """Initialize object detector."""
        raise NotImplementedError("ObjectDetector not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with object detection."""
        raise NotImplementedError("ObjectDetector not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup object detector resources."""
        raise NotImplementedError("ObjectDetector not implemented in this phase")


class FaceRecognizer(BaseProcessor):
    """Placeholder for face recognition processor."""
    
    def initialize(self) -> None:
        """Initialize face recognizer."""
        raise NotImplementedError("FaceRecognizer not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with face recognition."""
        raise NotImplementedError("FaceRecognizer not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup face recognizer resources."""
        raise NotImplementedError("FaceRecognizer not implemented in this phase")


class PoseEstimator(BaseProcessor):
    """Placeholder for pose estimation processor."""
    
    def initialize(self) -> None:
        """Initialize pose estimator."""
        raise NotImplementedError("PoseEstimator not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with pose estimation."""
        raise NotImplementedError("PoseEstimator not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup pose estimator resources."""
        raise NotImplementedError("PoseEstimator not implemented in this phase")


class BehaviorRecognizer(BaseProcessor):
    """Placeholder for behavior recognition processor."""
    
    def initialize(self) -> None:
        """Initialize behavior recognizer."""
        raise NotImplementedError("BehaviorRecognizer not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with behavior recognition."""
        raise NotImplementedError("BehaviorRecognizer not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup behavior recognizer resources."""
        raise NotImplementedError("BehaviorRecognizer not implemented in this phase")


class FusionProcessor(BaseProcessor):
    """Placeholder for feature fusion processor."""
    
    def initialize(self) -> None:
        """Initialize fusion processor."""
        raise NotImplementedError("FusionProcessor not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with feature fusion."""
        raise NotImplementedError("FusionProcessor not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup fusion processor resources."""
        raise NotImplementedError("FusionProcessor not implemented in this phase")


class TemporalSmoother(BaseProcessor):
    """Placeholder for temporal smoothing processor."""
    
    def initialize(self) -> None:
        """Initialize temporal smoother."""
        raise NotImplementedError("TemporalSmoother not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with temporal smoothing."""
        raise NotImplementedError("TemporalSmoother not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup temporal smoother resources."""
        raise NotImplementedError("TemporalSmoother not implemented in this phase")


class RuleEngine(BaseProcessor):
    """Placeholder for rule engine processor."""
    
    def initialize(self) -> None:
        """Initialize rule engine."""
        raise NotImplementedError("RuleEngine not implemented in this phase")

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with rule engine."""
        raise NotImplementedError("RuleEngine not implemented in this phase")

    def cleanup(self) -> None:
        """Cleanup rule engine resources."""
        raise NotImplementedError("RuleEngine not implemented in this phase")

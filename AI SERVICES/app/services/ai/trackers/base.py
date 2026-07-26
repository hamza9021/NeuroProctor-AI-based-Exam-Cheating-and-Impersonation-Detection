"""
Base tracker class for AI object tracking.

This module provides the abstract base class for all tracker implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import numpy as np


class BaseTracker(ABC):
    """
    Abstract base class for AI object trackers.

    All tracker implementations (DeepSORT, ByteTrack, etc.) should inherit
    from this class.
    """

    def __init__(self, max_age: int = 30):
        """
        Initialize the tracker.

        Args:
            max_age: Maximum number of frames to keep a track alive
        """
        self.max_age = max_age
        self.tracker = None
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the tracker.

        This method should be implemented by subclasses to set up
        the tracking algorithm.
        """
        pass

    @abstractmethod
    def update(self, detections: Any, frame: np.ndarray) -> Any:
        """
        Update the tracker with new detections.

        Args:
            detections: Detection results from the detector
            frame: Current frame as numpy array

        Returns:
            Updated track information
        """
        pass

    def is_tracker_initialized(self) -> bool:
        """Check if the tracker is initialized."""
        return self.is_initialized

    def reset(self) -> None:
        """Reset the tracker state."""
        if self.tracker is not None:
            self.tracker = None
        self.is_initialized = False

"""
Base processor class for AI video processing.

This module provides the abstract base class for all processor implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import numpy as np


class BaseProcessor(ABC):
    """
    Abstract base class for AI video processors.

    All processor implementations (pose estimation, head pose, etc.) should
    inherit from this class.
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        """
        Initialize the processor.

        Args:
            model_path: Path to the model weights file
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self.is_loaded = False

    @abstractmethod
    def load_model(self) -> None:
        """
        Load the AI model.

        This method should be implemented by subclasses to load
        the specific model weights and prepare for inference.
        """
        pass

    @abstractmethod
    def process(self, frame: np.ndarray) -> Any:
        """
        Process a frame.

        Args:
            frame: Input frame as numpy array (H, W, 3)

        Returns:
            Processing results
        """
        pass

    def is_model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.is_loaded

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.model is not None:
            del self.model
            self.model = None
            self.is_loaded = False

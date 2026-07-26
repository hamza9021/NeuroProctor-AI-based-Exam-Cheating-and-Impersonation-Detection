"""
Base recognition class for AI face recognition.

This module provides the abstract base class for all recognition implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import numpy as np


class BaseRecognition(ABC):
    """
    Abstract base class for AI face recognition.

    All recognition implementations (InsightFace, etc.) should inherit
    from this class.
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        """
        Initialize the recognition system.

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
    def get_embedding(self, face_image: np.ndarray) -> Any:
        """
        Get face embedding from an image.

        Args:
            face_image: Face image as numpy array

        Returns:
            Face embedding vector
        """
        pass

    @abstractmethod
    def compare_embeddings(self, embedding1: Any, embedding2: Any) -> float:
        """
        Compare two face embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1)
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

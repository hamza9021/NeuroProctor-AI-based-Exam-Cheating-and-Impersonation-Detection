"""
Base analyzer class for AI behavior analysis.

This module provides the abstract base class for all analyzer implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import numpy as np


class BaseAnalyzer(ABC):
    """
    Abstract base class for AI behavior analyzers.

    All analyzer implementations (cheating detection, etc.) should inherit
    from this class.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the analyzer.

        Args:
            config: Configuration dictionary for the analyzer
        """
        self.config = config or {}
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the analyzer.

        This method should be implemented by subclasses to set up
        the analysis algorithm.
        """
        pass

    @abstractmethod
    def analyze(self, data: Any) -> Any:
        """
        Analyze data for specific behaviors.

        Args:
            data: Input data (tracks, poses, etc.)

        Returns:
            Analysis results
        """
        pass

    def is_analyzer_initialized(self) -> bool:
        """Check if the analyzer is initialized."""
        return self.is_initialized

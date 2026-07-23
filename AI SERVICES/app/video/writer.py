"""
Video writer module for AI Services.

This module provides a VideoWriter class for writing processed
frames to video files with proper codec and settings.
"""

import cv2
from pathlib import Path
from typing import Optional
import numpy as np

from .metadata import VideoMetadata
from ..config.settings import settings
from ..utils.logger import get_logger


class VideoWriter:
    """Reusable class for writing video files."""

    def __init__(
        self,
        output_path: str,
        metadata: VideoMetadata,
        codec: Optional[str] = None,
    ):
        """
        Initialize video writer.

        Args:
            output_path: Path for output video file
            metadata: VideoMetadata instance from source video
            codec: Optional codec (uses default if not provided)

        Raises:
            ValueError: If output directory cannot be created
        """
        self.logger = get_logger(__name__)
        self.output_path = Path(output_path)
        self.metadata = metadata
        self.codec = codec or settings.DEFAULT_CODEC
        self.writer: Optional[cv2.VideoWriter] = None

        self._create_output_directory()
        self._initialize_writer()

    def _create_output_directory(self) -> None:
        """
        Create output directory if it doesn't exist.

        Raises:
            ValueError: If directory cannot be created
        """
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Output directory created: {self.output_path.parent}")
        except Exception as e:
            raise ValueError(f"Failed to create output directory: {e}")

    def _initialize_writer(self) -> None:
        """
        Initialize video writer with codec and settings.

        Raises:
            RuntimeError: If writer cannot be initialized
        """
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        
        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            self.metadata.fps,
            (self.metadata.width, self.metadata.height),
        )

        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to initialize video writer for: {self.output_path}")

        self.logger.info(f"Video writer initialized: {self.output_path.name}")

    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write a frame to the video file.

        Args:
            frame: Frame to write (numpy array)

        Raises:
            RuntimeError: If writer is not initialized
            ValueError: If frame dimensions don't match video metadata
        """
        if self.writer is None:
            raise RuntimeError("Video writer is not initialized")

        if frame.shape[:2] != (self.metadata.height, self.metadata.width):
            raise ValueError(
                f"Frame dimensions {frame.shape[:2]} do not match "
                f"video dimensions {(self.metadata.height, self.metadata.width)}"
            )

        self.writer.write(frame)

    def release(self) -> None:
        """Release video writer resources."""
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            self.logger.info(f"Video writer released: {self.output_path.name}")

    def get_output_path(self) -> Path:
        """
        Get the output file path.

        Returns:
            Path object of output file
        """
        return self.output_path

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()

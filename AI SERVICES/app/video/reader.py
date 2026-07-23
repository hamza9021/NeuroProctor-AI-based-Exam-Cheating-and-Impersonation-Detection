"""
Video reader module for AI Services.

This module provides a VideoReader class for opening, validating,
and reading video files frame by frame.
"""

import cv2
from pathlib import Path
from typing import Generator, Tuple, Optional
import numpy as np

from .metadata import VideoMetadata
from ..config.settings import settings
from ..utils.logger import get_logger


class VideoReader:
    """Reusable class for reading video files."""

    def __init__(self, video_path: str):
        """
        Initialize video reader.

        Args:
            video_path: Path to the video file

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If file extension is not supported
        """
        self.logger = get_logger(__name__)
        self.video_path = Path(video_path)
        self.cap: Optional[cv2.VideoCapture] = None
        self.metadata: Optional[VideoMetadata] = None

        self._validate_file()
        self._open_video()
        self._extract_metadata()

    def _validate_file(self) -> None:
        """
        Validate video file.

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If file extension is not supported
        """
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")

        if not settings.is_supported_extension(str(self.video_path)):
            raise ValueError(
                f"Unsupported file extension: {self.video_path.suffix}. "
                f"Supported extensions: {settings.SUPPORTED_EXTENSIONS}"
            )

    def _open_video(self) -> None:
        """
        Open video file using OpenCV.

        Raises:
            RuntimeError: If video cannot be opened
        """
        self.cap = cv2.VideoCapture(str(self.video_path))
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video file: {self.video_path}")

        self.logger.info(f"Video opened successfully: {self.video_path.name}")

    def _extract_metadata(self) -> None:
        """Extract video metadata."""
        if self.cap is None:
            raise RuntimeError("Video capture is not initialized")

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        codec = self._get_codec_string()
        
        if fps > 0:
            duration = frame_count / fps
        else:
            duration = 0.0

        self.metadata = VideoMetadata(
            filename=self.video_path.name,
            fps=fps,
            width=width,
            height=height,
            frame_count=frame_count,
            duration=duration,
            codec=codec,
        )

        self.logger.info(f"Metadata extracted: {self.metadata.display()}")

    def _get_codec_string(self) -> str:
        """
        Get codec string from OpenCV.

        Returns:
            Codec fourcc as string
        """
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        return "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    def get_metadata(self) -> VideoMetadata:
        """
        Get video metadata.

        Returns:
            VideoMetadata instance
        """
        if self.metadata is None:
            raise RuntimeError("Metadata not extracted")
        return self.metadata

    def read_frame(self) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        """
        Generator that yields frames sequentially.

        Yields:
            Tuple of (frame_number, timestamp, frame)

        Raises:
            RuntimeError: If video capture is not initialized
        """
        if self.cap is None:
            raise RuntimeError("Video capture is not initialized")

        frame_number = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                if frame is None:
                    self.logger.warning("Reached end of video or corrupted frame")
                break

            timestamp = frame_number / self.metadata.fps if self.metadata.fps > 0 else 0.0
            
            try:
                yield frame_number, timestamp, frame
                frame_number += 1
            except Exception as e:
                self.logger.error(f"Error processing frame {frame_number}: {e}")
                continue

    def release(self) -> None:
        """Release video capture resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("Video capture released")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()

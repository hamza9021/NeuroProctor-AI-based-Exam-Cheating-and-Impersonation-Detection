"""
Video metadata module for AI Services.

This module provides a class to store and display video metadata
including filename, fps, width, height, frame count, duration, and codec.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoMetadata:
    """Data class to store video metadata."""

    filename: str
    fps: float
    width: int
    height: int
    frame_count: int
    duration: float
    codec: str

    def display(self) -> str:
        """
        Format metadata for display.

        Returns:
            Formatted metadata string
        """
        metadata_str = f"""
{'=' * 50}
VIDEO METADATA
{'=' * 50}
Filename:        {self.filename}
FPS:             {self.fps:.2f}
Resolution:      {self.width}x{self.height}
Total Frames:    {self.frame_count}
Duration:        {self.duration:.2f}s
Codec:           {self.codec}
{'=' * 50}
"""
        return metadata_str

    def to_dict(self) -> dict:
        """
        Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        return {
            "filename": self.filename,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "frame_count": self.frame_count,
            "duration": self.duration,
            "codec": self.codec,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VideoMetadata":
        """
        Create VideoMetadata instance from dictionary.

        Args:
            data: Dictionary containing metadata

        Returns:
            VideoMetadata instance
        """
        return cls(
            filename=data.get("filename", ""),
            fps=data.get("fps", 0.0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            frame_count=data.get("frame_count", 0),
            duration=data.get("duration", 0.0),
            codec=data.get("codec", ""),
        )

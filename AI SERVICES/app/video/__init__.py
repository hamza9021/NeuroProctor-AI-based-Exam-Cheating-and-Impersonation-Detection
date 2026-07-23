"""
Video module for reading and writing video files.
"""

from .reader import VideoReader
from .writer import VideoWriter
from .metadata import VideoMetadata

__all__ = ["VideoReader", "VideoWriter", "VideoMetadata"]

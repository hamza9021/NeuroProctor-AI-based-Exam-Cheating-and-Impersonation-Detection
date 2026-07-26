"""Frame extractor for video processing."""

import cv2
import logging
from pathlib import Path
from typing import Iterator, Tuple

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extracts frames from video files."""
    
    def __init__(self, video_path: Path):
        """Initialize frame extractor.
        
        Args:
            video_path: Path to video file.
        """
        self._video_path = video_path
        self._cap = None
    
    def extract_frames(self) -> Iterator[Tuple[int, any]]:
        """Extract frames from video.
        
        Yields:
            Tuple of (frame_number, frame) for each frame.
        """
        self._cap = cv2.VideoCapture(str(self._video_path))
        
        if not self._cap.isOpened():
            raise ValueError(f"Failed to open video: {self._video_path}")
        
        frame_number = 0
        
        try:
            while True:
                ret, frame = self._cap.read()
                if not ret:
                    break
                
                yield frame_number, frame
                frame_number += 1
                
        finally:
            self.close()
    
    def get_frame_count(self) -> int:
        """Get total number of frames in video.
        
        Returns:
            Total frame count.
        """
        if self._cap is None:
            self._cap = cv2.VideoCapture(str(self._video_path))
        
        return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def get_fps(self) -> float:
        """Get video frame rate.
        
        Returns:
            Frames per second.
        """
        if self._cap is None:
            self._cap = cv2.VideoCapture(str(self._video_path))
        
        return self._cap.get(cv2.CAP_PROP_FPS)
    
    def close(self):
        """Close video capture."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

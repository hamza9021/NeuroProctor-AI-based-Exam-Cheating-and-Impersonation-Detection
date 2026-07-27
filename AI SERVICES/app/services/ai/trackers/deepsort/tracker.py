"""DeepSORT tracker wrapper."""

import logging
from typing import List, Tuple

import numpy as np

from app.services.ai.trackers.deepsort.config import DeepSORTConfig
from app.services.ai.trackers.deepsort.exceptions import DeepSortTrackingError

logger = logging.getLogger(__name__)


class Tracker:
    """Wrapper for DeepSORT tracking operations.
    
    Responsibilities:
    - Receive validated person detections
    - Call the DeepSORT tracker
    - Pass the current frame when required for appearance embeddings
    - Return raw DeepSORT tracks
    
    Does not:
    - Parse raw tracks
    - Map tracks into FrameContext
    - Draw annotations
    - Add Socket.IO orchestration logic
    """
    
    def __init__(self, tracker, config: DeepSORTConfig):
        """Initialize tracker wrapper.
        
        Args:
            tracker: DeepSORT tracker instance.
            config: DeepSORT configuration.
        """
        self._tracker = tracker
        self._config = config
    
    def update(self, frame: np.ndarray, detections: List[Tuple]) -> List:
        """Update tracker with new detections.
        
        Args:
            frame: Current frame as numpy array (not used by centroid tracker).
            detections: List of detections as (bbox, confidence, class_id).
            
        Returns:
            List of active tracks from centroid tracker.
            
        Raises:
            DeepSortTrackingError: If tracking operation fails.
        """
        try:
            # Convert detections to format expected by centroid tracker
            bboxes = []
            
            for bbox, conf, _ in detections:
                bboxes.append(bbox)
            
            if not bboxes:
                return []
            
            # Update tracker (centroid tracker takes bboxes directly)
            tracks = self._tracker.update(bboxes)
            
            return tracks
            
        except Exception as e:
            raise DeepSortTrackingError(f"Tracking update failed: {e}") from e

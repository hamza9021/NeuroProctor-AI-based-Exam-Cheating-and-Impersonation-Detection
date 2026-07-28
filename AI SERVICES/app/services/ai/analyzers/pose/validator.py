"""Validator for pose candidates."""

import logging
import math
from typing import List

from app.services.ai.analyzers.pose.config import YoloPoseConfig

logger = logging.getLogger(__name__)


class PoseValidator:
    """Validates pose candidates."""
    
    def __init__(self, config: YoloPoseConfig):
        """Initialize validator with configuration.
        
        Args:
            config: Pose configuration.
        """
        self._config = config
    
    def validate(self, candidates: List[dict], frame_width: int, frame_height: int) -> List[dict]:
        """Validate pose candidates.
        
        Args:
            candidates: List of pose candidates.
            frame_width: Frame width for boundary checking.
            frame_height: Frame height for boundary checking.
            
        Returns:
            List of valid pose candidates.
        """
        valid = []
        
        for candidate in candidates:
            if self._is_valid_candidate(candidate, frame_width, frame_height):
                valid.append(candidate)
        
        return valid
    
    def _is_valid_candidate(self, candidate: dict, frame_width: int, frame_height: int) -> bool:
        """Check if a pose candidate is valid.
        
        Args:
            candidate: Pose candidate to validate.
            frame_width: Frame width.
            frame_height: Frame height.
            
        Returns:
            True if valid, False otherwise.
        """
        # Check confidence
        if candidate['confidence'] < self._config.confidence:
            return False
        
        # Check bounding box
        bbox = candidate['bbox']
        if len(bbox) != 4:
            return False
        
        x1, y1, x2, y2 = bbox
        
        # Check coordinates are finite
        if not all(math.isfinite(coord) for coord in bbox):
            return False
        
        # Check coordinates are positive
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            return False
        
        # Check x2 > x1 and y2 > y1
        if x2 <= x1 or y2 <= y1:
            return False
        
        # Check keypoints
        keypoints = candidate['keypoints']
        keypoint_confidences = candidate['keypoint_confidences']
        
        if len(keypoints) != 17 or len(keypoint_confidences) != 17:
            return False
        
        # Count visible keypoints
        visible_count = sum(1 for conf in keypoint_confidences if conf >= self._config.keypoint_confidence)
        
        # Require at least 5 visible keypoints
        if visible_count < 5:
            return False
        
        return True

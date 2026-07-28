"""Annotator for pose skeleton visualization."""

import cv2
import logging
from typing import List

import numpy as np

from app.services.ai.analyzers.pose.constants import SKELETON_CONNECTIONS
from app.services.ai.analyzers.pose.pose import PoseResult

logger = logging.getLogger(__name__)


class PoseAnnotator:
    """Draws pose skeletons on frames."""
    
    def __init__(self, keypoint_confidence: float = 0.25):
        """Initialize annotator.
        
        Args:
            keypoint_confidence: Minimum confidence to draw keypoint.
        """
        self._keypoint_confidence = keypoint_confidence
    
    def annotate(self, frame: np.ndarray, poses: List[PoseResult]) -> np.ndarray:
        """Draw pose skeletons on frame.
        
        Args:
            frame: Input frame.
            poses: List of PoseResult to draw.
            
        Returns:
            Annotated frame.
        """
        annotated = frame.copy()
        frame_height, frame_width = frame.shape[:2]
        
        logger.info(f"Annotator received {len(poses)} poses to draw")
        
        for pose in poses:
            if not pose.is_valid:
                logger.warning(f"Skipping invalid pose for track {pose.track_id}")
                continue
            
            logger.info(f"Drawing skeleton for track {pose.track_id}")
            self._draw_skeleton(annotated, pose, frame_width, frame_height)
        
        logger.info(f"Annotator completed drawing")
        return annotated
    
    def _draw_skeleton(self, frame: np.ndarray, pose: PoseResult, frame_width: int, frame_height: int):
        """Draw skeleton connections and keypoints.
        
        Args:
            frame: Frame to draw on.
            pose: PoseResult to draw.
            frame_width: Frame width for clipping.
            frame_height: Frame height for clipping.
        """
        keypoints = pose.keypoints
        confidences = pose.keypoint_confidences
        
        # Draw skeleton connections
        for idx1, idx2 in SKELETON_CONNECTIONS:
            if idx1 >= len(keypoints) or idx2 >= len(keypoints):
                continue
            
            kp1 = keypoints[idx1]
            kp2 = keypoints[idx2]
            conf1 = confidences[idx1]
            conf2 = confidences[idx2]
            
            if conf1 < self._keypoint_confidence or conf2 < self._keypoint_confidence:
                continue
            
            x1, y1 = int(kp1[0]), int(kp1[1])
            x2, y2 = int(kp2[0]), int(kp2[1])
            
            # Clip to frame boundaries
            x1 = max(0, min(x1, frame_width - 1))
            y1 = max(0, min(y1, frame_height - 1))
            x2 = max(0, min(x2, frame_width - 1))
            y2 = max(0, min(y2, frame_height - 1))
            
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        
        # Draw keypoints
        for i, (kp, conf) in enumerate(zip(keypoints, confidences)):
            if conf < self._keypoint_confidence:
                continue
            
            x, y = int(kp[0]), int(kp[1])
            
            # Clip to frame boundaries
            x = max(0, min(x, frame_width - 1))
            y = max(0, min(y, frame_height - 1))
            
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

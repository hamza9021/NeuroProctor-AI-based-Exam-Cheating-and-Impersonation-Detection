"""Track-to-pose association using IoU matching."""

import logging
from typing import List

from app.services.ai.analyzers.pose.config import YoloPoseConfig
from app.services.ai.analyzers.pose.iou_calculator import IoUCalculator
from app.services.ai.analyzers.pose.pose import PoseResult

logger = logging.getLogger(__name__)


class PoseAssociator:
    """Associates pose candidates with DeepSORT tracks using IoU."""
    
    def __init__(self, config: YoloPoseConfig):
        """Initialize associator with configuration.
        
        Args:
            config: Pose configuration.
        """
        self._config = config
        self._iou_calculator = IoUCalculator()
    
    def associate(self, tracks: List, pose_candidates: List[dict]) -> List[PoseResult]:
        """Associate pose candidates with tracks.
        
        Args:
            tracks: List of Track objects from DeepSORT.
            pose_candidates: List of validated pose candidates.
            
        Returns:
            List of PoseResult with associated track IDs.
        """
        results = []
        
        if not tracks or not pose_candidates:
            return results
        
        # Filter to confirmed and recently updated tracks
        eligible_tracks = [
            t for t in tracks
            if t.is_confirmed and t.time_since_update < 10
        ]
        
        if not eligible_tracks:
            return results
        
        # Calculate IoU matrix
        iou_matrix = self._iou_calculator.calculate_matrix(eligible_tracks, pose_candidates)
        
        # Greedy matching by descending IoU
        matched_tracks = set()
        matched_poses = set()
        
        for _ in range(min(len(eligible_tracks), len(pose_candidates))):
            max_iou = 0
            best_track_idx = -1
            best_pose_idx = -1
            
            for i, track in enumerate(eligible_tracks):
                if i in matched_tracks:
                    continue
                for j, _ in enumerate(pose_candidates):
                    if j in matched_poses:
                        continue
                    if iou_matrix[i][j] > max_iou:
                        max_iou = iou_matrix[i][j]
                        best_track_idx = i
                        best_pose_idx = j
            
            if max_iou >= self._config.track_iou_threshold:
                track = eligible_tracks[best_track_idx]
                pose = pose_candidates[best_pose_idx]
                
                results.append(PoseResult(
                    track_id=track.track_id,
                    bbox=tuple(pose['bbox']),
                    keypoints=[(kp[0], kp[1]) for kp in pose['keypoints']],
                    keypoint_confidences=pose['keypoint_confidences'],
                    confidence=pose['confidence'],
                    is_valid=True,
                    visible_keypoints=sum(1 for c in pose['keypoint_confidences'] if c >= self._config.keypoint_confidence),
                ))
                
                matched_tracks.add(best_track_idx)
                matched_poses.add(best_pose_idx)
        
        return results

"""Mapper for DeepSORT tracking results."""

import logging
from typing import List, Tuple

from app.services.ai.pipeline.context import Detection
from app.services.ai.trackers.deepsort.track import Track

logger = logging.getLogger(__name__)


class TrackMapper:
    """Maps tracker output and links detections to tracks.
    
    Updates the existing shared context.
    Stores parsed tracking results in context.tracks.
    Links person detections to matching Track IDs.
    """
    
    def map_detections_to_tracks(
        self,
        detections: List[Detection],
        tracks: List[Track],
    ) -> Tuple[List[Detection], List[Track]]:
        """Map detections to tracks based on IOU.
        
        Args:
            detections: List of YOLO detections.
            tracks: List of DeepSORT tracks.
            
        Returns:
            Tuple of (updated detections, tracks).
        """
        # Link detections to tracks by IOU matching
        for track in tracks:
            best_detection = self._find_best_detection(track, detections)
            if best_detection:
                best_detection.track_id = track.track_id
        
        return detections, tracks
    
    def _find_best_detection(
        self,
        track: Track,
        detections: List[Detection],
    ) -> Detection:
        """Find the best matching detection for a track.
        
        Args:
            track: Track to match.
            detections: List of detections.
            
        Returns:
            Best matching detection or None.
        """
        best_detection = None
        best_iou = 0.0
        
        for detection in detections:
            if detection.class_name != "person":
                continue
            
            iou = self._calculate_iou(track.bbox, detection.bbox)
            if iou > best_iou and iou > 0.5:
                best_iou = iou
                best_detection = detection
        
        return best_detection
    
    def _calculate_iou(self, bbox1: tuple, bbox2: tuple) -> float:
        """Calculate Intersection over Union (IOU).
        
        Args:
            bbox1: First bounding box (x1, y1, x2, y2).
            bbox2: Second bounding box (x1, y1, x2, y2).
            
        Returns:
            IOU score between 0 and 1.
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union

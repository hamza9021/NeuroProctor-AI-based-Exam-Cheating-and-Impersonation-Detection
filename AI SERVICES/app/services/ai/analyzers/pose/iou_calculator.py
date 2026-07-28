"""IoU calculator for bounding box overlap."""

import logging
from typing import List

logger = logging.getLogger(__name__)


class IoUCalculator:
    """Calculates IoU between bounding boxes."""
    
    def calculate_matrix(self, tracks: List, pose_candidates: List[dict]) -> List[List[float]]:
        """Calculate IoU matrix between tracks and poses.
        
        Args:
            tracks: List of Track objects.
            pose_candidates: List of pose candidates.
            
        Returns:
            IoU matrix as list of lists.
        """
        matrix = []
        
        for track in tracks:
            row = []
            track_bbox = track.bbox
            
            for pose in pose_candidates:
                pose_bbox = pose['bbox']
                iou = self.calculate_iou(track_bbox, pose_bbox)
                row.append(iou)
            
            matrix.append(row)
        
        return matrix
    
    def calculate_iou(self, bbox1: tuple, bbox2: List) -> float:
        """Calculate IoU between two bounding boxes.
        
        Args:
            bbox1: First bounding box [x1, y1, x2, y2].
            bbox2: Second bounding box [x1, y1, x2, y2].
            
        Returns:
            IoU value between 0 and 1.
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
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = area1 + area2 - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area

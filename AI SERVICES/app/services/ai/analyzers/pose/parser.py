"""Parser for YOLO pose results."""

import logging
from typing import List, Tuple

from app.services.ai.analyzers.pose.exceptions import PoseParsingError

logger = logging.getLogger(__name__)


class PoseParser:
    """Parses raw YOLO pose results into pose candidates."""
    
    def parse(self, raw_results: list) -> List[dict]:
        """Parse raw YOLO pose results.
        
        Args:
            raw_results: Raw results from YOLO pose model.
            
        Returns:
            List of pose candidate dictionaries.
            
        Raises:
            PoseParsingError: If parsing fails.
        """
        candidates = []
        
        try:
            for result in raw_results:
                if not hasattr(result, 'keypoints') or result.keypoints is None:
                    continue
                
                keypoints_data = result.keypoints.xy.cpu().numpy()
                conf_data = result.keypoints.conf.cpu().numpy()
                
                for i in range(len(keypoints_data)):
                    keypoints = keypoints_data[i]
                    confidences = conf_data[i]
                    
                    # Get bounding box
                    if hasattr(result, 'boxes') and result.boxes is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        bbox = boxes[i].tolist()
                        confidence = result.boxes.conf.cpu().numpy()[i]
                    else:
                        continue
                    
                    candidates.append({
                        'bbox': bbox,
                        'keypoints': keypoints.tolist(),
                        'keypoint_confidences': confidences.tolist(),
                        'confidence': float(confidence),
                    })
            
            return candidates
            
        except Exception as e:
            raise PoseParsingError(f"Failed to parse pose results: {e}") from e

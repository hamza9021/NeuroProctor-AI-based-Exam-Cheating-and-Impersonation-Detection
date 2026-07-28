"""YOLO detection validator."""

import logging

from app.services.ai.detectors.yolo.constants import MIN_BBOX_AREA, MAX_BBOX_AREA
from app.services.ai.detectors.yolo.mapper import ClassMapper
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.pipeline.context import Detection

logger = logging.getLogger(__name__)


class DetectionValidator:
    """Validates detection results with class-specific confidence thresholds."""
    
    def __init__(self, mapper: ClassMapper, config: YOLOConfig):
        """Initialize validator with class mapper and config.
        
        Args:
            mapper: Class ID to name mapper.
            config: YOLO configuration with class-specific thresholds.
        """
        self._mapper = mapper
        self._config = config
    
    def validate(self, detection: Detection) -> bool:
        """Validate a single detection.
        
        Args:
            detection: Detection to validate.
            
        Returns:
            True if detection is valid.
        """
        # Check class-specific confidence threshold
        class_confidence = self._config.get_class_confidence(detection.class_name)
        if detection.confidence < class_confidence:
            return False
        
        # Check if class is in target classes
        if not self._mapper.is_target_class(detection.class_id):
            return False
        
        # Check bounding box validity
        if not self._is_valid_bbox(detection):
            return False
        
        return True
    
    def _is_valid_bbox(self, detection: Detection) -> bool:
        """Check if bounding box is valid.
        
        Args:
            detection: Detection to check.
            
        Returns:
            True if bounding box is valid.
        """
        # Check bbox has 4 coordinates
        if len(detection.bbox) != 4:
            return False
        
        # Check coordinates are valid
        x1, y1, x2, y2 = detection.bbox
        if x2 <= x1 or y2 <= y1:
            return False
        
        # Use class-specific minimum area for phones
        min_area = MIN_BBOX_AREA
        if detection.class_name == "cell phone":
            # Allow smaller boxes for phones
            min_area = 10
        
        # Check area is within bounds
        area = detection.width * detection.height
        if area < min_area or area > MAX_BBOX_AREA:
            return False
        
        return True
    
    def filter(self, detections: list[Detection]) -> list[Detection]:
        """Filter list of detections.
        
        Args:
            detections: List of detections to filter.
            
        Returns:
            List of valid detections.
        """
        valid = [d for d in detections if self.validate(d)]
        logger.debug(f"Filtered {len(detections)} detections to {len(valid)} valid")
        return valid

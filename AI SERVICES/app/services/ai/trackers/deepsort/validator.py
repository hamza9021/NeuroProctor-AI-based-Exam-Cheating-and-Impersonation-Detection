"""Validator for DeepSORT detections."""

import logging
from typing import List, Tuple

from app.services.ai.pipeline.context import Detection
from app.services.ai.trackers.deepsort.constants import (
    MAX_BBOX_AREA,
    MIN_BBOX_AREA,
    TARGET_CLASS,
)
from app.services.ai.trackers.deepsort.exceptions import InvalidTrackingDetectionError

logger = logging.getLogger(__name__)


class DetectionValidator:
    """Validates and filters detections for tracking.
    
    Responsibilities:
    - Read detections from context.detections
    - Keep only person detections for tracking
    - Validate bounding boxes
    - Validate confidence values
    - Reject malformed detections
    - Return validated detections in format required by DeepSORT
    
    Preserves non-person detections (like phones) in the context for later processing.
    """
    
    def validate(
        self,
        detections: List[Detection],
        confidence_threshold: float,
    ) -> Tuple[List[Detection], dict]:
        """Validate and filter person detections.
        
        Args:
            detections: All detections from YOLO.
            confidence_threshold: Minimum confidence threshold.
            
        Returns:
            Tuple of (validated detections, statistics dict).
            
        Raises:
            InvalidTrackingDetectionError: If detection is invalid.
        """
        person_detections = []
        stats = {
            "total_detections": len(detections),
            "valid_person_detections": 0,
            "invalid_person_detections": 0,
            "non_person_detections": 0,
        }
        
        for det in detections:
            if det.class_name != TARGET_CLASS:
                stats["non_person_detections"] += 1
                continue
            
            validation_result = self._is_valid_detection(det, confidence_threshold)
            if validation_result is True:
                person_detections.append(det)
                stats["valid_person_detections"] += 1
            else:
                stats["invalid_person_detections"] += 1
                logger.warning(f"Invalid person detection filtered: {validation_result}")
        
        logger.debug(f"Validated {len(person_detections)} person detections")
        return person_detections, stats
    
    def _is_valid_detection(
        self,
        detection: Detection,
        confidence_threshold: float,
    ) -> bool | str:
        """Check if a detection is valid for tracking.
        
        Args:
            detection: Detection to validate.
            confidence_threshold: Minimum confidence.
            
        Returns:
            True if detection is valid, or error reason string if invalid.
        """
        # Check confidence
        if detection.confidence < confidence_threshold:
            return f"confidence {detection.confidence:.2f} below threshold {confidence_threshold}"
        
        # Check bounding box
        bbox_result = self._is_valid_bbox(detection.bbox)
        if bbox_result is not True:
            return bbox_result
        
        # Check center point
        if not detection.center:
            return "center point missing"
        if len(detection.center) != 2:
            return f"center point has {len(detection.center)} coordinates, expected 2"
        
        return True
    
    def _is_valid_bbox(self, bbox: List[float]) -> bool | str:
        """Check if bounding box is valid.
        
        Args:
            bbox: Bounding box as [x1, y1, x2, y2].
            
        Returns:
            True if bbox is valid, or error reason string if invalid.
        """
        if len(bbox) != 4:
            return f"bbox has {len(bbox)} coordinates, expected 4"
        
        x1, y1, x2, y2 = bbox
        
        # Check coordinates are finite
        import math
        if not all(math.isfinite(coord) for coord in bbox):
            return "bbox contains non-finite values"
        
        # Check coordinates are positive
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            return "bbox contains negative coordinates"
        
        # Check x2 > x1 and y2 > y1
        if x2 <= x1:
            return f"bbox width must be positive (x2={x2} <= x1={x1})"
        if y2 <= y1:
            return f"bbox height must be positive (y2={y2} <= y1={y1})"
        
        # Check area constraints
        width = x2 - x1
        height = y2 - y1
        area = width * height
        
        if area < MIN_BBOX_AREA:
            return f"bbox area {area:.0f} below minimum {MIN_BBOX_AREA}"
        if area > MAX_BBOX_AREA:
            return f"bbox area {area:.0f} exceeds maximum {MAX_BBOX_AREA}"
        
        return True

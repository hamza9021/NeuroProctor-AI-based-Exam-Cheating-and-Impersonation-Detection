"""YOLO result parser."""

import logging
import numpy as np
from ultralytics import YOLO

from app.services.ai.pipeline.context import Detection
from app.services.ai.detectors.yolo.mapper import ClassMapper

logger = logging.getLogger(__name__)


class ResultParser:
    """Parses YOLO results into Detection objects."""
    
    def __init__(self, mapper: ClassMapper):
        """Initialize parser with class mapper.
        
        Args:
            mapper: Class ID to name mapper.
        """
        self._mapper = mapper
    
    def parse(self, results) -> list[Detection]:
        """Parse YOLO results into Detection objects.
        
        Args:
            results: Raw YOLO detection results.
            
        Returns:
            List of Detection objects.
        """
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for box in boxes:
                detection = self._parse_box(box)
                if detection:
                    detections.append(detection)
        
        return detections
    
    def _parse_box(self, box) -> Detection:
        """Parse single bounding box.
        
        Args:
            box: YOLO box object.
            
        Returns:
            Detection object or None if invalid.
        """
        class_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())
        
        # Get bounding box coordinates
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        # Calculate center, width, height
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        
        class_name = self._mapper.get_class_name(class_id)
        
        return Detection(
            class_name=class_name,
            class_id=class_id,
            confidence=confidence,
            bbox=[x1, y1, x2, y2],
            center=[center_x, center_y],
            width=width,
            height=height,
        )

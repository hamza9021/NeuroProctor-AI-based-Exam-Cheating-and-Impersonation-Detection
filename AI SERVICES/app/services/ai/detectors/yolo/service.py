"""YOLO detection service."""

import logging

from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.detectors.yolo.loader import ModelLoader
from app.services.ai.detectors.yolo.detector import Detector
from app.services.ai.detectors.yolo.parser import ResultParser
from app.services.ai.detectors.yolo.validator import DetectionValidator
from app.services.ai.detectors.yolo.mapper import ClassMapper
from app.services.ai.pipeline.context import FrameContext, Detection

logger = logging.getLogger(__name__)


class YOLODetectionService:
    """Service for YOLO object detection."""
    
    def __init__(self, config: YOLOConfig):
        """Initialize detection service.
        
        Args:
            config: YOLO configuration.
        """
        self._config = config
        self._model = None
        self._mapper = ClassMapper()
        self._detector = None
        self._parser = ResultParser(self._mapper)
        self._validator = DetectionValidator(self._mapper)
    
    def initialize(self):
        """Load YOLO model and initialize detector."""
        loader = ModelLoader(self._config)
        self._model = loader.load()
        self._detector = Detector(self._model, self._config)
        logger.info("YOLO detection service initialized")
    
    def detect(self, context: FrameContext) -> FrameContext:
        """Run detection on frame context.
        
        Args:
            context: Frame context with frame to process.
            
        Returns:
            Updated frame context with detections.
        """
        if self._detector is None:
            self.initialize()
        
        logger.debug(f"Processing frame {context.frame_number}")
        
        # Run detection
        results = self._detector.detect(context.frame)
        
        # Parse results
        detections = self._parser.parse(results)
        
        # Validate detections
        valid_detections = self._validator.filter(detections)
        
        # Log detection summary
        self._log_detections(valid_detections)
        
        # Update context
        context.detections = valid_detections
        
        return context
    
    def _log_detections(self, detections: list[Detection]):
        """Log detection summary.
        
        Args:
            detections: List of valid detections.
        """
        class_counts = {}
        for det in detections:
            class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1
        
        if class_counts:
            logger.info(f"Detected: {class_counts}")

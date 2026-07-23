"""
Object Detection Processor module.

This module provides a processor that integrates YOLO object detection
with the video processing pipeline.
"""

import numpy as np
from typing import Optional, List

from app.processors.base_processor import BaseProcessor
from app.detectors.object_detector import ObjectDetector
from app.detectors.detection import FrameDetections
from app.config.settings import settings
from app.utils.logger import get_logger


class ObjectDetectionProcessor(BaseProcessor):
    """Processor for YOLO object detection in video frames."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize object detection processor.

        Args:
            model_path: Path to YOLO model file (uses settings default if not provided)
            confidence_threshold: Confidence threshold for detections (uses settings default if not provided)
            iou_threshold: IoU threshold for NMS (uses settings default if not provided)
            device: Device to run inference on (uses settings default if not provided)
        """
        super().__init__("ObjectDetectionProcessor")
        
        self.logger = get_logger(__name__)
        
        self.detector = ObjectDetector(
            model_path=model_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            device=device,
        )
        
        self.current_frame_number: int = 0
        self.current_timestamp: float = 0.0
        self.last_detections: Optional[FrameDetections] = None
        self.all_detections: List[FrameDetections] = []

    def initialize(self) -> None:
        """Initialize the object detector (load model)."""
        try:
            self.detector.load_model()
            self.logger.info(f"ObjectDetectionProcessor initialized with device: {self.detector.get_device()}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ObjectDetectionProcessor: {e}")
            raise

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with object detection.

        Args:
            frame: Input frame as numpy array

        Returns:
            Annotated frame with detections drawn
        """
        # Detect objects in frame
        detections = self.detector.detect(
            frame=frame,
            frame_number=self.current_frame_number,
            timestamp=self.current_timestamp,
        )

        # Store detections
        self.last_detections = detections
        self.all_detections.append(detections)

        # Draw detections on frame
        annotated_frame = self.detector.draw_detections(frame, detections)

        # Log detection summary periodically
        if self.current_frame_number % 100 == 0:
            class_counts = detections.get_class_counts()
            total_objects = len(detections.detections)
            self.logger.info(
                f"Frame {self.current_frame_number}: "
                f"Total objects: {total_objects}, "
                f"Class counts: {class_counts}, "
                f"Inference: {detections.inference_time_ms:.2f}ms"
            )

        return annotated_frame

    def cleanup(self) -> None:
        """Clean up detector resources."""
        self.detector.cleanup()
        self.logger.info("ObjectDetectionProcessor cleaned up")

    def set_frame_context(self, frame_number: int, timestamp: float) -> None:
        """
        Set frame context for processing.

        Args:
            frame_number: Current frame number
            timestamp: Current frame timestamp
        """
        self.current_frame_number = frame_number
        self.current_timestamp = timestamp

    def get_last_detections(self) -> Optional[FrameDetections]:
        """
        Get detections from the last processed frame.

        Returns:
            FrameDetections object or None if no frame processed yet
        """
        return self.last_detections

    def get_all_detections(self) -> List[FrameDetections]:
        """
        Get all detections from processed frames.

        Returns:
            List of FrameDetections objects
        """
        return self.all_detections

    def clear_detections_history(self) -> None:
        """Clear the history of all detections."""
        self.all_detections.clear()
        self.last_detections = None

"""
Object Detector module using YOLO.

This module provides an ObjectDetector class that uses Ultralytics YOLO
for real-time object detection in video frames.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import time

from ultralytics import YOLO

from app.detectors.detection import Detection, FrameDetections
from app.config.settings import settings
from app.utils.logger import get_logger


class ObjectDetector:
    """YOLO-based object detector for exam monitoring."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize object detector.

        Args:
            model_path: Path to YOLO model file (uses settings default if not provided)
            confidence_threshold: Confidence threshold for detections (uses settings default if not provided)
            iou_threshold: IoU threshold for NMS (uses settings default if not provided)
            device: Device to run inference on (uses settings default if not provided)
        """
        self.logger = get_logger(__name__)
        self.model_path = Path(model_path) if model_path else settings.MODEL_PATH
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else settings.CONFIDENCE_THRESHOLD
        self.iou_threshold = iou_threshold if iou_threshold is not None else settings.IOU_THRESHOLD
        self.device = device if device else settings.DEVICE
        self.allowed_classes = settings.ALLOWED_CLASSES
        self.class_colors = settings.CLASS_COLORS

        self.model: Optional[YOLO] = None
        self.is_loaded = False

    def load_model(self) -> None:
        """
        Load YOLO model.

        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        if self.is_loaded:
            self.logger.warning("Model already loaded, skipping")
            return

        try:
            # Check if model file exists
            if not self.model_path.exists():
                self.logger.warning(f"Model file not found at {self.model_path}, downloading from Ultralytics...")
                # Ultralytics will auto-download if model name is provided
                self.model = YOLO(settings.MODEL_NAME)
            else:
                self.model = YOLO(str(self.model_path))

            # Set device
            if self.device == "auto":
                self.model.to("cuda" if self.model.device.type == "cuda" else "cpu")
            else:
                self.model.to(self.device)

            self.is_loaded = True
            self.logger.info(f"YOLO model loaded successfully from {self.model_path}")
            self.logger.info(f"Using device: {self.model.device}")

        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(f"Failed to load YOLO model: {e}")

    def detect(
        self,
        frame: np.ndarray,
        frame_number: int = 0,
        timestamp: float = 0.0,
    ) -> FrameDetections:
        """
        Detect objects in a frame.

        Args:
            frame: Input frame as numpy array
            frame_number: Frame number for logging
            timestamp: Frame timestamp

        Returns:
            FrameDetections object containing all detections

        Raises:
            RuntimeError: If model is not loaded
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        start_time = time.time()

        # Run inference
        results = self.model(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False,
        )

        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Process results
        detections = []

        if len(results) > 0:
            result = results[0]
            boxes = result.boxes

            if boxes is not None:
                for box in boxes:
                    # Get class name
                    class_id = int(box.cls[0])
                    class_name = self.model.names.get(class_id, "unknown")

                    # Filter by allowed classes
                    if class_name not in self.allowed_classes:
                        continue

                    # Get confidence
                    confidence = float(box.conf[0])

                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Calculate center point
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2

                    # Create detection
                    detection = Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bounding_box=(x1, y1, x2, y2),
                        center_point=(center_x, center_y),
                    )
                    detections.append(detection)

        # Create frame detections
        frame_detections = FrameDetections(
            frame_number=frame_number,
            timestamp=timestamp,
            detections=detections,
            inference_time_ms=inference_time,
        )

        # Log detection summary
        class_counts = frame_detections.get_class_counts()
        if class_counts:
            self.logger.debug(
                f"Frame {frame_number}: {class_counts}, Inference: {inference_time:.2f}ms"
            )

        return frame_detections

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: FrameDetections,
    ) -> np.ndarray:
        """
        Draw detection results on frame.

        Args:
            frame: Input frame
            detections: FrameDetections object

        Returns:
            Frame with drawn detections
        """
        annotated_frame = frame.copy()

        for detection in detections.detections:
            class_name = detection.class_name
            confidence = detection.confidence
            x1, y1, x2, y2 = detection.bounding_box

            # Get color for class
            color = self.class_colors.get(class_name, (0, 255, 0))

            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Create label
            label = f"{class_name} {confidence:.0%}"

            # Get label size
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )

            # Draw label background
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - label_height - baseline - 5),
                (x1 + label_width, y1),
                color,
                -1,
            )

            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - baseline - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return annotated_frame

    def get_device(self) -> str:
        """
        Get the device being used for inference.

        Returns:
            Device string
        """
        if self.model is None:
            return "not loaded"
        return str(self.model.device)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.model is not None:
            del self.model
            self.model = None
            self.is_loaded = False
            self.logger.info("Object detector cleaned up")

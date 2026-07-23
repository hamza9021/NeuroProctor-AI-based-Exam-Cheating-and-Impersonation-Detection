"""
Pose Processor module.

This module provides a processor that integrates YOLO pose estimation
with the video processing pipeline.
"""

import numpy as np
from typing import Optional, List

from app.processors.base_processor import BaseProcessor
from app.pose.pose_estimator import PoseEstimator
from app.pose.pose_result import PoseResult
from app.config.settings import settings
from app.utils.logger import get_logger


class PoseProcessor(BaseProcessor):
    """Processor for YOLO pose estimation in video frames."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize pose processor.

        Args:
            model_path: Path to YOLO pose model file (uses settings default if not provided)
            confidence_threshold: Confidence threshold for detections (uses settings default if not provided)
            iou_threshold: IoU threshold for NMS (uses settings default if not provided)
            device: Device to run inference on (uses settings default if not provided)
        """
        super().__init__("PoseProcessor")
        
        self.logger = get_logger(__name__)
        
        self.estimator = PoseEstimator(
            model_path=model_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            device=device,
        )
        
        self.current_frame_number: int = 0
        self.current_timestamp: float = 0.0
        self.last_pose_result: Optional[PoseResult] = None
        self.all_pose_results: List[PoseResult] = []

    def initialize(self) -> None:
        """Initialize the pose estimator (load model)."""
        try:
            self.estimator.load_model()
            self.logger.info(f"PoseProcessor initialized with device: {self.estimator.get_device()}")
        except Exception as e:
            self.logger.error(f"Failed to initialize PoseProcessor: {e}")
            raise

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with pose estimation.

        Args:
            frame: Input frame as numpy array

        Returns:
            Annotated frame with poses drawn
        """
        # Estimate poses in frame
        pose_result = self.estimator.estimate(
            frame=frame,
            frame_number=self.current_frame_number,
            timestamp=self.current_timestamp,
        )

        # Store pose result
        self.last_pose_result = pose_result
        self.all_pose_results.append(pose_result)

        # Draw poses on frame
        annotated_frame = self.estimator.draw_poses(frame, pose_result)

        # Log detection summary periodically
        if self.current_frame_number % 100 == 0:
            person_count = pose_result.get_person_count()
            self.logger.info(
                f"Frame {self.current_frame_number}: "
                f"Persons: {person_count}, "
                f"Inference: {pose_result.inference_time_ms:.2f}ms"
            )

        return annotated_frame

    def cleanup(self) -> None:
        """Clean up estimator resources."""
        self.estimator.cleanup()
        self.logger.info("PoseProcessor cleaned up")

    def set_frame_context(self, frame_number: int, timestamp: float) -> None:
        """
        Set frame context for processing.

        Args:
            frame_number: Current frame number
            timestamp: Current frame timestamp
        """
        self.current_frame_number = frame_number
        self.current_timestamp = timestamp

    def get_last_pose_result(self) -> Optional[PoseResult]:
        """
        Get pose result from the last processed frame.

        Returns:
            PoseResult object or None if no frame processed yet
        """
        return self.last_pose_result

    def get_all_pose_results(self) -> List[PoseResult]:
        """
        Get all pose results from processed frames.

        Returns:
            List of PoseResult objects
        """
        return self.all_pose_results

    def clear_pose_history(self) -> None:
        """Clear the history of all pose results."""
        self.all_pose_results.clear()
        self.last_pose_result = None

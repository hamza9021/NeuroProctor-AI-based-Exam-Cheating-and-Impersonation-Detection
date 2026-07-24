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
        self.last_frame_tracks = None

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

        # Associate poses with Track IDs if tracking data is available
        if self.last_frame_tracks:
            pose_result = self._associate_poses_with_tracks(pose_result)

        # Store pose result
        self.last_pose_result = pose_result
        self.all_pose_results.append(pose_result)

        # Draw poses on frame
        annotated_frame = self.estimator.draw_poses(frame, pose_result)

        # Log detection summary periodically
        if self.current_frame_number % 100 == 0:
            person_count = pose_result.get_person_count()
            tracked_count = sum(1 for p in pose_result.persons if p.track_id is not None)
            self.logger.info(
                f"Frame {self.current_frame_number}: "
                f"Persons: {person_count}, "
                f"Tracked: {tracked_count}, "
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
    
    def set_frame_tracks(self, frame_tracks) -> None:
        """
        Set frame tracks from tracking processor.
        
        Args:
            frame_tracks: FrameTracks object with track information
        """
        self.last_frame_tracks = frame_tracks
    
    def _associate_poses_with_tracks(self, pose_result) -> PoseResult:
        """
        Associate pose results with Track IDs using IoU matching.
        
        Args:
            pose_result: PoseResult object with person poses
            
        Returns:
            PoseResult with track IDs assigned to poses
        """
        from app.tracking.tracking_utils import calculate_iou
        
        if not self.last_frame_tracks or not self.last_frame_tracks.tracks:
            return pose_result
        
        person_tracks = [t for t in self.last_frame_tracks.tracks if t.class_name == "person" and t.is_active()]
        
        for person_pose in pose_result.persons:
            best_track = None
            best_iou = 0.3  # IoU threshold for matching
            
            for track in person_tracks:
                iou = calculate_iou(person_pose.bounding_box, track.bounding_box)
                if iou > best_iou:
                    best_iou = iou
                    best_track = track
            
            if best_track:
                person_pose.track_id = best_track.track_id
        
        return pose_result

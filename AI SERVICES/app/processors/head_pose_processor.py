"""
Head Pose Estimation Processor.

This processor integrates the 6DRepNet head pose estimation service
into the video processing pipeline, estimating head orientation for
all tracked persons.
"""

import numpy as np
from typing import Optional

from app.processors.base_processor import BaseProcessor
from app.head_pose.service import HeadPoseService
from app.head_pose.schemas import FrameHeadPoses, HeadPoseResult
from app.pose.pose_result import PoseResult
from app.tracking.tracking_models import FrameTracks
from app.utils.logger import get_logger


class HeadPoseProcessor(BaseProcessor):
    """
    Processor for head pose estimation using 6DRepNet.
    
    This processor estimates head orientation (yaw, pitch, roll) for
    all tracked persons in each frame and associates results with Track IDs.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        min_crop_size: int = 64,
        crop_padding: float = 0.3,
        use_keypoints: bool = True,
        confidence_threshold: float = 0.5,
        visualize: bool = True,
    ):
        """
        Initialize the head pose processor.
        
        Args:
            model_path: Path to 6DRepNet model weights (None for pretrained)
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
            min_crop_size: Minimum face crop size in pixels
            crop_padding: Padding ratio around face (0.0 to 1.0)
            use_keypoints: Whether to use pose keypoints for face refinement
            confidence_threshold: Minimum confidence threshold for results
            visualize: Whether to visualize head pose on frame
        """
        super().__init__("HeadPoseProcessor")
        
        self.logger = get_logger(__name__)
        
        self.visualize = visualize
        
        # Try to initialize head pose service
        try:
            self.head_pose_service = HeadPoseService(
                model_path=model_path,
                device=device,
                min_crop_size=min_crop_size,
                crop_padding=crop_padding,
                use_keypoints=use_keypoints,
                confidence_threshold=confidence_threshold,
            )
            self.is_available = self.head_pose_service.is_available
        except Exception as e:
            self.logger.warning(f"Failed to initialize HeadPoseService: {e}")
            self.logger.warning("Head pose estimation will be disabled")
            self.head_pose_service = None
            self.is_available = False
        
        # Frame context
        self.last_frame_tracks: Optional[FrameTracks] = None
        self.last_pose_result: Optional[PoseResult] = None
        self.last_head_poses: Optional[FrameHeadPoses] = None
        
        if self.is_available:
            self.logger.info("HeadPoseProcessor initialized")
        else:
            self.logger.info("HeadPoseProcessor initialized (head pose estimation disabled)")
    
    def initialize(self) -> None:
        """Initialize the head pose processor."""
        # Already initialized in __init__
        pass
    
    def set_frame_tracks(self, frame_tracks: FrameTracks) -> None:
        """
        Set the frame tracks for head pose estimation.
        
        Args:
            frame_tracks: FrameTracks from TrackingProcessor
        """
        self.last_frame_tracks = frame_tracks
    
    def set_pose_result(self, pose_result: PoseResult) -> None:
        """
        Set the pose result for head pose estimation.
        
        Args:
            pose_result: PoseResult from PoseProcessor
        """
        self.last_pose_result = pose_result
    
    def process(self, frame: np.ndarray, frame_number: int = 0, timestamp: float = 0.0) -> np.ndarray:
        """
        Process a frame to estimate head poses.
        
        Args:
            frame: Input frame (H, W, 3)
            frame_number: Frame number in the video
            timestamp: Timestamp in seconds
            
        Returns:
            Frame with optional visualization
        """
        if not self.is_available or self.head_pose_service is None:
            # Return frame unchanged if head pose estimation is not available
            return frame
        
        if self.last_frame_tracks is None:
            self.logger.warning("No frame tracks available, skipping head pose estimation")
            return frame
        
        # Estimate head poses for all tracks
        frame_head_poses = self.head_pose_service.estimate_frame_head_poses(
            frame=frame,
            frame_tracks=self.last_frame_tracks,
            pose_result=self.last_pose_result,
            frame_number=frame_number,
            timestamp=timestamp,
        )
        
        self.last_head_poses = frame_head_poses
        
        # Visualize if enabled
        if self.visualize:
            frame = self._visualize_head_poses(frame, frame_head_poses)
        
        # Log summary
        if frame_number % 30 == 0:
            self.logger.info(
                f"Frame {frame_number}: Head poses estimated for {len(frame_head_poses.head_poses)} tracks, "
                f"Processing time: {frame_head_poses.processing_time_ms:.2f}ms"
            )
        
        return frame
    
    def _visualize_head_poses(self, frame: np.ndarray, frame_head_poses: FrameHeadPoses) -> np.ndarray:
        """
        Visualize head pose estimates on frame.
        
        Args:
            frame: Input frame (H, W, 3)
            frame_head_poses: FrameHeadPoses with head pose estimates
            
        Returns:
            Frame with head pose visualization
        """
        from app.head_pose.head_pose_utils import draw_head_pose
        
        for head_pose in frame_head_poses.head_poses:
            # Get track bounding box
            track = self.last_frame_tracks.get_track_by_id(head_pose.track_id)
            if track is None:
                continue
            
            # Draw head pose
            frame = draw_head_pose(
                frame=frame,
                head_pose=head_pose,
                bbox=track.bounding_box,
                color=(0, 255, 255),  # Yellow
                font_scale=0.5,
            )
        
        return frame
    
    def get_last_head_poses(self) -> Optional[FrameHeadPoses]:
        """
        Get head poses from the last processed frame.
        
        Returns:
            FrameHeadPoses object or None if no frame processed yet
        """
        return self.last_head_poses
    
    def get_head_pose_by_track_id(self, track_id: int) -> Optional[HeadPoseResult]:
        """
        Get head pose for a specific track ID from the last frame.
        
        Args:
            track_id: Track ID to retrieve
            
        Returns:
            HeadPoseResult object or None if not found
        """
        if self.last_head_poses:
            return self.last_head_poses.get_head_pose_by_track_id(track_id)
        return None
    
    def get_statistics(self):
        """
        Get head pose estimation statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.head_pose_service.get_statistics()
    
    def reset(self) -> None:
        """Reset processor state."""
        self.last_frame_tracks = None
        self.last_pose_result = None
        self.last_head_poses = None
        self.head_pose_service.reset_statistics()
        
        self.logger.info("HeadPoseProcessor reset")
    
    def cleanup(self) -> None:
        """Clean up processor resources."""
        self.head_pose_service.cleanup()
        self.last_frame_tracks = None
        self.last_pose_result = None
        self.last_head_poses = None
        
        self.logger.info("HeadPoseProcessor cleaned up")

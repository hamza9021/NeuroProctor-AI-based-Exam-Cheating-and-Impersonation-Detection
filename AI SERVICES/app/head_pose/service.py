"""
Head Pose Estimation Service.

This module provides the main service for head pose estimation using 6DRepNet,
integrating model loading, face cropping, and inference.
"""

import time
import numpy as np
from typing import List, Optional, Dict, Any

from app.head_pose.schemas import HeadPoseResult, FrameHeadPoses
from app.head_pose.model_loader import HeadPoseModelLoader
from app.head_pose.face_cropper import FaceCropper
from app.pose.pose_result import PersonPose, PoseResult
from app.tracking.tracking_models import Track, FrameTracks
from app.utils.logger import get_logger


class HeadPoseService:
    """
    Service for head pose estimation using 6DRepNet.
    
    This service provides a clean interface for estimating head orientation
    (yaw, pitch, roll) for tracked persons in video frames.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        min_crop_size: int = 64,
        crop_padding: float = 0.3,
        use_keypoints: bool = True,
        confidence_threshold: float = 0.5,
    ):
        """
        Initialize the head pose estimation service.
        
        Args:
            model_path: Path to 6DRepNet model weights (None for pretrained)
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
            min_crop_size: Minimum face crop size in pixels
            crop_padding: Padding ratio around face (0.0 to 1.0)
            use_keypoints: Whether to use pose keypoints for face refinement
            confidence_threshold: Minimum confidence threshold for results
        """
        self.logger = get_logger(__name__)
        
        self.confidence_threshold = confidence_threshold
        self.is_available = False
        
        # Try to initialize model loader
        try:
            # Initialize model loader
            self.model_loader = HeadPoseModelLoader(
                model_path=model_path,
                device=device,
                pretrained=True,
            )
            
            # Initialize face cropper
            self.face_cropper = FaceCropper(
                min_crop_size=min_crop_size,
                crop_padding=crop_padding,
                use_keypoints=use_keypoints,
                debug_visualization=True,  # Enable debug visualization
                debug_output_dir="debug_face_crops",
            )
            
            # Statistics
            self.total_frames_processed = 0
            self.total_inferences = 0
            self.failed_inferences = 0
            self.average_processing_time_ms = 0.0
            
            self.is_available = True
            self.logger.info("HeadPoseService initialized successfully")
            
        except RuntimeError as e:
            self.logger.warning(f"HeadPoseService initialization failed: {e}")
            self.logger.warning("Head pose estimation will be disabled")
            self.is_available = False
    
    def estimate_frame_head_poses(
        self,
        frame: np.ndarray,
        frame_tracks: FrameTracks,
        pose_result: Optional[PoseResult] = None,
        frame_number: int = 0,
        timestamp: float = 0.0,
    ) -> FrameHeadPoses:
        """
        Estimate head poses for all tracked persons in a frame.
        
        Args:
            frame: Input frame (H, W, 3)
            frame_tracks: FrameTracks with active tracks
            pose_result: Optional PoseResult with pose keypoints
            frame_number: Frame number in the video
            timestamp: Timestamp in seconds
            
        Returns:
            FrameHeadPoses with head pose estimates for all tracks
        """
        # Return empty result if service is not available
        if not self.is_available:
            return FrameHeadPoses(
                frame_number=frame_number,
                timestamp=timestamp,
                head_poses=[],
                processing_time_ms=0.0,
            )
        
        start_time = time.time()
        
        head_poses = []
        
        # Get active tracks
        active_tracks = frame_tracks.get_active_tracks()
        
        for track in active_tracks:
            try:
                # Get corresponding pose if available
                pose = None
                if pose_result is not None:
                    pose = self._find_pose_for_track(track, pose_result)
                
                # Estimate head pose for this track
                head_pose = self.estimate_track_head_pose(
                    frame=frame,
                    track=track,
                    pose=pose,
                    frame_number=frame_number,
                    timestamp=timestamp,
                )
                
                if head_pose is not None:
                    head_poses.append(head_pose)
                    self.total_inferences += 1
                else:
                    self.failed_inferences += 1
                    
            except Exception as e:
                self.logger.error(f"Head pose estimation failed for track {track.track_id}: {e}")
                self.failed_inferences += 1
                continue
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Update statistics
        self.total_frames_processed += 1
        self.average_processing_time_ms = (
            (self.average_processing_time_ms * (self.total_frames_processed - 1) + processing_time)
            / self.total_frames_processed
        )
        
        # Create result
        frame_head_poses = FrameHeadPoses(
            frame_number=frame_number,
            timestamp=timestamp,
            head_poses=head_poses,
            processing_time_ms=processing_time,
        )
        
        # Log summary
        if frame_number % 30 == 0:
            self._log_statistics()
        
        return frame_head_poses
    
    def estimate_track_head_pose(
        self,
        frame: np.ndarray,
        track: Track,
        pose: Optional[PersonPose] = None,
        frame_number: int = 0,
        timestamp: float = 0.0,
    ) -> Optional[HeadPoseResult]:
        """
        Estimate head pose for a single tracked person.
        
        Args:
            frame: Input frame (H, W, 3)
            track: Track object with bounding box
            pose: Optional PersonPose with keypoints
            frame_number: Frame number in the video
            timestamp: Timestamp in seconds
            
        Returns:
            HeadPoseResult if successful, None otherwise
        """
        try:
            # Extract face crop
            crop_result = self.face_cropper.extract_face_crop(frame, track, pose)
            
            if not crop_result.is_valid:
                self.logger.debug(f"Track {track.track_id}: Invalid face crop, skipping inference")
                return None
            
            # Check crop confidence
            if crop_result.confidence < self.confidence_threshold:
                self.logger.debug(f"Track {track.track_id}: Low confidence crop ({crop_result.confidence:.2f}), skipping inference")
                return None
            
            # Validate crop before prediction
            if crop_result.crop is None:
                self.logger.error(f"Track {track.track_id}: crop is None before prediction")
                return None
            
            if not isinstance(crop_result.crop, np.ndarray):
                self.logger.error(f"Track {track.track_id}: crop is not numpy array: {type(crop_result.crop)}")
                return None
            
            if crop_result.crop.size == 0:
                self.logger.error(f"Track {track.track_id}: crop is empty: shape={crop_result.crop.shape}")
                return None
            
            # Log crop details before prediction
            crop_width = crop_result.crop.shape[1]
            crop_height = crop_result.crop.shape[0]
            self.logger.debug(f"Track {track.track_id}: Predicting head pose, crop size: {crop_width}x{crop_height}, confidence: {crop_result.confidence:.2f}")
            
            # Predict head pose
            import time
            start_time = time.time()
            yaw, pitch, roll = self.model_loader.predict(crop_result.crop)
            inference_time = (time.time() - start_time) * 1000
            
            self.logger.debug(f"Track {track.track_id}: Head pose prediction succeeded - yaw: {yaw:.2f}°, pitch: {pitch:.2f}°, roll: {roll:.2f}°, time: {inference_time:.2f}ms")
            
            # Normalize angles
            yaw = self._normalize_angle(yaw)
            pitch = self._normalize_angle(pitch)
            roll = self._normalize_angle(roll)
            
            # Create result
            head_pose = HeadPoseResult(
                track_id=track.track_id,
                frame_number=frame_number,
                timestamp=timestamp,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                confidence=crop_result.confidence,
                face_crop_bbox=crop_result.crop_bbox,
                metadata={
                    'track_class': track.class_name,
                    'track_confidence': track.confidence,
                },
            )
            
            # Log result
            self.logger.debug(
                f"Track {track.track_id}: Yaw={yaw:.1f}°, Pitch={pitch:.1f}°, Roll={roll:.1f}°, "
                f"Confidence={crop_result.confidence:.2f}"
            )
            
            return head_pose
            
        except Exception as e:
            self.logger.error(f"Head pose estimation failed for track {track.track_id}: {e}")
            return None
    
    def _find_pose_for_track(
        self,
        track: Track,
        pose_result: PoseResult,
    ) -> Optional[PersonPose]:
        """
        Find the pose corresponding to a track.
        
        Args:
            track: Track object
            pose_result: PoseResult with all poses
            
        Returns:
            PersonPose if found, None otherwise
        """
        # Try to match by track_id first
        for pose in pose_result.persons:
            if pose.track_id == track.track_id:
                return pose
        
        # Fallback: try to match by bounding box IoU
        from app.tracking.tracking_utils import calculate_iou
        
        best_pose = None
        best_iou = 0.3
        
        for pose in pose_result.persons:
            iou = calculate_iou(track.bounding_box, pose.bounding_box)
            if iou > best_iou:
                best_iou = iou
                best_pose = pose
        
        return best_pose
    
    def _normalize_angle(self, angle: float) -> float:
        """
        Normalize angle to [-90, 90] range.
        
        Args:
            angle: Angle in degrees
            
        Returns:
            Normalized angle in [-90, 90]
        """
        while angle > 90:
            angle -= 180
        while angle < -90:
            angle += 180
        return angle
    
    def _log_statistics(self) -> None:
        """Log service statistics."""
        success_rate = 0.0
        if self.total_inferences > 0:
            success_rate = (self.total_inferences / (self.total_inferences + self.failed_inferences)) * 100
        
        self.logger.info(
            f"HeadPose Stats - Frames: {self.total_frames_processed}, "
            f"Inferences: {self.total_inferences}, "
            f"Failed: {self.failed_inferences}, "
            f"Success Rate: {success_rate:.1f}%, "
            f"Avg Time: {self.average_processing_time_ms:.2f}ms"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = 0.0
        if self.total_inferences > 0:
            success_rate = (self.total_inferences / (self.total_inferences + self.failed_inferences)) * 100
        
        return {
            'total_frames_processed': self.total_frames_processed,
            'total_inferences': self.total_inferences,
            'failed_inferences': self.failed_inferences,
            'success_rate': success_rate,
            'average_processing_time_ms': self.average_processing_time_ms,
        }
    
    def get_device(self) -> str:
        """
        Get the device being used.
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        return self.model_loader.get_device()
    
    def reset_statistics(self) -> None:
        """Reset service statistics."""
        self.total_frames_processed = 0
        self.total_inferences = 0
        self.failed_inferences = 0
        self.average_processing_time_ms = 0.0
        
        self.logger.info("HeadPoseService statistics reset")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.model_loader.cleanup()
        self.logger.info("HeadPoseService cleaned up")

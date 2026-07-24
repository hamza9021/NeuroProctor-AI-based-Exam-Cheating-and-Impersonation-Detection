"""
Face Cropper for Head Pose Estimation.

This module handles extraction of face crops from tracked person bounding boxes,
with optional refinement using YOLO pose keypoints for better accuracy.
"""

import numpy as np
import cv2
from typing import Optional, Tuple
from dataclasses import dataclass
import os

from app.pose.pose_result import PersonPose
from app.tracking.tracking_models import Track
from app.utils.logger import get_logger


@dataclass
class FaceCropResult:
    """
    Result of face crop extraction.
    
    Attributes:
        crop: Face crop as numpy array
        crop_bbox: Bounding box of the crop (x1, y1, x2, y2)
        is_valid: Whether the crop is valid
        confidence: Confidence score for the crop quality
    """
    crop: Optional[np.ndarray]
    crop_bbox: Tuple[int, int, int, int]
    is_valid: bool
    confidence: float = 1.0


class FaceCropper:
    """
    Face crop extractor for head pose estimation.
    
    This class extracts face crops from tracked person bounding boxes,
    with optional refinement using pose keypoints for better accuracy.
    """
    
    def __init__(
        self,
        min_crop_size: int = 64,
        crop_padding: float = 0.3,
        use_keypoints: bool = True,
        debug_visualization: bool = False,
        debug_output_dir: str = "debug_frames",
    ):
        """
        Initialize the face cropper.
        
        Args:
            min_crop_size: Minimum crop size in pixels
            crop_padding: Padding ratio around the face (0.0 to 1.0)
            use_keypoints: Whether to use pose keypoints for refinement
            debug_visualization: Whether to save debug visualization frames
            debug_output_dir: Directory to save debug frames
        """
        self.logger = get_logger(__name__)
        
        self.min_crop_size = min_crop_size
        self.crop_padding = crop_padding
        self.use_keypoints = use_keypoints
        self.debug_visualization = debug_visualization
        self.debug_output_dir = debug_output_dir
        self.debug_frame_count = 0
        
        if self.debug_visualization:
            os.makedirs(self.debug_output_dir, exist_ok=True)
        
        self.logger.info(f"FaceCropper initialized: min_size={min_crop_size}, padding={crop_padding}, debug={debug_visualization}")
    
    def extract_face_crop(
        self,
        frame: np.ndarray,
        track: Track,
        pose: Optional[PersonPose] = None,
    ) -> FaceCropResult:
        """
        Extract face crop from frame for a tracked person.
        
        Args:
            frame: Input frame (H, W, 3)
            track: Track object with bounding box
            pose: Optional PersonPose with keypoints for refinement
            
        Returns:
            FaceCropResult with crop and metadata
        """
        try:
            # Validate input frame
            if frame is None:
                self.logger.error("Input frame is None")
                return FaceCropResult(None, (0, 0, 0, 0), False, 0.0)
            
            if not isinstance(frame, np.ndarray):
                self.logger.error(f"Input frame is not numpy array: {type(frame)}")
                return FaceCropResult(None, (0, 0, 0, 0), False, 0.0)
            
            if frame.size == 0:
                self.logger.error(f"Input frame is empty: shape={frame.shape}")
                return FaceCropResult(None, (0, 0, 0, 0), False, 0.0)
            
            # Log input details
            self.logger.debug(f"Frame shape: {frame.shape}, dtype: {frame.dtype}")
            self.logger.debug(f"Track {track.track_id} bbox: {track.bounding_box}")
            
            # Get face bounding box
            face_bbox = self._get_face_bbox(track, pose)
            self.logger.debug(f"Track {track.track_id} calculated face bbox: {face_bbox}")
            
            # Clamp coordinates to frame boundaries
            height, width = frame.shape[:2]
            x1, y1, x2, y2 = face_bbox
            
            self.logger.debug(f"Track {track.track_id} face bbox before clamping: ({x1}, {y1}, {x2}, {y2})")
            self.logger.debug(f"Track {track.track_id} frame dimensions: width={width}, height={height}")
            
            # Clamp to frame boundaries but preserve minimum size
            # If box extends beyond boundaries, shift it inward instead of just clipping
            box_width = x2 - x1
            box_height = y2 - y1
            
            # For X axis
            if x1 < 0:
                # Shift entire box right instead of clipping left edge
                shift = -x1
                x1 = 0
                x2 = min(width, x2 + shift)
            elif x2 > width:
                # Shift entire box left instead of clipping right edge
                shift = x2 - width
                x2 = width
                x1 = max(0, x1 - shift)
            
            # For Y axis
            if y1 < 0:
                # Shift entire box down instead of clipping top edge
                shift = -y1
                y1 = 0
                y2 = min(height, y2 + shift)
            elif y2 > height:
                # Shift entire box up instead of clipping bottom edge
                shift = y2 - height
                y2 = height
                y1 = max(0, y1 - shift)
            
            # Final clamp to ensure within bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)
            
            self.logger.debug(f"Track {track.track_id} face bbox after clamping: ({x1}, {y1}, {x2}, {y2})")
            
            # Ensure x1 < x2 and y1 < y2 with minimum size
            min_size = self.min_crop_size
            if x1 >= x2 or (x2 - x1) < min_size:
                self.logger.warning(f"Track {track.track_id} invalid bbox width: {x2 - x1}, adjusting")
                # Center the box and ensure minimum size
                center = (x1 + x2) / 2
                x1 = max(0, int(center - min_size / 2))
                x2 = min(width, int(center + min_size / 2))
                if x2 - x1 < min_size:
                    x2 = min(width, x1 + min_size)
                    
            if y1 >= y2 or (y2 - y1) < min_size:
                self.logger.warning(f"Track {track.track_id} invalid bbox height: {y2 - y1}, adjusting")
                # Center the box and ensure minimum size
                center = (y1 + y2) / 2
                y1 = max(0, int(center - min_size / 2))
                y2 = min(height, int(center + min_size / 2))
                if y2 - y1 < min_size:
                    y2 = min(height, y1 + min_size)
            
            face_bbox = (int(x1), int(y1), int(x2), int(y2))
            crop_width = x2 - x1
            crop_height = y2 - y1
            self.logger.debug(f"Track {track.track_id} final face bbox: {face_bbox}, crop dimensions: {crop_width}x{crop_height}")
            
            # Validate bounding box
            if not self._validate_bbox(face_bbox, frame.shape):
                self.logger.warning(f"Track {track.track_id} invalid face bbox: {face_bbox}, frame shape: {frame.shape}, crop size: {crop_width}x{crop_height}")
                return FaceCropResult(None, face_bbox, False, 0.0)
            
            # Extract crop
            crop = self._extract_crop(frame, face_bbox)
            self.logger.debug(f"Crop shape: {crop.shape if crop is not None else None}, dtype: {crop.dtype if crop is not None else None}")
            
            # Validate crop
            if not self._validate_crop(crop):
                self.logger.warning(f"Invalid crop for track {track.track_id}: shape={crop.shape if crop is not None else None}, dtype={crop.dtype if crop is not None else None}")
                return FaceCropResult(None, face_bbox, False, 0.0)
            
            # Calculate confidence based on crop quality
            confidence = self._calculate_crop_confidence(crop)
            
            # Create result
            crop_result = FaceCropResult(crop, face_bbox, True, confidence)
            
            # Save debug visualization if enabled
            if self.debug_visualization and self.debug_frame_count < 20:
                self._save_debug_visualization(frame, track, pose, face_bbox, crop_result)
            
            return crop_result
            
        except Exception as e:
            self.logger.error(f"Face crop extraction failed for track {track.track_id}: {e}", exc_info=True)
            return FaceCropResult(None, (0, 0, 0, 0), False, 0.0)
    
    def _get_face_bbox(
        self,
        track: Track,
        pose: Optional[PersonPose] = None,
    ) -> Tuple[int, int, int, int]:
        """
        Get face bounding box from track and optional pose keypoints.
        
        Args:
            track: Track object with bounding box
            pose: Optional PersonPose with keypoints
            
        Returns:
            Face bounding box (x1, y1, x2, y2)
        """
        if self.use_keypoints and pose is not None:
            # Use pose keypoints to refine face region
            return self._get_face_bbox_from_keypoints(track, pose)
        else:
            # Use track bounding box (upper half for face)
            return self._get_face_bbox_from_track(track)
    
    def _get_face_bbox_from_track(self, track: Track) -> Tuple[int, int, int, int]:
        """
        Get face bounding box from track bounding box.
        
        Uses the upper half of the person bounding box as face region.
        
        Args:
            track: Track object with bounding box
            
        Returns:
            Face bounding box (x1, y1, x2, y2)
        """
        x1, y1, x2, y2 = track.bounding_box
        self.logger.debug(f"Track {track.track_id} raw bbox: ({x1}, {y1}, {x2}, {y2})")
        
        # Ensure valid bbox
        if x2 <= x1 or y2 <= y1:
            self.logger.warning(f"Track {track.track_id} has invalid bbox dimensions: ({x1}, {y1}, {x2}, {y2})")
            # Try to fix by swapping
            if x2 <= x1:
                x1, x2 = x2, x1
            if y2 <= y1:
                y1, y2 = y2, y1
        
        width = x2 - x1
        height = y2 - y1
        
        self.logger.debug(f"Track {track.track_id} bbox dimensions: width={width}, height={height}")
        
        # Use upper half for face (adjust based on actual bbox size)
        # For small bboxes, use a larger percentage to ensure minimum face size
        if height < 50:
            face_height_ratio = 0.9  # Use most of very small bboxes
        elif height < 100:
            face_height_ratio = 0.8  # Use more of small bboxes
        elif height < 200:
            face_height_ratio = 0.7
        else:
            face_height_ratio = 0.6  # Standard ratio
            
        face_x1 = x1
        face_y1 = y1
        face_x2 = x2
        face_y2 = y1 + int(height * face_height_ratio)
        
        # Ensure minimum face height (at least 50 pixels)
        min_face_height = 50
        if face_y2 - face_y1 < min_face_height:
            face_y2 = min(y2, face_y1 + min_face_height)
        
        self.logger.debug(f"Track {track.track_id} face bbox before padding: ({face_x1}, {face_y1}, {face_x2}, {face_y2}), ratio={face_height_ratio}")
        
        # Add padding (ensure minimum padding)
        padding_x = max(10, int(width * self.crop_padding))
        padding_y = max(10, int((face_y2 - face_y1) * self.crop_padding))
        
        face_x1 = face_x1 - padding_x
        face_y1 = face_y1 - padding_y
        face_x2 = face_x2 + padding_x
        face_y2 = face_y2 + padding_y
        
        self.logger.debug(f"Track {track.track_id} face bbox after padding: ({face_x1}, {face_y1}, {face_x2}, {face_y2})")
        
        return (face_x1, face_y1, face_x2, face_y2)
    
    def _get_face_bbox_from_keypoints(
        self,
        track: Track,
        pose: PersonPose,
    ) -> Tuple[int, int, int, int]:
        """
        Get face bounding box from pose keypoints using robust algorithm.
        
        Preferred algorithm:
        1. If eyes and nose exist - compute eye distance, center on nose, create square box
        2. If eyes missing but nose exists - estimate face size using shoulder distance
        3. Fallback - use upper portion of person bounding box
        
        Args:
            track: Track object with bounding box
            pose: PersonPose with keypoints
            
        Returns:
            Face bounding box (x1, y1, x2, y2)
        """
        keypoints = pose.keypoints
        
        # Get relevant keypoints
        nose = keypoints.get_keypoint_by_name('nose')
        left_eye = keypoints.get_keypoint_by_name('left_eye')
        right_eye = keypoints.get_keypoint_by_name('right_eye')
        left_ear = keypoints.get_keypoint_by_name('left_ear')
        right_ear = keypoints.get_keypoint_by_name('right_ear')
        left_shoulder = keypoints.get_keypoint_by_name('left_shoulder')
        right_shoulder = keypoints.get_keypoint_by_name('right_shoulder')
        
        self.logger.debug(f"Track {track.track_id} keypoints availability: nose={nose is not None}, left_eye={left_eye is not None}, right_eye={right_eye is not None}")
        
        # Algorithm 1: Use eyes and nose for accurate face box
        if nose is not None and left_eye is not None and right_eye is not None:
            if nose.confidence > 0.5 and left_eye.confidence > 0.5 and right_eye.confidence > 0.5:
                # Compute eye distance
                eye_distance = np.sqrt((right_eye.x - left_eye.x)**2 + (right_eye.y - left_eye.y)**2)
                
                # Face size is approximately 3x eye distance
                face_size = int(eye_distance * 3.0)
                face_size = max(64, face_size)  # Minimum face size
                
                # Center on nose
                center_x = int(nose.x)
                center_y = int(nose.y)
                
                # Create square box
                half_size = face_size // 2
                face_x1 = center_x - half_size
                face_y1 = center_y - half_size
                face_x2 = center_x + half_size
                face_y2 = center_y + half_size
                
                # Add padding
                padding = int(face_size * self.crop_padding)
                face_x1 -= padding
                face_y1 -= padding
                face_x2 += padding
                face_y2 += padding
                
                self.logger.debug(f"Track {track.track_id} face bbox from eyes+nose: ({face_x1}, {face_y1}, {face_x2}, {face_y2}), eye_distance={eye_distance:.1f}")
                return (face_x1, face_y1, face_x2, face_y2)
        
        # Algorithm 2: Use nose and estimate size from shoulders
        if nose is not None and left_shoulder is not None and right_shoulder is not None:
            if nose.confidence > 0.5 and left_shoulder.confidence > 0.5 and right_shoulder.confidence > 0.5:
                # Shoulder distance for scale estimation
                shoulder_distance = np.sqrt((right_shoulder.x - left_shoulder.x)**2 + (right_shoulder.y - left_shoulder.y)**2)
                
                # Face size is approximately 0.5x shoulder distance
                face_size = int(shoulder_distance * 0.5)
                face_size = max(64, face_size)
                
                # Center on nose
                center_x = int(nose.x)
                center_y = int(nose.y)
                
                # Create square box
                half_size = face_size // 2
                face_x1 = center_x - half_size
                face_y1 = center_y - half_size
                face_x2 = center_x + half_size
                face_y2 = center_y + half_size
                
                # Add padding
                padding = int(face_size * self.crop_padding)
                face_x1 -= padding
                face_y1 -= padding
                face_x2 += padding
                face_y2 += padding
                
                self.logger.debug(f"Track {track.track_id} face bbox from nose+shoulders: ({face_x1}, {face_y1}, {face_x2}, {face_y2}), shoulder_distance={shoulder_distance:.1f}")
                return (face_x1, face_y1, face_x2, face_y2)
        
        # Algorithm 3: Use any available face keypoints
        valid_face_points = []
        for kp in [nose, left_eye, right_eye, left_ear, right_ear]:
            if kp is not None and kp.confidence > 0.5:
                valid_face_points.append((kp.x, kp.y))
        
        if len(valid_face_points) >= 2:
            xs = [p[0] for p in valid_face_points]
            ys = [p[1] for p in valid_face_points]
            
            face_x1 = int(min(xs))
            face_y1 = int(min(ys))
            face_x2 = int(max(xs))
            face_y2 = int(max(ys))
            
            # Ensure minimum size
            if face_x2 - face_x1 < 20:
                face_x1 = max(0, face_x1 - 10)
                face_x2 = face_x2 + 10
            if face_y2 - face_y1 < 20:
                face_y1 = max(0, face_y1 - 10)
                face_y2 = face_y2 + 10
            
            # Add padding
            width = face_x2 - face_x1
            height = face_y2 - face_y1
            padding_x = max(10, int(width * self.crop_padding))
            padding_y = max(10, int(height * self.crop_padding))
            
            face_x1 = face_x1 - padding_x
            face_y1 = face_y1 - padding_y
            face_x2 = face_x2 + padding_x
            face_y2 = face_y2 + padding_y
            
            self.logger.debug(f"Track {track.track_id} face bbox from available keypoints ({len(valid_face_points)}): ({face_x1}, {face_y1}, {face_x2}, {face_y2})")
            return (face_x1, face_y1, face_x2, face_y2)
        
        # Fallback: Use track-based estimation
        self.logger.debug(f"Track {track.track_id} insufficient keypoints, using track bbox fallback")
        return self._get_face_bbox_from_track(track)
    
    def _validate_bbox(
        self,
        bbox: Tuple[int, int, int, int],
        frame_shape: Tuple[int, int, int],
    ) -> bool:
        """
        Validate bounding box dimensions.
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
            frame_shape: Frame shape (H, W, C)
            
        Returns:
            True if valid, False otherwise
        """
        x1, y1, x2, y2 = bbox
        height, width = frame_shape[:2]
        
        # Check bounds (allow slight overflow for edge cases)
        if x1 < -5 or y1 < -5 or x2 > width + 5 or y2 > height + 5:
            self.logger.debug(f"Bbox out of bounds: ({x1}, {y1}, {x2}, {y2}), frame: ({width}, {height})")
            return False
        
        # Check size
        crop_width = x2 - x1
        crop_height = y2 - y1
        
        if crop_width <= 0 or crop_height <= 0:
            self.logger.debug(f"Bbox has non-positive dimensions: width={crop_width}, height={crop_height}")
            return False
        
        if crop_width < self.min_crop_size or crop_height < self.min_crop_size:
            self.logger.debug(f"Bbox too small: width={crop_width}, height={crop_height}, min={self.min_crop_size}")
            return False
        
        return True
    
    def _extract_crop(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
    ) -> np.ndarray:
        """
        Extract crop from frame.
        
        Args:
            frame: Input frame (H, W, 3)
            bbox: Bounding box (x1, y1, x2, y2)
            
        Returns:
            Face crop as numpy array
        """
        x1, y1, x2, y2 = bbox
        return frame[y1:y2, x1:x2].copy()
    
    def _validate_crop(self, crop: np.ndarray) -> bool:
        """
        Validate crop quality.
        
        Args:
            crop: Face crop as numpy array
            
        Returns:
            True if valid, False otherwise
        """
        if crop is None or crop.size == 0:
            return False
        
        if len(crop.shape) != 3 or crop.shape[2] != 3:
            return False
        
        # Check for reasonable brightness (not too dark or too bright)
        mean_brightness = np.mean(crop)
        if mean_brightness < 10 or mean_brightness > 245:
            return False
        
        # Check for variance (not uniform color)
        if np.std(crop) < 5:
            return False
        
        return True
    
    def _calculate_crop_confidence(self, crop: np.ndarray) -> float:
        """
        Calculate confidence score for crop quality.
        
        Args:
            crop: Face crop as numpy array
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from validation
        if not self._validate_crop(crop):
            return 0.0
        
        # Calculate based on size
        height, width = crop.shape[:2]
        size_score = min(1.0, (width * height) / (224 * 224))
        
        # Calculate based on brightness
        mean_brightness = np.mean(crop)
        brightness_score = 1.0 - abs(mean_brightness - 128) / 128
        
        # Calculate based on variance
        variance_score = min(1.0, np.std(crop) / 64)
        
        # Combined score
        confidence = (size_score + brightness_score + variance_score) / 3
        
        return max(0.0, min(1.0, confidence))
    
    def _save_debug_visualization(
        self,
        frame: np.ndarray,
        track: Track,
        pose: Optional[PersonPose],
        face_bbox: Tuple[int, int, int, int],
        crop_result: FaceCropResult,
    ) -> None:
        """
        Save debug visualization frame showing face bounding box and keypoints.
        
        Args:
            frame: Original frame
            track: Track object
            pose: Optional pose result
            face_bbox: Generated face bounding box
            crop_result: Face crop result
        """
        try:
            debug_frame = frame.copy()
            
            # Draw person bounding box in green
            x1, y1, x2, y2 = track.bounding_box
            cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Person {track.track_id}", (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw face bounding box in red
            fx1, fy1, fx2, fy2 = face_bbox
            cv2.rectangle(debug_frame, (fx1, fy1), (fx2, fy2), (0, 0, 255), 2)
            cv2.putText(debug_frame, f"Face {track.track_id}", (fx1, fy1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Draw pose keypoints in blue if available
            if pose is not None:
                keypoints = pose.keypoints
                keypoint_names = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 
                                'left_shoulder', 'right_shoulder']
                for kp_name in keypoint_names:
                    kp = keypoints.get_keypoint_by_name(kp_name)
                    if kp is not None and kp.confidence > 0.5:
                        cv2.circle(debug_frame, (int(kp.x), int(kp.y)), 5, (255, 0, 0), -1)
            
            # Draw crop center in yellow
            if crop_result.is_valid and crop_result.crop is not None:
                cx = (fx1 + fx2) // 2
                cy = (fy1 + fy2) // 2
                cv2.circle(debug_frame, (cx, cy), 8, (0, 255, 255), -1)
            
            # Add info text
            info_text = f"Track {track.track_id} | Valid: {crop_result.is_valid} | Conf: {crop_result.confidence:.2f}"
            cv2.putText(debug_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Save frame
            output_path = os.path.join(self.debug_output_dir, f"debug_frame_{self.debug_frame_count:03d}_track_{track.track_id}.jpg")
            cv2.imwrite(output_path, debug_frame)
            
            self.debug_frame_count += 1
            self.logger.debug(f"Saved debug visualization: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save debug visualization: {e}")

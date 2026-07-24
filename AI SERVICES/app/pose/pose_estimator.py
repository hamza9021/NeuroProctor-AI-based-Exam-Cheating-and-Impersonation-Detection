"""
Pose Estimator module using YOLO.

This module provides a PoseEstimator class that uses Ultralytics YOLO
for real-time pose estimation in video frames.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import time

from ultralytics import YOLO

from app.pose.keypoints import Keypoint, Keypoints
from app.pose.skeleton import SKELETON_CONNECTIONS
from app.pose.pose_result import PersonPose, PoseResult
from app.config.settings import settings
from app.utils.logger import get_logger


class PoseEstimator:
    """YOLO-based pose estimator for exam monitoring."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize pose estimator.

        Args:
            model_path: Path to YOLO pose model file (uses settings default if not provided)
            confidence_threshold: Confidence threshold for detections (uses settings default if not provided)
            iou_threshold: IoU threshold for NMS (uses settings default if not provided)
            device: Device to run inference on (uses settings default if not provided)
        """
        self.logger = get_logger(__name__)
        
        # Use configuration from settings
        if model_path:
            model_path_obj = Path(model_path)
            if model_path_obj.is_absolute():
                self.model_path = model_path_obj
            else:
                self.model_path = settings.MODELS_DIR / model_path
        else:
            self.model_path = settings.MODELS_DIR / settings.POSE_MODEL
        
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else settings.POSE_CONFIDENCE_THRESHOLD
        self.iou_threshold = iou_threshold if iou_threshold is not None else settings.POSE_IOU_THRESHOLD
        self.device = device if device else settings.DEVICE

        self.model: Optional[YOLO] = None
        self.is_loaded = False

        # COCO 17 keypoints names
        self.keypoint_names = [
            "nose", "left_eye", "right_eye", "left_ear", "right_ear",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle",
        ]

    def load_model(self) -> None:
        """
        Load YOLO pose model.

        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        if self.is_loaded:
            self.logger.warning("Pose model already loaded, skipping")
            return

        start_time = time.time()

        try:
            # Check if model file exists
            if not self.model_path.exists():
                self.logger.warning(f"Pose model not found at {self.model_path}, downloading from Ultralytics...")
                # Ultralytics will auto-download if model name is provided
                self.model = YOLO(settings.POSE_MODEL)
            else:
                self.model = YOLO(str(self.model_path))

            # Set device
            if self.device == "auto":
                self.model.to("cuda" if self.model.device.type == "cuda" else "cpu")
            else:
                self.model.to(self.device)

            self.is_loaded = True
            loading_time = time.time() - start_time
            
            self.logger.info(f"YOLO pose model loaded successfully from {self.model_path}")
            self.logger.info(f"Model: {settings.POSE_MODEL}")
            self.logger.info(f"Using device: {self.model.device}")
            self.logger.info(f"Model loading time: {loading_time:.2f}s")

        except Exception as e:
            self.logger.error(f"Failed to load YOLO pose model: {e}")
            raise RuntimeError(f"Failed to load YOLO pose model: {e}")

    def estimate(
        self,
        frame: np.ndarray,
        frame_number: int = 0,
        timestamp: float = 0.0,
    ) -> PoseResult:
        """
        Estimate poses in a frame.

        Args:
            frame: Input frame as numpy array
            frame_number: Frame number for logging
            timestamp: Frame timestamp

        Returns:
            PoseResult object containing all person poses

        Raises:
            RuntimeError: If model is not loaded
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Pose model not loaded. Call load_model() first.")

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
        persons = []

        if len(results) > 0:
            result = results[0]
            
            if result.keypoints is not None:
                # YOLO pose returns keypoints as (x, y, confidence) for each keypoint
                keypoints_data = result.keypoints.data.cpu().numpy()  # Shape: (num_persons, 17, 3)
                
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    box_confidences = result.boxes.conf.cpu().numpy()
                else:
                    boxes = None
                    box_confidences = None

                num_persons = len(keypoints_data)
                
                for person_idx in range(num_persons):
                    # Extract bounding box
                    if boxes is not None:
                        x1, y1, x2, y2 = boxes[person_idx]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        confidence = float(box_confidences[person_idx]) if box_confidences is not None else 0.0
                    else:
                        # Compute bounding box from keypoints
                        person_keypoints = keypoints_data[person_idx]
                        visible_keypoints = person_keypoints[person_keypoints[:, 2] > 0]
                        if len(visible_keypoints) > 0:
                            x1, y1 = int(visible_keypoints[:, 0].min()), int(visible_keypoints[:, 1].min())
                            x2, y2 = int(visible_keypoints[:, 0].max()), int(visible_keypoints[:, 1].max())
                        else:
                            x1, y1, x2, y2 = 0, 0, 0, 0
                        confidence = 0.0

                    # Extract keypoints (x, y, confidence)
                    person_keypoints = keypoints_data[person_idx]
                    
                    keypoints_dict = {}
                    for kp_idx, kp_name in enumerate(self.keypoint_names):
                        if kp_idx < len(person_keypoints):
                            x, y, conf = person_keypoints[kp_idx]
                            
                            if conf > 0:  # Only store visible keypoints
                                keypoints_dict[kp_name] = Keypoint(
                                    x=float(x),
                                    y=float(y),
                                    confidence=float(conf),
                                    name=kp_name,
                                )

                    # Create Keypoints object
                    keypoints_obj = Keypoints(**keypoints_dict)

                    # Create PersonPose
                    person_pose = PersonPose(
                        person_id=person_idx,
                        bounding_box=(x1, y1, x2, y2),
                        confidence=confidence,
                        keypoints=keypoints_obj,
                    )
                    persons.append(person_pose)

        # Create pose result
        pose_result = PoseResult(
            frame_number=frame_number,
            timestamp=timestamp,
            persons=persons,
            inference_time_ms=inference_time,
        )

        # Log detection summary
        if persons:
            self.logger.debug(
                f"Frame {frame_number}: {len(persons)} persons detected, "
                f"Inference: {inference_time:.2f}ms"
            )

        return pose_result

    def draw_poses(
        self,
        frame: np.ndarray,
        pose_result: PoseResult,
    ) -> np.ndarray:
        """
        Draw pose results on frame.

        Args:
            frame: Input frame
            pose_result: PoseResult object

        Returns:
            Frame with drawn poses
        """
        annotated_frame = frame.copy()

        for person in pose_result.persons:
            # Draw bounding box
            x1, y1, x2, y2 = person.bounding_box
            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                settings.POSE_BOX_COLOR,
                settings.POSE_BOX_THICKNESS,
            )

            # Draw skeleton connections
            self._draw_skeleton(annotated_frame, person.keypoints)

            # Draw keypoints
            self._draw_keypoints(annotated_frame, person.keypoints)

        return annotated_frame

    def _draw_skeleton(self, frame: np.ndarray, keypoints: Keypoints) -> None:
        """
        Draw skeleton connections on frame.

        Args:
            frame: Frame to draw on
            keypoints: Keypoints object
        """
        for kp1_name, kp2_name in SKELETON_CONNECTIONS:
            kp1 = keypoints.get_keypoint_by_name(kp1_name)
            kp2 = keypoints.get_keypoint_by_name(kp2_name)

            if kp1 and kp2 and kp1.is_visible() and kp2.is_visible():
                pt1 = (int(kp1.x), int(kp1.y))
                pt2 = (int(kp2.x), int(kp2.y))
                cv2.line(
                    frame,
                    pt1,
                    pt2,
                    settings.POSE_SKELETON_COLOR,
                    settings.POSE_SKELETON_THICKNESS,
                )

    def _draw_keypoints(self, frame: np.ndarray, keypoints: Keypoints) -> None:
        """
        Draw keypoints on frame.

        Args:
            frame: Frame to draw on
            keypoints: Keypoints object
        """
        for keypoint in keypoints.get_visible_keypoints():
            pt = (int(keypoint.x), int(keypoint.y))
            cv2.circle(
                frame,
                pt,
                settings.POSE_KEYPOINT_RADIUS,
                settings.POSE_KEYPOINT_COLOR,
                -1,  # Filled circle
            )

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
            self.logger.info("Pose estimator cleaned up")

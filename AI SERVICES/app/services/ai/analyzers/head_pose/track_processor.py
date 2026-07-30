"""Track processor for single track head pose estimation."""

import logging
import time
import zlib
from typing import Optional, Tuple

import numpy as np

from app.services.ai.analyzers.head_pose.config import HeadPoseConfig
from app.services.ai.analyzers.head_pose.constants import EVENT_DATA_PATH_LOGGED
from app.services.ai.analyzers.head_pose.cropper import FaceCropper
from app.services.ai.analyzers.head_pose.estimator import HeadPoseEstimator
from app.services.ai.analyzers.head_pose.face_locator import FaceLocator
from app.services.ai.analyzers.head_pose.head_pose import HeadPoseResult
from app.services.ai.analyzers.head_pose.parser import HeadPoseParser
from app.services.ai.analyzers.head_pose.temporal_smoother import TemporalSmoother
from app.services.ai.analyzers.head_pose.validator import HeadPoseValidator
from app.services.ai.pipeline.frame_context import FrameContext

logger = logging.getLogger(__name__)

# COCO keypoint index for the nose
_NOSE_KP_INDEX = 0
# Minimum confidence to trust the nose keypoint
_NOSE_CONF_THRESHOLD = 0.5


class TrackProcessor:
    """Processes a single track for head pose estimation."""

    def __init__(
        self,
        locator: FaceLocator,
        cropper: FaceCropper,
        estimator: HeadPoseEstimator,
        parser: HeadPoseParser,
        validator: HeadPoseValidator,
        config: Optional[HeadPoseConfig] = None,
        temporal_smoother: Optional[TemporalSmoother] = None,
    ):
        """Initialize track processor.

        Args:
            locator: Face locator.
            cropper: Face cropper.
            estimator: Head pose estimator.
            parser: Output parser.
            validator: Result validator.
            config: Head pose configuration (used to gate diagnostic logging).
            temporal_smoother: Temporal smoother for angle smoothing.
        """
        self._locator = locator
        self._cropper = cropper
        self._estimator = estimator
        self._parser = parser
        self._validator = validator
        self._config = config
        self._temporal_smoother = temporal_smoother

    async def process(self, context: FrameContext, track) -> HeadPoseResult:
        """Process a single track.

        Args:
            context: FrameContext containing the current frame and poses.
            track: DeepSORT track object with ``track_id`` and ``bbox``.

        Returns:
            HeadPoseResult with all visualization fields populated.
        """
        frame_h, frame_w = context.frame.shape[:2]
        track_id = int(track.track_id)
        inference_executed = False
        axis_source = None

        logger.info(
            "[HEAD-POSE TRACE START] frame=%d track_id=%d",
            context.frame_number, track_id,
        )

        # ------------------------------------------------------------------ #
        # 1. Gather pose data for this specific track                         #
        # ------------------------------------------------------------------ #
        pose_data: Optional[dict] = None
        lookup_success = False
        lookup_failure_reason = "no_poses_dict"
        available_pose_track_ids = []
        pose_result_type = None
        keypoints_shape = None
        keypoint_confidences_shape = None
        nose_x = nose_y = nose_confidence = 0.0

        # Log FrameContext pose field structure
        pose_field_type = type(context.poses).__name__ if hasattr(context, "poses") else "no_poses_attr"
        logger.info(
            "[HEAD-POSE POSE STRUCTURE] frame=%d pose_field_type=%s",
            context.frame_number, pose_field_type,
        )

        if hasattr(context, "poses") and context.poses:
            # context.poses is a dictionary keyed by track_id (from PoseMapper)
            if isinstance(context.poses, dict):
                available_pose_track_ids = list(context.poses.keys())
                pose = context.poses.get(track_id)
                if pose is not None:
                    # PoseResult has separate keypoints and keypoint_confidences
                    # Convert to numpy array with shape (N, 3) for compatibility
                    if hasattr(pose, "keypoints") and hasattr(pose, "keypoint_confidences"):
                        kp_list = pose.keypoints
                        conf_list = pose.keypoint_confidences
                        if kp_list and conf_list and len(kp_list) == len(conf_list):
                            # Build (N, 3) array: [x, y, confidence]
                            keypoints_array = np.zeros((len(kp_list), 3), dtype=np.float32)
                            for i, (kp, conf) in enumerate(zip(kp_list, conf_list)):
                                keypoints_array[i, 0] = kp[0]
                                keypoints_array[i, 1] = kp[1]
                                keypoints_array[i, 2] = conf
                            pose_data = {"keypoints": keypoints_array}
                            pose_result_type = type(pose).__name__
                            keypoints_shape = keypoints_array.shape
                            keypoint_confidences_shape = len(conf_list)
                            # Extract nose info for logging
                            if len(kp_list) > 0:
                                nose_x, nose_y = kp_list[0]
                                nose_confidence = conf_list[0] if len(conf_list) > 0 else 0.0
                            lookup_success = True
                            lookup_failure_reason = None
                        else:
                            lookup_failure_reason = "keypoints_conf_mismatch"
                    else:
                        lookup_failure_reason = "missing_keypoints_or_conf"
                else:
                    lookup_failure_reason = "track_id_not_found"
            else:
                # Fallback for list format (if structure changes)
                available_pose_track_ids = [p.track_id for p in context.poses if hasattr(p, "track_id")]
                for pose in context.poses:
                    if hasattr(pose, "track_id") and int(pose.track_id) == track_id:
                        if hasattr(pose, "keypoints") and hasattr(pose, "keypoint_confidences"):
                            kp_list = pose.keypoints
                            conf_list = pose.keypoint_confidences
                            if kp_list and conf_list and len(kp_list) == len(conf_list):
                                keypoints_array = np.zeros((len(kp_list), 3), dtype=np.float32)
                                for i, (kp, conf) in enumerate(zip(kp_list, conf_list)):
                                    keypoints_array[i, 0] = kp[0]
                                    keypoints_array[i, 1] = kp[1]
                                    keypoints_array[i, 2] = conf
                                pose_data = {"keypoints": keypoints_array}
                                pose_result_type = type(pose).__name__
                                keypoints_shape = keypoints_array.shape
                                keypoint_confidences_shape = len(conf_list)
                                if len(kp_list) > 0:
                                    nose_x, nose_y = kp_list[0]
                                    nose_confidence = conf_list[0] if len(conf_list) > 0 else 0.0
                                lookup_success = True
                                lookup_failure_reason = None
                                break
                        else:
                            lookup_failure_reason = "missing_keypoints_or_conf"
                if not lookup_success:
                    lookup_failure_reason = "track_id_not_found_in_list"
        else:
            lookup_failure_reason = "no_poses_attribute"

        # Debug log for pose lookup
        logger.info(
            "[HEAD-POSE POSE LOOKUP] frame=%d head_pose_track_id=%d available_pose_track_ids=%s pose_result_type=%s keypoints_shape=%s keypoint_confidences_shape=%s nose_x=%.1f nose_y=%.1f nose_confidence=%.2f lookup_success=%s lookup_failure_reason=%s",
            context.frame_number, track_id, available_pose_track_ids, pose_result_type, keypoints_shape, keypoint_confidences_shape, nose_x, nose_y, nose_confidence, lookup_success, lookup_failure_reason,
        )

        # ------------------------------------------------------------------ #
        # 2. Locate face region                                                #
        # ------------------------------------------------------------------ #
        face_bbox = await self._locator.locate(
            track_id, track.bbox, pose_data, context.frame.shape[:2]
        )

        # ------------------------------------------------------------------ #
        # 3. Crop face and validate                                            #
        # ------------------------------------------------------------------ #
        crop = await self._cropper.crop(context.frame, face_bbox, track_id)
        if crop is None or crop.size == 0:
            logger.warning(
                "[HEAD-POSE TRACE] frame=%d track_id=%d empty_crop=True face_bbox=%s",
                context.frame_number, track_id, face_bbox,
            )
            return None
        face_crop_shape = tuple(crop.shape)          # (H, W, C)

        # Determine crop source for logging
        crop_source = "unknown"
        visible_facial_keypoints = 0
        if pose_data is not None and "keypoints" in pose_data:
            keypoints = pose_data["keypoints"]
            # Count visible facial keypoints (nose, eyes, ears)
            # keypoints is (N, 3) array: [x, y, confidence]
            facial_indices = [0, 1, 2, 3, 4]
            for idx in facial_indices:
                if idx < len(keypoints) and keypoints[idx, 2] >= 0.5:
                    visible_facial_keypoints += 1
            if visible_facial_keypoints >= 2:
                crop_source = "facial_keypoints"
            else:
                crop_source = "track_bbox_fallback"
        else:
            crop_source = "track_bbox_fallback"

        logger.info(
            "[HEAD-POSE TRACE] frame=%d track_id=%d face_bbox=%s person_bbox=%s crop_shape=%s crop_source=%s visible_facial_keypoints=%d",
            context.frame_number, track_id, face_bbox, tuple(track.bbox), face_crop_shape, crop_source, visible_facial_keypoints,
        )

        # ------------------------------------------------------------------ #
        # 4. Run SixDRepNet inference                                          #
        # ------------------------------------------------------------------

        # Rotation matrix returned by estimator, shape (3, 3)
        rotation_matrix = await self._estimator.estimate(crop, track_id)
        inference_timestamp = time.monotonic()
        inference_executed = True

        yaw, pitch, roll = await self._parser.parse(rotation_matrix, track_id)

        logger.info(
            "[HEAD-POSE TRACE] frame=%d track_id=%d inference_executed=%s raw_yaw=%.2f raw_pitch=%.2f raw_roll=%.2f",
            context.frame_number, track_id, inference_executed, yaw, pitch, roll,
        )

        # ------------------------------------------------------------------ #
        # 5. Validate result                                                   #
        # ------------------------------------------------------------------ #
        is_valid = await self._validator.validate(
            track_id, face_bbox, yaw, pitch, roll
        )

        logger.info(
            "[HEAD-POSE TRACE] frame=%d track_id=%d is_valid=%s",
            context.frame_number, track_id, is_valid,
        )

        # ------------------------------------------------------------------ #
        # 6. Apply temporal smoothing with reliability gate                    #
        # ------------------------------------------------------------------ #
        raw_yaw, raw_pitch, raw_roll = yaw, pitch, roll
        
        # Lightweight reliability check before smoothing
        smoothing_updated = False
        smoothing_skip_reason = None
        
        # Check for non-finite model output
        if not (np.isfinite(raw_yaw) and np.isfinite(raw_pitch) and np.isfinite(raw_roll)):
            smoothing_skip_reason = "non_finite_model_output"
        # Check for empty or too small crop
        elif face_crop_shape[0] < 32 or face_crop_shape[1] < 32:
            smoothing_skip_reason = "crop_too_small"
        # Check for excessively large crop compared to person bbox
        elif face_bbox:
            person_area = (track.bbox[2] - track.bbox[0]) * (track.bbox[3] - track.bbox[1])
            face_area = (face_bbox[2] - face_bbox[0]) * (face_bbox[3] - face_bbox[1])
            if person_area > 0 and face_area > person_area * 0.5:
                smoothing_skip_reason = "crop_too_large"
        
        if self._temporal_smoother is not None and smoothing_skip_reason is None:
            # Get previous values for logging
            previous_yaw = previous_pitch = previous_roll = None
            if self._temporal_smoother.has_track(track_id):
                state = self._temporal_smoother._states.get(track_id)
                if state:
                    previous_yaw = state.yaw
                    previous_pitch = state.pitch
                    previous_roll = state.roll
            
            yaw, pitch, roll = self._temporal_smoother.smooth(
                track_id, raw_yaw, raw_pitch, raw_roll, context.frame_number
            )
            smoothing_updated = True
            
            # Comprehensive smoothing trace log
            logger.info(
                "[HEAD-POSE SMOOTHING TRACE] "
                "frame=%d track_id=%d "
                "raw_yaw=%.2f raw_pitch=%.2f raw_roll=%.2f "
                "previous_yaw=%s previous_pitch=%s previous_roll=%s "
                "smoothed_yaw=%.2f smoothed_pitch=%.2f smoothed_roll=%.2f "
                "alpha=%.2f smoother_id=%d smoothing_updated=%s",
                context.frame_number, track_id,
                raw_yaw, raw_pitch, raw_roll,
                f"{previous_yaw:.2f}" if previous_yaw is not None else "None",
                f"{previous_pitch:.2f}" if previous_pitch is not None else "None",
                f"{previous_roll:.2f}" if previous_roll is not None else "None",
                yaw, pitch, roll,
                self._temporal_smoother._alpha if self._temporal_smoother._enabled else 0.0,
                id(self._temporal_smoother),
                smoothing_updated,
            )
        elif self._temporal_smoother is not None and smoothing_skip_reason is not None:
            # Skip smoothing update, preserve previous state
            previous_yaw = previous_pitch = previous_roll = None
            if self._temporal_smoother.has_track(track_id):
                state = self._temporal_smoother._states.get(track_id)
                if state:
                    previous_yaw = state.yaw
                    previous_pitch = state.pitch
                    previous_roll = state.roll
                    yaw, pitch, roll = previous_yaw, previous_pitch, previous_roll
            
            logger.info(
                "[HEAD-POSE SMOOTHING TRACE] "
                "frame=%d track_id=%d "
                "raw_yaw=%.2f raw_pitch=%.2f raw_roll=%.2f "
                "previous_yaw=%s previous_pitch=%s previous_roll=%s "
                "smoothed_yaw=%.2f smoothed_pitch=%.2f smoothed_roll=%.2f "
                "alpha=%.2f smoother_id=%d smoothing_updated=False skip_reason=%s",
                context.frame_number, track_id,
                raw_yaw, raw_pitch, raw_roll,
                f"{previous_yaw:.2f}" if previous_yaw is not None else "None",
                f"{previous_pitch:.2f}" if previous_pitch is not None else "None",
                f"{previous_roll:.2f}" if previous_roll is not None else "None",
                yaw, pitch, roll,
                self._temporal_smoother._alpha if self._temporal_smoother._enabled else 0.0,
                id(self._temporal_smoother),
                smoothing_skip_reason,
            )
        else:
            # No smoothing - raw equals smoothed
            yaw, pitch, roll = raw_yaw, raw_pitch, raw_roll
            logger.info(
                "[HEAD-POSE SMOOTHING TRACE] "
                "frame=%d track_id=%d "
                "raw_yaw=%.2f raw_pitch=%.2f raw_roll=%.2f "
                "previous_yaw=None previous_pitch=None previous_roll=None "
                "smoothed_yaw=%.2f smoothed_pitch=%.2f smoothed_roll=%.2f "
                "alpha=0.0 smoother_id=None smoothing_updated=False skip_reason=smoother_disabled",
                context.frame_number, track_id,
                raw_yaw, raw_pitch, raw_roll,
                yaw, pitch, roll,
            )

        # ------------------------------------------------------------------ #
        # 7. Compute axis origin (nose → face centre → upper-person centre)   #
        # ------------------------------------------------------------------ #
        axis_origin = self._compute_axis_origin(
            pose_data, face_bbox, track.bbox, frame_h, frame_w
        )

        # Determine axis source for logging
        axis_source = "unknown"
        if pose_data is not None and "keypoints" in pose_data:
            keypoints = pose_data["keypoints"]
            # keypoints is (N, 3) array: [x, y, confidence]
            if _NOSE_KP_INDEX < len(keypoints):
                nose_confidence = keypoints[_NOSE_KP_INDEX, 2]
                if nose_confidence >= _NOSE_CONF_THRESHOLD:
                    axis_source = "nose"
                else:
                    axis_source = "head_crop_center"
            else:
                axis_source = "head_crop_center"
        else:
            axis_source = "head_crop_center"

        # Fallback to person bbox if face bbox is invalid
        fx1, fy1, fx2, fy2 = face_bbox
        if not (fx2 > fx1 and fy2 > fy1):
            axis_source = "person_fallback"

        logger.info(
            "[HEAD-POSE TRACE] frame=%d track_id=%d axis_origin=%s axis_source=%s",
            context.frame_number, track_id, axis_origin, axis_source,
        )

        # ------------------------------------------------------------------ #
        # 8. Diagnostic logs (gated on config flags)                          #
        # ------------------------------------------------------------------ #
        cfg = self._config
        debug_data_path   = cfg is not None and cfg.debug_log_data_path
        debug_freshness   = cfg is not None and cfg.debug_trace_frame_freshness
        debug_crop_crc    = cfg is not None and cfg.debug_crop_checksums

        logger.debug(
            "track_id=%d  frame=%d  roll=%.1f  yaw=%.1f  pitch=%.1f  "
            "axis_origin=%s  face_bbox=%s",
            track_id, context.frame_number,
            roll, yaw, pitch, axis_origin, face_bbox,
        )

        if debug_data_path:
            self._log_data_path(
                frame_index=context.frame_number,
                track_id=track_id,
                person_bbox=tuple(track.bbox),
                face_bbox=face_bbox,
                face_crop_shape=face_crop_shape,
                rotation_matrix=rotation_matrix,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                axis_origin=axis_origin,
            )

        if debug_freshness:
            self._log_freshness_trace(
                frame=context.frame,
                crop=crop,
                frame_index=context.frame_number,
                track_id=track_id,
                face_bbox=face_bbox,
                face_crop_shape=face_crop_shape,
                rotation_matrix=rotation_matrix,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                inference_call_count=self._estimator.inference_call_count,
                do_crop_crc=debug_crop_crc,
            )

        # ------------------------------------------------------------------ #
        # 9. Build result — stamp frame identity                              #
        # ------------------------------------------------------------------ #
        result = HeadPoseResult(
            track_id=track_id,
            face_bbox=face_bbox,
            raw_yaw=raw_yaw,
            raw_pitch=raw_pitch,
            raw_roll=raw_roll,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            is_valid=is_valid,
            person_bbox=tuple(track.bbox),
            axis_origin=axis_origin,
            frame_index=context.frame_number,
            source_timestamp=inference_timestamp,
        )

        logger.info(
            "[HEAD-POSE TRACE] frame=%d track_id=%d result_created=True result_id=%d is_valid=%s",
            context.frame_number, track_id, id(result), result.is_valid,
        )

        return result

    # ---------------------------------------------------------------------- #
    # Private helpers                                                          #
    # ---------------------------------------------------------------------- #

    def _log_freshness_trace(
        self,
        frame: np.ndarray,
        crop: np.ndarray,
        frame_index: int,
        track_id: int,
        face_bbox: Tuple[float, float, float, float],
        face_crop_shape: tuple,
        rotation_matrix: np.ndarray,
        yaw: float,
        pitch: float,
        roll: float,
        inference_call_count: int,
        do_crop_crc: bool,
    ) -> None:
        """Emit [HEAD-POSE TRACE] log for frame-freshness diagnosis."""
        frame_crc = zlib.crc32(frame.tobytes()) & 0xFFFF_FFFF
        crop_crc  = (zlib.crc32(crop.tobytes()) & 0xFFFF_FFFF) if do_crop_crc else -1

        logger.debug(
            "[HEAD-POSE TRACE]\n"
            "  frame_index         : %d\n"
            "  track_id            : %d\n"
            "  frame_object_id     : %d\n"
            "  frame_checksum      : %d\n"
            "  face_bbox           : %s\n"
            "  crop_object_id      : %d\n"
            "  crop_checksum       : %s\n"
            "  crop_shape          : %s\n"
            "  inference_call_no   : %d\n"
            "  raw_pitch_deg       : %.4f\n"
            "  raw_yaw_deg         : %.4f\n"
            "  raw_roll_deg        : %.4f",
            frame_index,
            track_id,
            id(frame),
            frame_crc,
            "(%.1f, %.1f, %.1f, %.1f)" % tuple(float(v) for v in face_bbox),
            id(crop),
            str(crop_crc) if do_crop_crc else "disabled",
            face_crop_shape,
            inference_call_count,
            pitch,
            yaw,
            roll,
        )

    def _log_data_path(
        self,
        frame_index: int,
        track_id: int,
        person_bbox: Tuple[float, float, float, float],
        face_bbox: Tuple[float, float, float, float],
        face_crop_shape: tuple,
        rotation_matrix: np.ndarray,
        yaw: float,
        pitch: float,
        roll: float,
        axis_origin: Tuple[int, int],
    ) -> None:
        """Emit a full data-path log record for every tracked face.

        Each field maps to one pipeline stage:

        Stage               Field
        ----------------    -----------------------------------------
        Context             frame_index
        DeepSORT            track_id, person_bbox
        FaceLocator         face_bbox
        FaceCropper         face_crop_shape
        Estimator           rotation_matrix (3x3, det ≈ 1)
        Parser              raw_yaw, raw_pitch, raw_roll (degrees)
        TrackProcessor      axis_origin

        Args:
            frame_index: FrameContext.frame_number.
            track_id: DeepSORT track ID.
            person_bbox: Person bbox (x1,y1,x2,y2).
            face_bbox: Face bbox (x1,y1,x2,y2).
            face_crop_shape: Crop shape (H,W,C).
            rotation_matrix: Raw 3x3 rotation matrix from 6DRepNet.
            yaw: Parsed yaw in degrees.
            pitch: Parsed pitch in degrees.
            roll: Parsed roll in degrees.
            axis_origin: Clamped (cx,cy) for 3-D axis origin.
        """
        logger.debug(
            "[HEAD-POSE DATA PATH]\n"
            "  frame_index       : %d\n"
            "  track_id          : %d\n"
            "  person_bbox       : %s\n"
            "  face_bbox         : %s\n"
            "  face_crop_shape   : %s  (H x W x C)\n"
            "  rotation_matrix   :\n%s\n"
            "  det(R)            : %.6f\n"
            "  raw_yaw           : %.4f deg\n"
            "  raw_pitch         : %.4f deg\n"
            "  raw_roll          : %.4f deg\n"
            "  axis_origin       : %s",
            frame_index,
            track_id,
            "(%.1f, %.1f, %.1f, %.1f)" % tuple(float(v) for v in person_bbox),
            "(%.1f, %.1f, %.1f, %.1f)" % tuple(float(v) for v in face_bbox),
            face_crop_shape,
            rotation_matrix,
            float(np.linalg.det(rotation_matrix)),
            yaw,
            pitch,
            roll,
            axis_origin,
        )


    def _compute_axis_origin(
        self,
        pose_data: Optional[dict],
        face_bbox: Tuple[float, float, float, float],
        track_bbox: Tuple[float, float, float, float],
        frame_h: int,
        frame_w: int,
    ) -> Tuple[int, int]:
        """Compute the clamped pixel origin for the 3-D head-pose axis.

        Priority:
        1. Nose keypoint (COCO index 0) if confidence >= threshold.
        2. Centre of the face bounding box.
        3. Upper-centre of the person bounding box.

        Args:
            pose_data: Dict with ``keypoints`` array (shape N×3, x/y/conf).
            face_bbox: Face bounding box (x1, y1, x2, y2).
            track_bbox: Person bounding box (x1, y1, x2, y2).
            frame_h: Frame height in pixels.
            frame_w: Frame width in pixels.

        Returns:
            Clamped (cx, cy) integer pixel coordinates.
        """
        # --- Priority 1: reliable nose keypoint ---
        if pose_data is not None and "keypoints" in pose_data:
            kps = pose_data["keypoints"]
            if (
                isinstance(kps, np.ndarray)
                and kps.ndim == 2
                and kps.shape[0] > _NOSE_KP_INDEX
                and kps.shape[1] >= 3
            ):
                nose = kps[_NOSE_KP_INDEX]
                if float(nose[2]) >= _NOSE_CONF_THRESHOLD:
                    cx = int(nose[0])
                    cy = int(nose[1])
                    return (
                        max(0, min(cx, frame_w - 1)),
                        max(0, min(cy, frame_h - 1)),
                    )

        # --- Priority 2: face-bbox centre ---
        fx1, fy1, fx2, fy2 = face_bbox
        if fx2 > fx1 and fy2 > fy1:
            cx = int((fx1 + fx2) / 2)
            cy = int((fy1 + fy2) / 2)
            return (
                max(0, min(cx, frame_w - 1)),
                max(0, min(cy, frame_h - 1)),
            )

        # --- Priority 3: upper-centre of person bbox ---
        px1, py1, px2, py2 = track_bbox
        cx = int((px1 + px2) / 2)
        cy = int(py1 + (py2 - py1) * 0.15)
        return (
            max(0, min(cx, frame_w - 1)),
            max(0, min(cy, frame_h - 1)),
        )


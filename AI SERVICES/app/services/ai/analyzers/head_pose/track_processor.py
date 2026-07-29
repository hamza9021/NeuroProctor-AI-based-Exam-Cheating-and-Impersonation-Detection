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
    ):
        """Initialize track processor.

        Args:
            locator: Face locator.
            cropper: Face cropper.
            estimator: Head pose estimator.
            parser: Output parser.
            validator: Result validator.
            config: Head pose configuration (used to gate diagnostic logging).
        """
        self._locator = locator
        self._cropper = cropper
        self._estimator = estimator
        self._parser = parser
        self._validator = validator
        self._config = config

    async def process(self, context: FrameContext, track) -> HeadPoseResult:
        """Process a single track.

        Args:
            context: FrameContext containing the current frame and poses.
            track: DeepSORT track object with ``track_id`` and ``bbox``.

        Returns:
            HeadPoseResult with all visualization fields populated.
        """
        frame_h, frame_w = context.frame.shape[:2]

        # ------------------------------------------------------------------ #
        # 1. Gather pose data for this specific track                         #
        # ------------------------------------------------------------------ #
        pose_data: Optional[dict] = None
        if hasattr(context, "poses"):
            for pose in context.poses:
                if hasattr(pose, "track_id") and pose.track_id == track.track_id:
                    pose_data = {"keypoints": pose.keypoints}
                    break

        # ------------------------------------------------------------------ #
        # 2. Locate face region                                                #
        # ------------------------------------------------------------------ #
        face_bbox = await self._locator.locate(
            track.track_id, track.bbox, pose_data, context.frame.shape[:2]
        )

        # ------------------------------------------------------------------ #
        # 3. Crop face and run inference                                       #
        # ------------------------------------------------------------------ #
        crop = await self._cropper.crop(context.frame, face_bbox, track.track_id)
        face_crop_shape = tuple(crop.shape)          # (H, W, C)

        # Rotation matrix returned by estimator, shape (3, 3)
        rotation_matrix = await self._estimator.estimate(crop, track.track_id)
        inference_timestamp = time.monotonic()

        yaw, pitch, roll = await self._parser.parse(rotation_matrix, track.track_id)

        # ------------------------------------------------------------------ #
        # 4. Validate result                                                   #
        # ------------------------------------------------------------------ #
        is_valid = await self._validator.validate(
            track.track_id, face_bbox, yaw, pitch, roll
        )

        # ------------------------------------------------------------------ #
        # 5. Compute axis origin (nose → face centre → upper-person centre)   #
        # ------------------------------------------------------------------ #
        axis_origin = self._compute_axis_origin(
            pose_data, face_bbox, track.bbox, frame_h, frame_w
        )

        # ------------------------------------------------------------------ #
        # 6. Diagnostic logs (gated on config flags)                          #
        # ------------------------------------------------------------------ #
        cfg = self._config
        debug_data_path   = cfg is not None and cfg.debug_log_data_path
        debug_freshness   = cfg is not None and cfg.debug_trace_frame_freshness
        debug_crop_crc    = cfg is not None and cfg.debug_crop_checksums

        logger.debug(
            "track_id=%d  frame=%d  roll=%.1f  yaw=%.1f  pitch=%.1f  "
            "axis_origin=%s  face_bbox=%s",
            track.track_id, context.frame_number,
            roll, yaw, pitch, axis_origin, face_bbox,
        )

        if debug_data_path:
            self._log_data_path(
                frame_index=context.frame_number,
                track_id=track.track_id,
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
                track_id=track.track_id,
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
        # 7. Build result — stamp frame identity                              #
        # ------------------------------------------------------------------ #
        return HeadPoseResult(
            track_id=track.track_id,
            face_bbox=face_bbox,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            is_valid=is_valid,
            person_bbox=tuple(track.bbox),
            axis_origin=axis_origin,
            frame_index=context.frame_number,
            source_timestamp=inference_timestamp,
        )

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


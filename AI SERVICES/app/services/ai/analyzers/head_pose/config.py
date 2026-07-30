"""Configuration for 6DRepNet head pose estimation."""

from dataclasses import dataclass


@dataclass
class HeadPoseConfig:
    """Configuration for head pose estimation.

    Attributes:
        model_path: Path to 6DRepNet model weights.
        device: Device for inference ('auto', 'cuda', 'cpu').
        input_size: Input image size for model (default 224).
        face_padding: Padding around face crop (0.0 to 1.0).
        min_face_size: Minimum face size in pixels.
        max_abs_angle: Maximum absolute angle in degrees.
        annotation_enabled: Whether to draw annotations.
        draw_axis: Whether to draw orientation axis.
        axis_length: Length of orientation axis in pixels.
        log_level: Logging detail level ('summary', 'detailed', 'debug').
        frame_log_interval: Emit detailed logs every N frames.
        debug_log_data_path: When True, emit a full structured log of the
            complete head-pose data path (face_bbox, crop shape,
            raw_rotation_matrix, raw angles, smoothed angles, axis_origin)
            for every tracked face on every frame.  Set to True to diagnose
            pitch/yaw estimation problems.  Defaults to False.
    """

    model_path: str = "models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth"
    device: str = "auto"
    input_size: int = 224
    face_padding: float = 0.20
    min_face_size: int = 40
    max_abs_angle: float = 90.0
    annotation_enabled: bool = True
    draw_axis: bool = True
    axis_length: int = 50
    log_level: str = "detailed"
    frame_log_interval: int = 10
    debug_log_data_path: bool = False
    # Square crop parameters for stable head pose estimation
    minimum_head_size: int = 80
    head_padding_scale: float = 1.5
    vertical_center_ratio: float = 0.4
    # ------------------------------------------------------------------ #
    # Diagnostic flags — all default False.                               #
    # Enable selectively to trace freshness bugs; never leave True in     #
    # production because checksumming every frame/crop is expensive.      #
    # ------------------------------------------------------------------ #
    debug_trace_frame_freshness: bool = False
    """Emit one [HEAD-POSE TRACE] log per face per frame with frame/crop
    checksums, object ids, and inference counter."""
    debug_crop_checksums: bool = False
    """Include CRC32 checksums of the face crop in freshness logs."""
    debug_tensor_checksums: bool = False
    """Include tensor statistics and checksum in freshness logs."""
    debug_reject_stale_results: bool = True
    """Skip rendering a HeadPoseResult whose frame_index differs from the
    current FrameContext.frame_number.  Enabled by default."""



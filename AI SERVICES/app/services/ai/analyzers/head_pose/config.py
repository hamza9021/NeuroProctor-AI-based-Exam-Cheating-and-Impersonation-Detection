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
        log_level: Logging detail level.
        frame_log_interval: Emit detailed logs every N frames.
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

"""DeepSORT configuration."""

from dataclasses import dataclass

from app.services.ai.trackers.deepsort.constants import (
    DEFAULT_FRAME_LOG_INTERVAL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_AGE,
    DEFAULT_MAX_COSINE_DISTANCE,
    DEFAULT_MAX_IOU_DISTANCE,
    DEFAULT_N_INIT,
    DEFAULT_NN_BUDGET,
)


@dataclass
class DeepSORTConfig:
    """Configuration for DeepSORT tracking.
    
    Stores only configuration parameters. No logic.
    """
    
    max_age: int = DEFAULT_MAX_AGE
    """Maximum number of frames to keep a track alive."""
    
    n_init: int = DEFAULT_N_INIT
    """Number of consecutive detections before track is confirmed."""
    
    max_iou_distance: float = DEFAULT_MAX_IOU_DISTANCE
    """Maximum IOU distance for matching."""
    
    max_cosine_distance: float = DEFAULT_MAX_COSINE_DISTANCE
    """Maximum cosine distance for appearance matching."""
    
    nn_budget: int = DEFAULT_NN_BUDGET
    """Maximum size of the appearance feature gallery."""
    
    embedding_model: str = "mars-small128.pb"
    """ReID model path for feature extraction."""
    
    embedding_size: int = 128
    """Size of the embedding vector."""
    
    device: str = "auto"
    """Device for inference: 'auto', 'cuda', or 'cpu'."""
    
    detection_confidence_threshold: float = 0.3
    """Minimum confidence for detections to be tracked."""
    
    use_half_precision: bool = True
    """Use half precision for faster inference."""
    
    socket_log_detail_level: str = DEFAULT_LOG_LEVEL
    """Log level: 'summary', 'detailed', or 'debug'."""
    
    frame_log_interval: int = DEFAULT_FRAME_LOG_INTERVAL
    """Emit detailed frame logs every N frames."""
    
    annotation_required: bool = False
    """Whether annotation is mandatory or optional."""

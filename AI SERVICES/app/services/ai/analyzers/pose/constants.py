"""Constants for YOLO pose estimation."""

# COCO 17 body keypoints
KEYPOINT_NAMES = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]

# Skeleton connections (keypoint index pairs)
SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),  # Head
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
    (5, 11), (6, 12), (11, 12),  # Torso
    (11, 13), (13, 15), (12, 14), (14, 16),  # Legs
]

# Socket.IO event names
EVENT_POSE_INITIALIZATION_STARTED = "pose_initialization_started"
EVENT_POSE_MODEL_LOADING = "pose_model_loading"
EVENT_POSE_DEVICE_SELECTED = "pose_device_selected"
EVENT_POSE_INITIALIZED = "pose_initialized"
EVENT_POSE_STAGE_STARTED = "pose_stage_started"
EVENT_POSE_FRAME_RECEIVED = "pose_frame_received"
EVENT_POSE_TRACKS_RECEIVED = "pose_tracks_received"
EVENT_POSE_INFERENCE_STARTED = "pose_inference_started"
EVENT_POSE_INFERENCE_COMPLETED = "pose_inference_completed"
EVENT_POSE_CANDIDATES_PARSED = "pose_candidates_parsed"
EVENT_POSE_CANDIDATES_VALIDATED = "pose_candidates_validated"
EVENT_POSE_TRACK_MATCH_STARTED = "pose_track_match_started"
EVENT_POSE_TRACK_MATCHED = "pose_track_matched"
EVENT_POSE_TRACK_UNMATCHED = "pose_track_unmatched"
EVENT_POSE_MAPPING_COMPLETED = "pose_mapping_completed"
EVENT_POSE_ANNOTATION_STARTED = "pose_annotation_started"
EVENT_POSE_ANNOTATION_COMPLETED = "pose_annotation_completed"
EVENT_POSE_FRAME_COMPLETED = "pose_frame_completed"
EVENT_POSE_STAGE_COMPLETED = "pose_stage_completed"
EVENT_POSE_WARNING = "pose_warning"
EVENT_POSE_FAILED = "pose_failed"

# Log levels
LOG_LEVEL_SUMMARY = "summary"
LOG_LEVEL_DETAILED = "detailed"
LOG_LEVEL_DEBUG = "debug"

# Default log level
DEFAULT_LOG_LEVEL = LOG_LEVEL_DETAILED

# Default frame log interval
DEFAULT_FRAME_LOG_INTERVAL = 10

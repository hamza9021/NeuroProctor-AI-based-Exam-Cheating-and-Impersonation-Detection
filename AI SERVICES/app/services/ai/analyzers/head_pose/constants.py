"""Constants for 6DRepNet head pose estimation."""

# Stage name
STAGE_NAME = "sixdrepnet_head_pose"

# Socket.IO event names
EVENT_INITIALIZATION_STARTED = "head_pose_initialization_started"
EVENT_MODEL_LOADING = "head_pose_model_loading"
EVENT_DEVICE_SELECTED = "head_pose_device_selected"
EVENT_INITIALIZED = "head_pose_initialized"
EVENT_STAGE_STARTED = "head_pose_stage_started"
EVENT_FRAME_RECEIVED = "head_pose_frame_received"
EVENT_TRACKS_RECEIVED = "head_pose_tracks_received"
EVENT_FACE_LOCATION_STARTED = "head_pose_face_location_started"
EVENT_FACE_REGION_FOUND = "head_pose_face_region_found"
EVENT_FACE_REGION_MISSING = "head_pose_face_region_missing"
EVENT_CROP_CREATED = "head_pose_crop_created"
EVENT_INFERENCE_STARTED = "head_pose_inference_started"
EVENT_INFERENCE_COMPLETED = "head_pose_inference_completed"
EVENT_RESULT_PARSED = "head_pose_result_parsed"
EVENT_RESULT_VALIDATED = "head_pose_result_validated"
EVENT_RESULT_MAPPED = "head_pose_result_mapped"
EVENT_ANNOTATION_STARTED = "head_pose_annotation_started"
EVENT_ANNOTATION_COMPLETED = "head_pose_annotation_completed"
EVENT_FRAME_COMPLETED = "head_pose_frame_completed"
EVENT_STAGE_COMPLETED = "head_pose_stage_completed"
EVENT_WARNING = "head_pose_warning"
EVENT_FAILED = "head_pose_failed"

# Axis names
AXIS_YAW = "yaw"
AXIS_PITCH = "pitch"
AXIS_ROLL = "roll"

# Valid angle names
VALID_ANGLES = [AXIS_YAW, AXIS_PITCH, AXIS_ROLL]

# Default annotation labels
LABEL_YAW = "Yaw"
LABEL_PITCH = "Pitch"
LABEL_ROLL = "Roll"

# Log levels
LOG_LEVEL_SUMMARY = "summary"
LOG_LEVEL_DETAILED = "detailed"
LOG_LEVEL_DEBUG = "debug"

# Default log level
DEFAULT_LOG_LEVEL = LOG_LEVEL_DETAILED

# Default frame log interval
DEFAULT_FRAME_LOG_INTERVAL = 10

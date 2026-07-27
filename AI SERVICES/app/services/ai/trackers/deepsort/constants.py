"""Constants for DeepSORT tracking."""

# Target class for tracking
TARGET_CLASS = "person"

# Default tracking parameters
DEFAULT_MAX_AGE = 70
DEFAULT_N_INIT = 3
DEFAULT_MAX_IOU_DISTANCE = 0.7
DEFAULT_MAX_COSINE_DISTANCE = 0.2
DEFAULT_NN_BUDGET = 100

# ReID model
DEFAULT_EMBEDDING_MODEL = "mars-small128.pb"
DEFAULT_EMBEDDING_SIZE = 128

# Bounding box constraints
MIN_BBOX_AREA = 100
MAX_BBOX_AREA = 1000000

# Track state thresholds
MIN_HITS_TO_CONFIRM = 3
MAX_TIME_SINCE_UPDATE = 30

# Socket.IO event names
EVENT_TRACKING_INITIALIZATION_STARTED = "tracking_initialization_started"
EVENT_TRACKING_MODEL_LOADING = "tracking_model_loading"
EVENT_TRACKING_DEVICE_SELECTED = "tracking_device_selected"
EVENT_TRACKING_INITIALIZED = "tracking_initialized"
EVENT_TRACKING_STAGE_STARTED = "tracking_stage_started"
EVENT_TRACKING_FRAME_RECEIVED = "tracking_frame_received"
EVENT_TRACKING_DETECTIONS_RECEIVED = "tracking_detections_received"
EVENT_TRACKING_PERSON_DETECTIONS_FILTERED = "tracking_person_detections_filtered"
EVENT_TRACKING_UPDATE_STARTED = "tracking_update_started"
EVENT_TRACKING_UPDATE_COMPLETED = "tracking_update_completed"
EVENT_TRACK_CREATED = "track_created"
EVENT_TRACK_CONFIRMED = "track_confirmed"
EVENT_TRACK_UPDATED = "track_updated"
EVENT_TRACK_TEMPORARILY_LOST = "track_temporarily_lost"
EVENT_TRACK_RECOVERED = "track_recovered"
EVENT_TRACK_REMOVED = "track_removed"
EVENT_TRACKING_ANNOTATION_STARTED = "tracking_annotation_started"
EVENT_TRACKING_ANNOTATION_COMPLETED = "tracking_annotation_completed"
EVENT_TRACKING_ANNOTATION_FAILED = "tracking_annotation_failed"
EVENT_TRACKING_FRAME_COMPLETED = "tracking_frame_completed"
EVENT_TRACKING_STAGE_COMPLETED = "tracking_stage_completed"
EVENT_TRACKING_WARNING = "tracking_warning"
EVENT_TRACKING_FAILED = "tracking_failed"

# Log levels
LOG_LEVEL_SUMMARY = "summary"
LOG_LEVEL_DETAILED = "detailed"
LOG_LEVEL_DEBUG = "debug"

# Default log level
DEFAULT_LOG_LEVEL = LOG_LEVEL_DETAILED

# Frame log interval (emit detailed logs every N frames)
DEFAULT_FRAME_LOG_INTERVAL = 10

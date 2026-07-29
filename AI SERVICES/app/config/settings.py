"""
Application-wide settings loaded from environment variables.

Uses Pydantic BaseSettings so that:
  1. Every variable is declared with a Python type (type-safety at startup).
  2. Values are read from the .env file automatically.
  3. Missing required variables raise a clear ValidationError on startup
     (fail-fast rather than failing at first use).

Access settings anywhere via the module-level singleton:
    from app.config.settings import settings
"""
from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All environment-configurable application settings."""

    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True
    APP_TITLE: str = "NeuroProctor AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "AI-powered student face registration and impersonation detection service "
        "for the NeuroProctor exam integrity platform."
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Must match the React frontend origin exactly (no trailing slash).
    CORS_ORIGIN: str = "http://localhost:5173"

    # ── Express Backend ───────────────────────────────────────────────────────
    # URL of the Express backend for API communication
    EXPRESS_BACKEND_URL: str = "http://localhost:8080"

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://localhost:27017/neuroproctor"
    MONGO_DB_NAME: str = "neuroproctor"

    # ── JWT ───────────────────────────────────────────────────────────────────
    # ACCESS_TOKEN_SECRET MUST be identical to the Express backend secret.
    # No default is provided so that a missing value raises an error at startup.
    ACCESS_TOKEN_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # ── Cloudinary ────────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_STUDENT_FOLDER: str = "neuroproctor/students"

    # ── InsightFace / ONNX ────────────────────────────────────────────────────
    INSIGHTFACE_MODEL_NAME: str = "buffalo_l"
    # ctx_id: 0 = first GPU device.  -1 forces CPU-only.
    INSIGHTFACE_CTX_ID: int = 0
    # Detection input size in pixels (square). 640 is the recommended default.
    INSIGHTFACE_DET_SIZE: int = 640

    # ── YOLO Object Detection ───────────────────────────────────────────────────
    # YOLO model to use (will be downloaded by ultralytics if not found)
    YOLO_MODEL: str = "yolov8m.pt"
    # Device for inference: "auto", "cuda", "cpu", or specific GPU index like "cuda:0"
    YOLO_DEVICE: str = "auto"
    # Confidence threshold for detections (0.0 to 1.0)
    YOLO_CONFIDENCE: float = 0.25
    # IOU threshold for NMS (0.0 to 1.0)
    YOLO_IOU: float = 0.45
    # Image size for inference (square, in pixels)
    YOLO_IMAGE_SIZE: int = 640
    # Enable verbose logging from ultralytics
    YOLO_VERBOSE: bool = False

    # ── Phone Detection ─────────────────────────────────────────────────────────
    # Phone detection enabled
    PHONE_DETECTION_ENABLED: bool = True
    # Dedicated phone model path (empty to use main YOLO model)
    PHONE_MODEL_PATH: str = ""
    # Phone class name to detect
    PHONE_CLASS_NAME: str = "cell phone"
    # Phone-specific confidence threshold
    PHONE_CONFIDENCE: float = 0.10
    # Phone inference image size
    PHONE_IMAGE_SIZE: int = 960
    # Fallback image sizes for GPU memory constraints (comma-separated)
    PHONE_FALLBACK_IMAGE_SIZES: str = "768,640"
    # Minimum phone bounding box area
    PHONE_MIN_BOX_AREA: int = 10
    # Enable student ROI phone detection
    PHONE_ROI_ENABLED: bool = True
    # ROI expansion factor (0.15 = 15% expansion)
    PHONE_ROI_EXPANSION: float = 0.15
    # Frames to confirm a phone detection
    PHONE_TEMPORAL_CONFIRM_FRAMES: int = 3
    # Max missed frames before expiration
    PHONE_TEMPORAL_MAX_MISSED_FRAMES: int = 2
    # IoU threshold for student-phone association
    PHONE_ASSOCIATION_IOU: float = 0.10
    # IoU threshold for phone deduplication
    PHONE_DEDUPLICATION_IOU: float = 0.50
    # Debug mode for phone detection
    PHONE_DEBUG_ENABLED: bool = False
    # Max debug frames to save
    PHONE_DEBUG_MAX_FRAMES: int = 20
    # Raw diagnostic mode confidence threshold
    PHONE_RAW_DEBUG_CONFIDENCE: float = 0.01
    # Raw diagnostic mode image size
    PHONE_RAW_DEBUG_IMAGE_SIZE: int = 1280
    # Test configuration: max frames to process (0 = unlimited)
    PHONE_TEST_MAX_FRAMES: int = 0
    # Test configuration: start frame
    PHONE_TEST_START_FRAME: int = 0
    # Test configuration: end frame (0 = end of video)
    PHONE_TEST_END_FRAME: int = 0
    # Test configuration: frame step
    PHONE_TEST_FRAME_STEP: int = 1
    # Association configuration: frames to confirm student switch
    PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES: int = 3
    # Association configuration: score margin to switch students
    PHONE_ASSOCIATION_SWITCH_MARGIN: float = 0.20
    # Association configuration: maximum centre distance for association
    PHONE_MAX_CENTRE_DISTANCE: float = 100.0
    # Association configuration: minimum association score
    PHONE_MIN_ASSOCIATION_SCORE: float = 0.3

    # ── Head Pose Estimation ───────────────────────────────────────────────────
    # Head pose model path
    HEAD_POSE_MODEL_PATH: str = "models/6DRepNet_300W_LP_AFLW2000.pth"
    # Head pose device
    HEAD_POSE_DEVICE: str = "auto"
    # Head pose input size
    HEAD_POSE_INPUT_SIZE: int = 224
    # Face crop padding (0.0 to 1.0)
    HEAD_POSE_FACE_PADDING: float = 0.20
    # Minimum face size in pixels
    HEAD_POSE_MIN_FACE_SIZE: int = 40
    # Maximum absolute angle in degrees
    HEAD_POSE_MAX_ABS_ANGLE: float = 90.0
    # Enable head pose annotation
    HEAD_POSE_ANNOTATION_ENABLED: bool = True
    # Draw orientation axis
    HEAD_POSE_DRAW_AXIS: bool = True
    # Log level for head pose
    HEAD_POSE_LOG_LEVEL: str = "detailed"
    # Frame log interval
    HEAD_POSE_FRAME_LOG_INTERVAL: int = 10

    # ── Image Validation ──────────────────────────────────────────────────────
    MAX_IMAGE_SIZE_MB: int = 5
    EMBEDDING_DIMENSION: int = 512

    # Allowed MIME types for uploaded images.
    # ClassVar tells Pydantic NOT to treat this as a settings field.
    ALLOWED_IMAGE_TYPES: ClassVar[list[str]] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
    ]

    # ── AI Processing Directories ───────────────────────────────────────────────
    OUTPUT_DIR: str = "outputs"
    LOGS_DIR: str = "logs"
    TEMP_DIR: str = "temp"
    ANNOTATED_VIDEOS_DIR: str = "annotated_videos"
    REPORTS_DIR: str = "reports"
    EVIDENCE_DIR: str = "evidence"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,   # Env vars ARE case-sensitive on Linux
        extra="ignore",        # Silently ignore unknown env vars
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    lru_cache ensures the .env file is read only once across the entire
    application lifetime, making settings lookups effectively free.
    """
    return Settings()


# ---------------------------------------------------------------------------
# Module-level singleton — import directly for zero-overhead access.
# ---------------------------------------------------------------------------
settings: Settings = get_settings()

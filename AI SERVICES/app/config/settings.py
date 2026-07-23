"""
Configuration settings for AI Services module.

This module contains all configuration settings including paths,
supported file extensions, default codec, and logging levels.
"""

from pathlib import Path
from typing import List


class Settings:
    """Configuration settings for the AI Services pipeline."""

    # Base directory
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    # Directory paths
    INPUT_DIR: Path = BASE_DIR / "input_videos"
    OUTPUT_DIR: Path = BASE_DIR / "output_videos"
    TEMP_DIR: Path = BASE_DIR / "temp"
    LOG_DIR: Path = BASE_DIR / "logs"

    # Supported video extensions
    SUPPORTED_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".flv"]

    # Default codec
    DEFAULT_CODEC: str = "mp4v"

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Processing settings
    MAX_RETRY_ATTEMPTS: int = 3
    CHUNK_SIZE: int = 1024

    # YOLO Object Detection settings
    MODELS_DIR: Path = BASE_DIR / "app" / "models"
    MODEL_NAME: str = "yolov8n.pt"
    MODEL_PATH: Path = MODELS_DIR / MODEL_NAME
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    DEVICE: str = "auto"  # "auto", "cpu", "cuda", "0", "1", etc.
    
    # Allowed detection classes for exam monitoring
    ALLOWED_CLASSES: List[str] = [
        "person",
        "cell phone",
        "laptop",
        "book",
        "keyboard",
        "mouse",
    ]
    
    # Visualization colors for different classes (BGR format for OpenCV)
    CLASS_COLORS: dict = {
        "person": (0, 255, 0),      # Green
        "cell phone": (0, 0, 255),  # Red
        "laptop": (255, 0, 0),      # Blue
        "book": (255, 255, 0),      # Cyan
        "keyboard": (0, 255, 255),   # Yellow
        "mouse": (255, 0, 255),     # Magenta
    }

    # YOLO Pose Estimation settings
    POSE_MODEL_NAME: str = "yolov8n-pose.pt"
    POSE_MODEL_PATH: Path = MODELS_DIR / POSE_MODEL_NAME
    POSE_CONFIDENCE_THRESHOLD: float = 0.5
    POSE_IOU_THRESHOLD: float = 0.45
    POSE_DEVICE: str = "auto"  # "auto", "cpu", "cuda", "0", "1", etc.
    
    # Pose visualization settings
    POSE_SKELETON_COLOR: tuple = (0, 255, 255)  # Yellow (BGR)
    POSE_KEYPOINT_COLOR: tuple = (0, 0, 255)    # Red (BGR)
    POSE_KEYPOINT_RADIUS: int = 3
    POSE_SKELETON_THICKNESS: int = 2
    POSE_BOX_COLOR: tuple = (255, 0, 0)  # Blue (BGR)
    POSE_BOX_THICKNESS: int = 2

    # Rule Engine settings
    # Person-related thresholds
    MAX_PERSONS: int = 1  # Maximum allowed persons in frame
    PERSON_CONFIDENCE_THRESHOLD: float = 0.5
    
    # Object-related thresholds
    PHONE_CONFIDENCE_THRESHOLD: float = 0.5
    LAPTOP_CONFIDENCE_THRESHOLD: float = 0.5
    BOOK_CONFIDENCE_THRESHOLD: float = 0.5
    
    # Head direction thresholds (in degrees)
    HEAD_TURN_THRESHOLD: float = 30.0  # Degrees to consider as looking left/right
    HEAD_DOWN_THRESHOLD: float = 20.0  # Degrees to consider as looking down
    
    # Frame boundary thresholds (percentage of frame)
    FRAME_BOUNDARY_MARGIN: float = 0.1  # 10% margin from frame edge
    
    # Standing detection threshold
    STANDING_HEIGHT_RATIO: float = 0.7  # Height/width ratio threshold for standing

    @classmethod
    def create_directories(cls) -> None:
        """Create all necessary directories if they don't exist."""
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_supported_extension(cls, filename: str) -> bool:
        """Check if the file extension is supported."""
        return Path(filename).suffix.lower() in cls.SUPPORTED_EXTENSIONS


# Global settings instance
settings = Settings()

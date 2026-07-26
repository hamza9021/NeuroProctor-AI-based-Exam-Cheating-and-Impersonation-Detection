"""YOLO detection constants."""

# YOLOv8m model name
MODEL_NAME = "yolov8m"

# Target classes to detect
TARGET_CLASSES = {
    0: "person",
    67: "cell phone",
    73: "book",
    63: "laptop",
    74: "tablet",
    75: "mouse",
    76: "keyboard",
}

# Default image size for inference
DEFAULT_IMAGE_SIZE = 640

# Default confidence threshold
DEFAULT_CONFIDENCE = 0.25

# Default IOU threshold for NMS
DEFAULT_IOU = 0.45

# Minimum bounding box area (pixels)
MIN_BBOX_AREA = 100

# Maximum bounding box area (pixels)
MAX_BBOX_AREA = 1000000

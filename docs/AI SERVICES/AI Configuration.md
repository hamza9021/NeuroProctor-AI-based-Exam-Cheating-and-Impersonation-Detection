---
title: AI Configuration
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - configuration
last_reviewed: 2026-08-03
---

# AI Configuration

This document details AI Services configuration.

## Configuration File

**File:** `AI SERVICES/app/config/settings.py`

**Class:** `Settings` (Pydantic BaseSettings)

**Purpose:** Load and validate application settings from environment variables

---

## Application Settings

```python
APP_NAME: str = "NeuroProctor AI Services"
APP_VERSION: str = "1.0.0"
DEBUG: bool = False
```

---

## CORS Settings

```python
CORS_ORIGINS: list = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE"]
CORS_ALLOW_HEADERS: list = ["*"]
```

---

## Express Backend Settings

```python
EXPRESS_API_URL: str = "http://localhost:8080"
EXPRESS_API_TIMEOUT: int = 30
```

---

## MongoDB Settings

```python
MONGO_URI: str = "mongodb://localhost:27017"
MONGO_DB_NAME: str = "neuroproctor"
```

---

## JWT Settings

```python
ACCESS_TOKEN_SECRET: str
ACCESS_TOKEN_EXPIRY: str = "15m"
```

**Important:** `ACCESS_TOKEN_SECRET` must be identical to Backend's `ACCESS_TOKEN_SECRET`

---

## Cloudinary Settings

```python
CLOUDINARY_CLOUD_NAME: str
CLOUDINARY_API_KEY: str
CLOUDINARY_API_SECRET: str
CLOUDINARY_STUDENT_FOLDER: str = "neuroproctor/students"
CLOUDINARY_VIDEO_ORIGINAL_FOLDER: str = "videos/original"
CLOUDINARY_VIDEO_PROCESSED_FOLDER: str = "videos/processed"
```

---

## InsightFace Settings

```python
INSIGHTFACE_PROVIDERS: list = ["CPUExecutionProvider"]
INSIGHTFACE_MODEL_PACK: str = "buffalo_l"
```

---

## YOLO Settings

```python
YOLO_MODEL: str = "yolov8m.pt"
YOLO_CONFIDENCE_THRESHOLD: float = 0.25
YOLO_IOU_THRESHOLD: float = 0.45
YOLO_IMAGE_SIZE: int = 640
YOLO_DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
```

---

## Phone Detection Settings

```python
PHONE_MODEL: str = "yolov8m.pt"
PHONE_CONFIDENCE_THRESHOLD: float = 0.10
PHONE_IMAGE_SIZE: int = 960
PHONE_TEMPORAL_CONFIRM_FRAMES: int = 3
PHONE_TEMPORAL_MAX_MISSED_FRAMES: int = 2
PHONE_ROI_ENABLED: bool = True
PHONE_ROI_EXPANSION: float = 0.15
```

---

## Head Pose Settings

```python
HEAD_POSE_MODEL_PATH: str
HEAD_POSE_INPUT_SIZE: int = 224
HEAD_POSE_FACE_PADDING: float = 0.20
HEAD_POSE_MIN_FACE_SIZE: int = 40
HEAD_POSE_SMOOTHING_ENABLED: bool = True
HEAD_POSE_SMOOTHING_ALPHA: float = 0.35
HEAD_POSE_MAX_SINGLE_FRAME_DELTA: float = 45
HEAD_POSE_QUALITY_THRESHOLD: float = 0.5
```

---

## Image Validation Settings

```python
IMAGE_VALIDATION_ENABLED: bool = True
IMAGE_VALIDATION_MIN_WIDTH: int = 100
IMAGE_VALIDATION_MIN_HEIGHT: int = 100
IMAGE_VALIDATION_MAX_SIZE_MB: int = 10
IMAGE_VALIDATION_ALLOWED_FORMATS: list = ["jpg", "jpeg", "png"]
```

---

## AI Processing Directories

```python
AI_PROCESSING_TEMP_DIR: str = "temp"
AI_PROCESSING_OUTPUT_DIR: str = "output"
```

---

## Socket.IO Settings

```python
SOCKETIO_CORS_ALLOWED_ORIGINS: list = ["http://localhost:5173"]
SOCKETIO_CORS_ALLOW_CREDENTIALS: bool = True
```

---

## Environment Variables

### Required Variables

- `ACCESS_TOKEN_SECRET` - JWT secret (must match Backend)
- `MONGO_URI` - MongoDB connection string
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `HEAD_POSE_MODEL_PATH` - Path to 6DRepNet model

### Optional Variables

- `DEBUG` - Enable debug mode (default: False)
- `CORS_ORIGINS` - Allowed CORS origins (default: http://localhost:5173)
- `EXPRESS_API_URL` - Backend API URL (default: http://localhost:8080)

---

## Related Documentation

- [07 - Environment Variables](07%20-%20Environment%20Variables.md) - Environment variables reference
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services overview

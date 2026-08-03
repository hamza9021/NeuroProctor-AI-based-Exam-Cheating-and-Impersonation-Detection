---
title: Environment Variables
project: NeuroProctor
type: reference
status: active
tags:
  - neuroproctor
  - configuration
  - environment
last_reviewed: 2026-08-03
---

# Environment Variables

This document lists all environment variables used across the three NeuroProctor applications.

## Frontend Environment Variables

**File:** `Frontend/.env`

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | Backend Express API URL | `http://localhost:8080` | Yes |
| `VITE_AI_API_URL` | AI Services FastAPI URL | `http://localhost:8000` | Yes |

**Example:**
```env
VITE_API_URL=http://localhost:8080
VITE_AI_API_URL=http://localhost:8000
```

## Backend (Express) Environment Variables

**File:** `Backend(Express)/.env`

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Express server port | `8080` | No |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/neuroproctor` | Yes |
| `ACCESS_TOKEN_SECRET` | JWT access token secret | - | Yes |
| `REFRESH_TOKEN_SECRET` | JWT refresh token secret | - | Yes |
| `ACCESS_TOKEN_EXPIRY` | Access token expiration time | `15m` | No |
| `REFRESH_TOKEN_EXPIRY` | Refresh token expiration time | `7d` | No |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | - | Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | - | Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | - | Yes |

**Example:**
```env
PORT=8080
MONGODB_URI=mongodb://localhost:27017/neuroproctor
ACCESS_TOKEN_SECRET=your-secret-key-change-this
REFRESH_TOKEN_SECRET=your-refresh-secret-change-this
ACCESS_TOKEN_EXPIRY=15m
REFRESH_TOKEN_EXPIRY=7d
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Important Notes:**
- `ACCESS_TOKEN_SECRET` and `REFRESH_TOKEN_SECRET` must be strong random strings
- These secrets must match between Backend and AI Services for JWT verification
- Never commit actual secrets to version control

## AI Services Environment Variables

**File:** `AI SERVICES/.env`

### Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Environment (development/production) | `development` | No |
| `APP_HOST` | Server host | `0.0.0.0` | No |
| `APP_PORT` | Server port | `8000` | No |
| `APP_DEBUG` | Debug mode | `True` | No |
| `APP_TITLE` | Application title | `NeuroProctor AI Backend` | No |
| `APP_VERSION` | Application version | `1.0.0` | No |

### CORS Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGIN` | Allowed CORS origin | `http://localhost:5173` | Yes |

### Backend Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EXPRESS_BACKEND_URL` | Express backend URL | `http://localhost:8080` | Yes |

### MongoDB Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/neuroproctor` | Yes |
| `MONGO_DB_NAME` | Database name | `neuroproctor` | No |

### JWT Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ACCESS_TOKEN_SECRET` | JWT access token secret (must match Express) | - | Yes |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | No |

### Cloudinary Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | - | Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | - | Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | - | Yes |
| `CLOUDINARY_STUDENT_FOLDER` | Student images folder | `neuroproctor/students` | No |

### InsightFace Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `INSIGHTFACE_MODEL_NAME` | InsightFace model name | `buffalo_l` | No |
| `INSIGHTFACE_CTX_ID` | GPU device ID (0 = first GPU, -1 = CPU) | `0` | No |
| `INSIGHTFACE_DET_SIZE` | Detection input size (pixels) | `640` | No |

### YOLO Detection Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `YOLO_MODEL` | YOLO model path | `yolov8m.pt` | No |
| `YOLO_DEVICE` | Inference device (auto/cuda/cpu) | `auto` | No |
| `YOLO_CONFIDENCE` | Confidence threshold (0.0-1.0) | `0.25` | No |
| `YOLO_IOU` | IOU threshold for NMS (0.0-1.0) | `0.45` | No |
| `YOLO_IMAGE_SIZE` | Inference image size (pixels) | `640` | No |
| `YOLO_VERBOSE` | Enable verbose logging | `False` | No |

### Phone Detection Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PHONE_DETECTION_ENABLED` | Enable phone detection | `True` | No |
| `PHONE_MODEL_PATH` | Dedicated phone model path | `""` | No |
| `PHONE_CLASS_NAME` | Phone class name to detect | `cell phone` | No |
| `PHONE_CONFIDENCE` | Phone confidence threshold | `0.10` | No |
| `PHONE_IMAGE_SIZE` | Phone inference image size | `960` | No |
| `PHONE_FALLBACK_IMAGE_SIZES` | Fallback sizes for GPU memory | `768,640` | No |
| `PHONE_MIN_BOX_AREA` | Minimum phone bounding box area | `10` | No |
| `PHONE_ROI_ENABLED` | Enable ROI-based detection | `True` | No |
| `PHONE_ROI_EXPANSION` | ROI expansion factor (0.15 = 15%) | `0.15` | No |
| `PHONE_TEMPORAL_CONFIRM_FRAMES` | Frames to confirm phone detection | `3` | No |
| `PHONE_TEMPORAL_MAX_MISSED_FRAMES` | Max missed frames before expiration | `2` | No |
| `PHONE_ASSOCIATION_IOU` | IOU threshold for student-phone association | `0.10` | No |
| `PHONE_DEDUPLICATION_IOU` | IOU threshold for phone deduplication | `0.50` | No |
| `PHONE_DEBUG_ENABLED` | Enable debug mode | `False` | No |
| `PHONE_DEBUG_MAX_FRAMES` | Max debug frames to save | `20` | No |
| `PHONE_RAW_DEBUG_CONFIDENCE` | Raw debug confidence threshold | `0.01` | No |
| `PHONE_RAW_DEBUG_IMAGE_SIZE` | Raw debug image size | `1280` | No |
| `PHONE_TEST_MAX_FRAMES` | Test: max frames to process (0 = unlimited) | `0` | No |
| `PHONE_TEST_START_FRAME` | Test: start frame | `0` | No |
| `PHONE_TEST_END_FRAME` | Test: end frame (0 = end of video) | `0` | No |
| `PHONE_TEST_FRAME_STEP` | Test: frame step | `1` | No |
| `PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES` | Frames to confirm student switch | `3` | No |
| `PHONE_ASSOCIATION_SWITCH_MARGIN` | Score margin to switch students | `0.20` | No |
| `PHONE_MAX_CENTRE_DISTANCE` | Max centre distance for association | `100.0` | No |
| `PHONE_MIN_ASSOCIATION_SCORE` | Minimum association score | `0.3` | No |

### Head Pose Estimation Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HEAD_POSE_MODEL_PATH` | Head pose model path | `models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth` | Yes |
| `HEAD_POSE_DEVICE` | Inference device (auto/cuda/cpu) | `auto` | No |
| `HEAD_POSE_INPUT_SIZE` | Input image size (pixels) | `224` | No |
| `HEAD_POSE_FACE_PADDING` | Face crop padding (0.0-1.0) | `0.20` | No |
| `HEAD_POSE_MIN_FACE_SIZE` | Minimum face size (pixels) | `40` | No |
| `HEAD_POSE_MAX_ABS_ANGLE` | Maximum absolute angle (degrees) | `90.0` | No |
| `HEAD_POSE_ANNOTATION_ENABLED` | Enable head pose annotation | `True` | No |
| `HEAD_POSE_DRAW_AXIS` | Draw orientation axis | `True` | No |
| `HEAD_POSE_LOG_LEVEL` | Log level (basic/detailed) | `detailed` | No |
| `HEAD_POSE_FRAME_LOG_INTERVAL` | Frame log interval | `10` | No |
| `HEAD_POSE_SMOOTHING_ENABLED` | Enable temporal smoothing | `True` | No |
| `HEAD_POSE_SMOOTHING_ALPHA` | Smoothing alpha (0.0 < alpha <= 1.0) | `0.35` | No |
| `HEAD_POSE_SMOOTHING_MAX_MISSING_FRAMES` | Max missing frames before clearing | `5` | No |
| `HEAD_POSE_MAX_SINGLE_FRAME_DELTA` | Max single-frame angular change (degrees) | `45.0` | No |

### Image Validation Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAX_IMAGE_SIZE_MB` | Maximum image upload size (MB) | `5` | No |
| `EMBEDDING_DIMENSION` | Face embedding dimension | `512` | No |

### Directory Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OUTPUT_DIR` | General output directory | `outputs` | No |
| `LOGS_DIR` | Log files directory | `logs` | No |
| `TEMP_DIR` | Temporary files directory | `temp` | No |
| `ANNOTATED_VIDEOS_DIR` | Annotated videos directory | `annotated_videos` | No |
| `REPORTS_DIR` | Reports directory | `reports` | No |
| `EVIDENCE_DIR` | Evidence directory | `evidence` | No |

## Complete AI Services .env Example

```env
# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=True

# CORS
CORS_ORIGIN=http://localhost:5173

# Express Backend
EXPRESS_BACKEND_URL=http://localhost:8080

# MongoDB
MONGO_URI=mongodb://localhost:27017/neuroproctor
MONGO_DB_NAME=neuroproctor

# JWT (MUST match Express backend)
ACCESS_TOKEN_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_STUDENT_FOLDER=neuroproctor/students

# InsightFace
INSIGHTFACE_MODEL_NAME=buffalo_l
INSIGHTFACE_CTX_ID=0
INSIGHTFACE_DET_SIZE=640

# YOLO Detection
YOLO_MODEL=yolov8m.pt
YOLO_DEVICE=auto
YOLO_CONFIDENCE=0.25
YOLO_IOU=0.45
YOLO_IMAGE_SIZE=640
YOLO_VERBOSE=False

# Phone Detection
PHONE_DETECTION_ENABLED=True
PHONE_MODEL_PATH=
PHONE_CLASS_NAME=cell phone
PHONE_CONFIDENCE=0.10
PHONE_IMAGE_SIZE=960
PHONE_FALLBACK_IMAGE_SIZES=768,640
PHONE_MIN_BOX_AREA=10
PHONE_ROI_ENABLED=True
PHONE_ROI_EXPANSION=0.15
PHONE_TEMPORAL_CONFIRM_FRAMES=3
PHONE_TEMPORAL_MAX_MISSED_FRAMES=2
PHONE_ASSOCIATION_IOU=0.10
PHONE_DEDUPLICATION_IOU=0.50
PHONE_DEBUG_ENABLED=False
PHONE_DEBUG_MAX_FRAMES=20
PHONE_RAW_DEBUG_CONFIDENCE=0.01
PHONE_RAW_DEBUG_IMAGE_SIZE=1280
PHONE_TEST_MAX_FRAMES=0
PHONE_TEST_START_FRAME=0
PHONE_TEST_END_FRAME=0
PHONE_TEST_FRAME_STEP=1
PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES=3
PHONE_ASSOCIATION_SWITCH_MARGIN=0.20
PHONE_MAX_CENTRE_DISTANCE=100.0
PHONE_MIN_ASSOCIATION_SCORE=0.3

# Head Pose Estimation
HEAD_POSE_MODEL_PATH=models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth
HEAD_POSE_DEVICE=auto
HEAD_POSE_INPUT_SIZE=224
HEAD_POSE_FACE_PADDING=0.20
HEAD_POSE_MIN_FACE_SIZE=40
HEAD_POSE_MAX_ABS_ANGLE=90.0
HEAD_POSE_ANNOTATION_ENABLED=True
HEAD_POSE_DRAW_AXIS=True
HEAD_POSE_LOG_LEVEL=detailed
HEAD_POSE_FRAME_LOG_INTERVAL=10
HEAD_POSE_SMOOTHING_ENABLED=True
HEAD_POSE_SMOOTHING_ALPHA=0.35
HEAD_POSE_SMOOTHING_MAX_MISSING_FRAMES=5
HEAD_POSE_MAX_SINGLE_FRAME_DELTA=45.0

# Image Validation
MAX_IMAGE_SIZE_MB=5
EMBEDDING_DIMENSION=512

# Directories
OUTPUT_DIR=outputs
LOGS_DIR=logs
TEMP_DIR=temp
ANNOTATED_VIDEOS_DIR=annotated_videos
REPORTS_DIR=reports
EVIDENCE_DIR=evidence
```

## Security Considerations

### Critical Variables

The following variables are critical for security and must be properly configured:

1. **JWT Secrets** (`ACCESS_TOKEN_SECRET`, `REFRESH_TOKEN_SECRET`)
   - Must be strong random strings (at least 32 characters)
   - Must be identical across Backend and AI Services
   - Never commit to version control
   - Rotate periodically in production

2. **Cloudinary Credentials** (`CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`)
   - Provide access to your Cloudinary account
   - Never commit to version control
   - Use environment-specific credentials

3. **Database URI** (`MONGO_URI`)
   - Contains database credentials if using authentication
   - Use strong passwords in production
   - Never commit to version control

### Production Recommendations

1. **Use a secrets manager** (AWS Secrets Manager, HashiCorp Vault, etc.)
2. **Restrict CORS origins** to actual frontend domain
3. **Disable debug mode** (`APP_DEBUG=False`)
4. **Use HTTPS** in production
5. **Rotate secrets regularly**
6. **Use strong, unique passwords**
7. **Monitor for unauthorized access**

## Related Documentation

- [06 - Setup and Running Guide](06%20-%20Setup%20and%20Running%20Guide.md) - Setup instructions
- [Reference/Configuration Matrix](Reference/Configuration%20Matrix.md) - Configuration reference
- [11 - Security and Authentication](11%20-%20Security%20and%20Authentication.md) - Security details

---
title: AI Services Overview
project: NeuroProctor
type: service
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - fastapi
last_reviewed: 2026-08-03
---

# AI Services Overview

## Technology Stack

- **Framework:** FastAPI
- **Runtime:** Python 3.10+
- **Database:** MongoDB with Motor (async)
- **Authentication:** JWT (shared with Express backend)
- **Real-Time:** Socket.IO
- **Cloud Storage:** Cloudinary
- **Validation:** Pydantic
- **AI Models:**
  - YOLOv8 (object detection)
  - DeepSORT (tracking)
  - YOLO Pose (pose estimation)
  - 6DRepNet (head pose)
  - InsightFace (face embeddings)

## Entry Point

**File:** `AI SERVICES/main.py`

**Description:** Initializes FastAPI app, middleware, routes, and Socket.IO

**Key Components:**
- FastAPI app creation
- CORS middleware
- Exception handlers
- API routers
- Socket.IO integration
- Lifespan events (startup/shutdown)

```python
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Add middleware
app.add_middleware(CORSMiddleware, ...)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(student_router, prefix="/api/v1/students")
app.include_router(video_router, prefix="/api/v1/video")
```

## Directory Structure

```
app/
├── main.py                      # FastAPI entry point
├── api/                         # API routes
│   ├── dependencies.py          # Auth dependencies
│   └── routes/
│       ├── health.py            # Health check
│       ├── student.py           # Student endpoints
│       └── video.py             # Video processing
├── config/                      # Configuration
│   ├── settings.py              # Environment settings
│   ├── database.py              # MongoDB connection
│   └── cloudinary_config.py     # Cloudinary config
├── core/                        # Core utilities
│   ├── exceptions.py            # Custom exceptions
│   └── responses.py             # Response helpers
├── middleware/                  # Middleware
│   └── logging.py               # Logging middleware
├── models/                      # MongoDB models
│   └── student.py               # Student model
├── schemas/                     # Pydantic schemas
│   ├── student.py               # Student schemas
│   └── video.py                 # Video schemas
├── repositories/                # Data access layer
│   ├── student_repository.py    # Student repository
│   └── base_repository.py       # Base repository
├── services/                    # Business logic
│   ├── ai/                      # AI pipeline
│   │   ├── analyzers/           # AI analyzers
│   │   │   ├── head_pose/       # Head pose estimation
│   │   │   ├── phone/           # Phone detection
│   │   │   └── pose/            # Pose estimation
│   │   ├── detectors/           # Object detectors
│   │   │   ├── phone/           # Phone detection
│   │   │   └── yolo/            # YOLO detection
│   │   ├── pipeline/            # Pipeline framework
│   │   ├── processors/          # Video processors
│   │   ├── trackers/            # Object trackers
│   │   │   └── deepsort/        # DeepSORT tracking
│   │   └── monitoring/          # Logging & events
│   └── backend/                 # Backend integration
│       ├── cloudinary_service.py
│       ├── embedding_service.py
│       ├── student_service.py
│       ├── video_client.py
│       └── video_service.py
└── utils/                       # Utilities
    ├── image.py                 # Image utilities
    └── objectid.py              # ObjectId utilities
```

## Configuration

### Settings

**File:** `AI SERVICES/app/config/settings.py`

**Purpose:** Centralized configuration using Pydantic BaseSettings

**Key Settings:**
- Application settings (host, port, debug)
- CORS origin
- Express backend URL
- MongoDB connection
- JWT settings
- Cloudinary settings
- InsightFace settings
- YOLO settings
- Phone detection settings
- Head pose settings
- Directory paths

**Usage:**
```python
from app.config.settings import settings

# Access settings
db_uri = settings.MONGO_URI
yolo_model = settings.YOLO_MODEL
```

---

### Database Connection

**File:** `AI SERVICES/app/config/database.py`

**Purpose:** Async MongoDB connection using Motor

**Usage:**
```python
from app.config.database import connect_to_mongo, close_mongo_connection

@app.on_event("startup")
async def startup():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()
```

---

## Authentication

### JWT Verification

**File:** `AI SERVICES/app/api/dependencies.py`

**Dependency:** `verify_jwt`

**Purpose:** Verifies JWT token from HttpOnly cookies

**Process:**
1. Extract token from cookies
2. Verify signature using `ACCESS_TOKEN_SECRET`
3. Decode token payload
4. Return `TokenPayload` object

---

### Role-Based Authorization

**Dependency:** `require_roles`

**Purpose:** Factory function for role-based authorization

**Usage:**
```python
_protected = require_roles(["admin", "invigilator"])

@router.post("", current_user: TokenPayload = Depends(_protected))
async def create_student(...):
    # Handler logic
```

---

## API Routes

### Health Check

**File:** `AI SERVICES/app/api/routes/health.py`

**Endpoints:**
- `GET /api/v1/health` - Health check

---

### Student Endpoints

**File:** `AI SERVICES/app/api/routes/student.py`

**Endpoints:**
- `POST /api/v1/students` - Register student with face
- `GET /api/v1/students` - List students (paginated)
- `GET /api/v1/students/{student_id}` - Get student by ID
- `PUT /api/v1/students/{student_id}/face` - Update face pose
- `DELETE /api/v1/students/{student_id}` - Delete student

**Authentication:** Requires admin or invigilator role

---

### Video Processing Endpoints

**File:** `AI SERVICES/app/api/routes/video.py`

**Endpoints:**
- `POST /api/v1/video/process` - Process video for cheating detection

**Authentication:** Requires invigilator role

**Socket.IO Events:** Emits real-time progress events

---

## AI Pipeline

### Pipeline Architecture

The AI pipeline processes videos through multiple stages:

1. **YOLO Detection** - Object detection (person, cell phone, etc.)
2. **DeepSORT Tracking** - Person tracking with stable IDs
3. **Phone Detection** - Phone detection with temporal tracking
4. **Pose Estimation** - YOLO Pose with 17 COCO keypoints
5. **Head Pose Estimation** - 6DRepNet for yaw, pitch, roll

### Pipeline Stages

**YOLO Detection Stage**
- **File:** `AI SERVICES/app/services/ai/detectors/yolo/stage.py`
- **Purpose:** Detect objects in each frame
- **Output:** List of detections with bounding boxes

**DeepSORT Stage**
- **File:** `AI SERVICES/app/services/ai/trackers/deepsort/stage.py`
- **Purpose:** Track persons across frames
- **Output:** List of person tracks with stable IDs

**Pose Stage**
- **File:** `AI SERVICES/app/services/ai/analyzers/pose/stage.py`
- **Purpose:** Estimate pose keypoints for each person
- **Output:** Pose results associated with tracks

**Head Pose Stage**
- **File:** `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py`
- **Purpose:** Estimate head orientation (yaw, pitch, roll)
- **Output:** Head pose results with temporal smoothing

**Phone Detection**
- **File:** `AI SERVICES/app/services/ai/detectors/phone/service.py`
- **Purpose:** Detect phones with temporal tracking
- **Output:** Phone tracks with student association

---

### Phone Association

**File:** `AI SERVICES/app/services/ai/analyzers/phone/associator.py`

**Purpose:** Associate phone detections with person tracks

**Priority Evidence:**
1. Wrist distance (highest priority)
2. ROI source track ID match
3. Phone center inside bounding box
4. Phone area overlap
5. Normalized distance to person center
6. Expanded bounding box fallback

---

### Video Processor

**File:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Purpose:** Orchestrates the complete video processing pipeline

**Process:**
1. Extract frames from video
2. Process each frame through pipeline stages
3. Draw annotations on frames
4. Write annotated video
5. Emit real-time progress events

---

## Socket.IO Integration

### Socket Manager

**File:** `AI SERVICES/app/services/ai/monitoring/socket_manager.py`

**Purpose:** Centralized Socket.IO management

**Methods:**
- `emit(event, data, room)` - Emit event to clients
- `join_room(sid, room)` - Join client to room
- `leave_room(sid, room)` - Remove client from room

---

### Pipeline Logger

**File:** `AI SERVICES/app/services/ai/monitoring/pipeline_logger.py`

**Purpose:** Logs pipeline events and emits Socket.IO events

**Methods:**
- `info(message, emit_event, data)` - Log info and optionally emit
- `warning(message, emit_event, data)` - Log warning
- `error(message, emit_event, data)` - Log error

---

### Event Emitter

**File:** `AI SERVICES/app/services/ai/monitoring/event_emitter.py`

**Purpose:** Helper class for emitting standard pipeline events

**Methods:**
- `emit_info(message, data)` - Emit info event
- `emit_warning(message, data)` - Emit warning
- `emit_error(message, data)` - Emit error
- `emit_stage_started(stage_name, data)` - Emit stage started
- `emit_stage_completed(stage_name, data)` - Emit stage completed
- `emit_pipeline_started(data)` - Emit pipeline started
- `emit_pipeline_completed(data)` - Emit pipeline completed
- `emit_pipeline_failed(error, data)` - Emit pipeline failed

---

## Database Models

### Student Model

**File:** `AI SERVICES/app/models/student.py`

**Purpose:** Pydantic model for student documents

**Fields:**
- `id` - MongoDB ObjectId
- `full_name` - Student's full name
- `registration_number` - Unique registration number
- `email` - Student's email
- `department` - Academic department
- `semester` - Current semester (1-8)
- `profile_image` - Cloudinary URL
- `cloudinary_public_id` - Cloudinary public ID
- `face_embeddings` - Array of face embedding subdocuments
- `is_face_registered` - Face registration status
- `is_active` - Active status
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

**Face Embedding Subdocument:**
- `pose` - Head pose (front/left/right/up/down)
- `embedding` - 512-dimensional ArcFace vector
- `quality_score` - Detection confidence (0.0-1.0)
- `captured_at` - Capture timestamp

---

## Services

### Student Service

**File:** `AI SERVICES/app/services/backend/student_service.py`

**Purpose:** Business logic for student operations

**Methods:**
- `create_student()` - Register student with face
- `list_students()` - List students with pagination
- `get_student()` - Get student by ID
- `update_face()` - Update face pose
- `delete_student()` - Delete student

---

### Embedding Service

**File:** `AI SERVICES/app/services/backend/embedding_service.py`

**Purpose:** Generate face embeddings using InsightFace

**Methods:**
- `generate_embedding(image_bytes)` - Generate 512-dim embedding
- `get_quality_score()` - Get detection confidence

---

### Video Service

**File:** `AI SERVICES/app/services/backend/video_service.py`

**Purpose:** Orchestrate video processing workflow

**Methods:**
- `process_video()` - Process video through AI pipeline
- `_validate_video()` - Validate video format and size
- `_process_with_ai_pipeline()` - Run AI pipeline
- `_upload_to_cloudinary()` - Upload to Cloudinary
- `_create_video_analysis()` - Create record via Express backend

---

### Video Client

**File:** `AI SERVICES/app/services/backend/video_client.py`

**Purpose:** HTTP client for Express backend integration

**Methods:**
- `create_video_analysis()` - Create video analysis record
- `update_video_analysis()` - Update video analysis status

---

### Cloudinary Service

**File:** `AI SERVICES/app/services/backend/cloudinary_service.py`

**Purpose:** Cloudinary operations

**Methods:**
- `upload_image()` - Upload image to Cloudinary
- `delete_image()` - Delete image from Cloudinary

---

## Testing

### Test Directory

**Location:** `AI SERVICES/tests/`

**Test Framework:** pytest with pytest-asyncio

**Test Files:**
- `test_phone_detection.py` - Phone detection and association
- `test_head_pose.py` - Head pose estimation
- `test_head_pose_integration.py` - Head pose integration
- `test_head_pose_pose_keypoints.py` - Pose keypoint handling
- `test_head_pose_quality_evaluator.py` - Quality evaluation
- `test_deepsort_fixes.py` - DeepSORT tracking
- `test_pose_estimation.py` - Pose estimation
- `test_temporal_smoothing.py` - Temporal smoothing

**Run Tests:**
```bash
cd "AI SERVICES"
pytest tests/ -v
```

---

## Development

### Start Development Server

```bash
cd "AI SERVICES"
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**URL:** http://localhost:8000

**API Docs:** http://localhost:8000/api/docs (Swagger UI)

---

## Dependencies

**File:** `AI SERVICES/requirements.txt`

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `motor` - Async MongoDB driver
- `pydantic` - Data validation
- `pydantic-settings` - Settings management
- `python-socketio` - Socket.IO
- `ultralytics` - YOLO models
- `insightface` - Face recognition
- `onnxruntime` - ONNX runtime
- `opencv-python` - Computer vision
- `numpy` - Numerical computing
- `pillow` - Image processing
- `cloudinary` - Cloud storage
- `httpx` - HTTP client
- `sixdrepnet` - Head pose estimation

---

## Related Documentation

- [00 - Project Home](00%20-%20Project%20Home.md) - Project overview
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System architecture
- [Frontend/Frontend Overview](Frontend/Frontend%20Overview.md) - Frontend documentation
- [Backend/Backend Overview](Backend/Backend%20Overview.md) - Backend documentation
- [08 - API Reference](08%20-%20API%20Reference.md) - API endpoints
- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - AI pipeline details

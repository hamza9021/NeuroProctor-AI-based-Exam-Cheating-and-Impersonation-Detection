# NeuroProctor — FastAPI AI Backend

> **AI-powered student face registration and impersonation detection service**  
> Part of the NeuroProctor Exam Integrity Platform

---

## Architecture Overview

```
React Frontend
      │
      ▼
Express Backend (Port 8080)   ← Authentication Server
  • Login / Register
  • Issues JWT in HttpOnly cookie (accessToken)
      │
      ▼
FastAPI AI Backend (Port 8000)  ← This Service
  • Reads & validates JWT from cookie
  • Student CRUD
  • Face embedding (InsightFace + ONNX GPU)
  • Cloudinary image storage
      │
      ▼
MongoDB (neuroproctor database)
Cloudinary (profile images)
InsightFace buffalo_l (GPU embeddings)
```

---

## Project Structure

```
Backend(FastApi)/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── student.py        # Student CRUD + face endpoints
│   │   │   └── health.py         # Liveness probe
│   │   └── dependencies.py       # get_current_user + require_roles
│   ├── config/
│   │   ├── settings.py           # Pydantic BaseSettings (env vars)
│   │   ├── database.py           # Motor async MongoDB singleton
│   │   ├── cloudinary_config.py  # Cloudinary SDK init
│   │   └── security.py           # JWT constants
│   ├── core/
│   │   ├── jwt.py                # JWT decode/verify
│   │   ├── responses.py          # Standard response builders
│   │   └── exceptions.py         # Exception hierarchy + handlers
│   ├── middleware/
│   │   └── auth.py               # Request logging middleware
│   ├── models/
│   │   └── student.py            # MongoDB document models
│   ├── repositories/
│   │   ├── base_repository.py    # Generic async CRUD base
│   │   └── student_repository.py # Student-specific DB operations
│   ├── services/
│   │   ├── student_service.py    # Business logic orchestrator
│   │   ├── cloudinary_service.py # Image upload/delete
│   │   └── embedding_service.py  # InsightFace singleton
│   ├── schemas/
│   │   └── student.py            # API request/response schemas
│   └── utils/
│       └── objectid.py           # BSON ObjectId ↔ str helpers
├── main.py                       # FastAPI app factory + lifespan
├── .env                          # Environment variables (do not commit)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Quick Start

### 1. Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| MongoDB | 6.0+ (running locally or Atlas) |
| CUDA (optional) | 11.x / 12.x for GPU acceleration |
| Node.js Express Backend | Running on port 8080 |

### 2. Create a Virtual Environment

```bash
cd "Backend(FastApi)"
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **GPU Note:** `onnxruntime-gpu` requires a compatible CUDA installation.  
> If you don't have a GPU, replace `onnxruntime-gpu` with `onnxruntime` in `requirements.txt`.

### 4. Configure Environment Variables

The `.env` file is already pre-filled with values matching the Express backend.  
Review and update if your values differ:

```env
ACCESS_TOKEN_SECRET=kldsalfjsaldkfd90212jkfskjdnmcxnnjdsakasl  # Must match Express
MONGO_URI=mongodb://localhost:27017/neuroproctor
CLOUDINARY_CLOUD_NAME=dcvwltj5h
CLOUDINARY_API_KEY=979317169374586
CLOUDINARY_API_SECRET=lA7eof0Cr2IPmfmJvOrYtE4m1Tc
```

### 5. Run the Server

```bash
# Development (with hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or directly
python main.py
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

---

## API Reference

### Authentication

All endpoints (except `/api/v1/health`) require a valid JWT stored in the `accessToken` HttpOnly cookie.  
This cookie is set automatically by the Express backend after login.  
**Allowed roles:** `admin`, `invigilator`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Service health check (public) |
| `POST` | `/api/v1/students` | Register student + generate face embedding |
| `GET` | `/api/v1/students` | List students (paginated, searchable, sortable) |
| `GET` | `/api/v1/students/{id}` | Get student by ID |
| `PUT` | `/api/v1/students/{id}/face` | Update face embedding for a specific pose |
| `DELETE` | `/api/v1/students/{id}` | Delete student + Cloudinary image |

### POST /api/v1/students

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | ✅ | Student's full name |
| `registration_number` | string | ✅ | Unique reg/roll number |
| `email` | string | ✅ | Institutional email |
| `department` | string | ✅ | Academic department |
| `semester` | integer | ✅ | Current semester (1–8) |
| `profile_image` | file | ✅ | JPEG/PNG, max 5 MB, 1 face |

**Success Response (201):**
```json
{
  "success": true,
  "message": "Student registered successfully.",
  "data": {
    "id": "64b1f3a2c9e77b001f4d5e8a",
    "full_name": "Hamza Riaz",
    "registration_number": "SP23-BCS-183",
    "email": "hamza@example.com",
    "department": "Computer Science",
    "semester": 7,
    "profile_image": "https://res.cloudinary.com/dcvwltj5h/...",
    "is_face_registered": true,
    "is_active": true,
    "face_embeddings": [
      { "pose": "front", "quality_score": 0.98, "captured_at": "...", "is_registered": true },
      { "pose": "left",  "quality_score": 0.0,  "captured_at": null,  "is_registered": false },
      { "pose": "right", "quality_score": 0.0,  "captured_at": null,  "is_registered": false },
      { "pose": "up",    "quality_score": 0.0,  "captured_at": null,  "is_registered": false },
      { "pose": "down",  "quality_score": 0.0,  "captured_at": null,  "is_registered": false }
    ],
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### PUT /api/v1/students/{id}/face

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pose` | string | ✅ | `front` \| `left` \| `right` \| `up` \| `down` |
| `image` | file | ✅ | JPEG/PNG, max 5 MB, exactly 1 face |

### GET /api/v1/students

**Query Parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `page` | `1` | Page number (1-indexed) |
| `limit` | `10` | Items per page (max 100) |
| `search` | - | Search name, email, reg. number, department |
| `sort_by` | `created_at` | Field to sort by |
| `sort_order` | `desc` | `asc` or `desc` |

---

## MongoDB Document Schema

```json
{
  "_id": "ObjectId",
  "full_name": "Hamza Riaz",
  "registration_number": "SP23-BCS-183",
  "email": "hamza@example.com",
  "department": "Computer Science",
  "semester": 7,
  "profile_image": "https://res.cloudinary.com/...",
  "cloudinary_public_id": "neuroproctor/students/profiles/sp23-bcs-183",
  "face_embeddings": [
    {
      "pose": "front",
      "embedding": [0.123, -0.456, ...],  // 512 floats
      "quality_score": 0.98,
      "captured_at": "2024-01-15T10:30:00Z"
    },
    {
      "pose": "left",
      "embedding": [],                     // Empty placeholder
      "quality_score": 0.0,
      "captured_at": null
    }
    // ... right, up, down placeholders
  ],
  "is_face_registered": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Error Response Format

```json
{
  "success": false,
  "message": "Human-readable error description.",
  "errors": ["Optional list of field-level or detail messages"]
}
```

| Status | Meaning |
|--------|---------|
| `400` | Bad request (validation error) |
| `401` | Missing / expired / invalid JWT |
| `403` | Role not permitted (`admin` or `invigilator` required) |
| `404` | Student not found |
| `409` | Duplicate registration number or email |
| `422` | Face detection failure (no face / multiple faces) |
| `500` | Internal server error (Cloudinary / InsightFace / DB) |

---

## Face Embedding Strategy

When a student is registered with a **single front-facing image**:

1. ✅ Front embedding is generated immediately (512-dim ArcFace vector).
2. ⬜ Left, Right, Up, Down — stored as **empty placeholder embeddings**.

Placeholders are filled via `PUT /students/{id}/face` as additional  
pose photos are captured.  Once all 5 are filled, `is_face_registered = true`.

**Why placeholders instead of generating synthetic poses?**  
Generating fake `left/right/up/down` embeddings from a single front image  
would introduce fabricated biometric data, reducing identification accuracy.  
Real captures from multiple angles are required for reliable impersonation detection.

---

## GPU Acceleration

InsightFace uses ONNX Runtime with providers in this priority order:
1. `CUDAExecutionProvider` — NVIDIA GPU (preferred, ~10–50x faster)
2. `CPUExecutionProvider` — CPU fallback (automatic if CUDA unavailable)

The model is loaded **once** at startup and kept in GPU memory for the  
lifetime of the process.  No per-request model loading.

---

## Development Notes

- **Python:** 3.12+
- **FastAPI:** 0.111+ (with Pydantic v2)
- **Motor:** 3.4+ (async MongoDB driver)
- **InsightFace:** 0.7.3+ (buffalo_l model, ArcFace 512-dim)
- **ONNX Runtime GPU:** 1.18+

All async operations use `await` — the event loop is never blocked.  
CPU/GPU-bound operations (InsightFace inference, Cloudinary upload) are  
offloaded to thread-pool executors via `asyncio.get_event_loop().run_in_executor()`.

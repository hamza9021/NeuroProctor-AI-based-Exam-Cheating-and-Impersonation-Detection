---
title: API Reference
project: NeuroProctor
type: reference
status: active
tags:
  - neuroproctor
  - api
  - endpoints
last_reviewed: 2026-08-03
---

# API Reference

This document documents all API endpoints across the Backend (Express) and AI Services (FastAPI) applications.

## Backend (Express) API

**Base URL:** `http://localhost:8080`

**Authentication:** JWT via HttpOnly cookies

### User Endpoints

#### Register User

**Endpoint:** `POST /api/users/register`

**Authentication:** None

**Request:** Multipart form data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| fullName | string | Yes | User's full name |
| email | string | Yes | User's email (unique) |
| password | string | Yes | User's password |
| phoneNumber | string | Yes | User's phone number |
| role | string | Yes | User role (invigilator/admin) |
| profileImage | file | Yes | Profile image file |

**Response:** 201 Created
```json
{
  "success": true,
  "message": "User Created Successfully",
  "data": {
    "_id": "string",
    "fullName": "string",
    "email": "string",
    "phoneNumber": "string",
    "role": "string",
    "profileImage": "string",
    "isVerified": false,
    "isActive": false,
    "createdAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/user.controller.js`

---

#### Login User

**Endpoint:** `POST /api/users/login`

**Authentication:** None

**Request:** JSON

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email |
| password | string | Yes | User's password |
| role | string | Yes | User role |

**Response:** 200 OK (sets HttpOnly cookies)
```json
{
  "success": true,
  "message": "User Logged In Successfully",
  "data": {
    "_id": "string",
    "fullName": "string",
    "email": "string",
    "phoneNumber": "string",
    "role": "string",
    "profileImage": "string",
    "isVerified": boolean,
    "isActive": boolean
  }
}
```

**Cookies Set:**
- `accessToken` - JWT access token
- `refreshToken` - JWT refresh token

**Source:** `Backend(Express)/src/Controllers/user.controller.js`

---

#### Logout User

**Endpoint:** `POST /api/users/logout`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Logout Successfully",
  "data": {}
}
```

**Source:** `Backend(Express)/src/Controllers/user.controller.js`

---

#### Get Current User

**Endpoint:** `GET /api/users/`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "User Data",
  "data": {
    "_id": "string",
    "fullName": "string",
    "email": "string",
    "phoneNumber": "string",
    "role": "string",
    "profileImage": "string",
    "isVerified": boolean,
    "isActive": boolean
  }
}
```

**Source:** `Backend(Express)/src/Controllers/user.controller.js`

---

### Exam Endpoints

#### Create Exam

**Endpoint:** `POST /api/exams/create`

**Authentication:** Required (JWT)

**Request:** JSON

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Exam title |
| description | string | Yes | Exam description |
| courseName | string | Yes | Course name |
| courseCode | string | Yes | Course code |
| duration | number | Yes | Duration in minutes |
| startTime | string | Yes | Start time (ISO date) |
| endTime | string | Yes | End time (ISO date) |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Created Successfully",
  "data": {
    "_id": "string",
    "title": "string",
    "description": "string",
    "courseName": "string",
    "courseCode": "string",
    "duration": number,
    "startTime": "date",
    "endTime": "date",
    "status": "scheduled",
    "createdBy": "string",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/exam.controller.js`

---

#### Get Exams

**Endpoint:** `GET /api/exams`

**Authentication:** Required (JWT)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|--------|-------------|
| page | number | 1 | Page number |
| limit | number | 10 | Items per page |
| search | string | - | Search query |
| sortBy | string | createdAt | Sort field |
| sortOrder | string | desc | Sort direction (asc/desc) |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exams fetched successfully",
  "data": {
    "exams": [...],
    "pagination": {
      "total": number,
      "page": number,
      "limit": number,
      "totalPages": number,
      "hasNextPage": boolean,
      "hasPrevPage": boolean
    }
  }
}
```

**Source:** `Backend(Express)/src/Controllers/exam.controller.js`

---

#### Get Exam by ID

**Endpoint:** `GET /api/exams/:id`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exams Data",
  "data": {
    "_id": "string",
    "title": "string",
    "description": "string",
    "courseName": "string",
    "courseCode": "string",
    "duration": number,
    "startTime": "date",
    "endTime": "date",
    "status": "string",
    "createdBy": "string",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/exam.controller.js`

---

#### Update Exam

**Endpoint:** `PUT /api/exams/update/:id`

**Authentication:** Required (JWT)

**Request:** JSON (same as create)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Updated Successfully",
  "data": {}
}
```

**Source:** `Backend(Express)/src/Controllers/exam.controller.js`

---

#### Delete Exam

**Endpoint:** `DELETE /api/exams/delete/:id`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Deleted Successfully",
  "data": {}
}
```

**Source:** `Backend(Express)/src/Controllers/exam.controller.js`

---

### Exam Session Endpoints

#### Create Exam Session

**Endpoint:** `POST /api/examSessions/create`

**Authentication:** Required (JWT)

**Request:** JSON

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| examId | string | Yes | Exam ID |
| invigilatorId | string | Yes | Invigilator user ID |
| sessionCode | string | Yes | Unique session code |
| mode | string | No | Session mode (offline/live) |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Session Created Successfully",
  "data": {
    "_id": "string",
    "examId": "string",
    "invigilatorId": "string",
    "sessionCode": "string",
    "mode": "offline",
    "status": "scheduled",
    "verified": false,
    "startedAt": null,
    "endedAt": null,
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

#### Get Exam Sessions

**Endpoint:** `GET /api/examSessions/`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Sessions Data",
  "data": [...]
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

#### Get Exam Session by ID

**Endpoint:** `GET /api/examSessions/:id`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Session Data",
  "data": {
    "_id": "string",
    "examId": "string",
    "invigilatorId": "string",
    "sessionCode": "string",
    "mode": "string",
    "status": "string",
    "verified": boolean,
    "startedAt": "date",
    "endedAt": "date",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

#### Get Invigilator Sessions

**Endpoint:** `GET /api/examSessions/invigilator/:id`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Invigilator Sessions Data",
  "data": [...]
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

#### Update Exam Session

**Endpoint:** `PUT /api/examSessions/update/:id`

**Authentication:** Required (JWT)

**Request:** JSON (any session field)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Session Updated Successfully",
  "data": {}
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

#### Delete Exam Session

**Endpoint:** `DELETE /api/examSessions/delete/:id`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Exam Session Deleted Successfully",
  "data": {}
}
```

**Source:** `Backend(Express)/src/Controllers/examSession.controller.js`

---

### Video Analysis Endpoints

#### Create Video Analysis

**Endpoint:** `POST /api/videoAnalysis`

**Authentication:** Required (JWT)

**Request:** JSON

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sessionId | string | Yes | Exam session ID |
| examId | string | Yes | Exam ID |
| invigilatorId | string | Yes | Invigilator user ID |
| originalVideo | string | Yes | Cloudinary URL for original video |
| processedVideo | string | Yes | Cloudinary URL for processed video |
| processingTime | number | No | Processing time in seconds |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video Analysis Created Successfully",
  "data": {
    "_id": "string",
    "sessionId": "string",
    "examId": "string",
    "invigilatorId": "string",
    "originalVideo": "string",
    "processedVideo": "string",
    "status": "completed",
    "processingTime": number,
    "uploadedAt": "date",
    "completedAt": "date",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

---

#### Get Video Analysis by Session

**Endpoint:** `GET /api/videoAnalysis/session/:sessionId`

**Authentication:** Required (JWT)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video Analysis Data",
  "data": {
    "_id": "string",
    "sessionId": "string",
    "examId": "string",
    "invigilatorId": "string",
    "originalVideo": "string",
    "processedVideo": "string",
    "status": "string",
    "processingTime": number,
    "uploadedAt": "date",
    "completedAt": "date",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

---

#### Get Video Analyses by Invigilator

**Endpoint:** `GET /api/videoAnalysis/invigilator`

**Authentication:** Required (JWT, invigilator role)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video Analyses Data",
  "data": [...]
}
```

**Source:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

---

#### Update Video Analysis

**Endpoint:** `PUT /api/videoAnalysis/:id`

**Authentication:** Required (JWT)

**Request:** JSON

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | string | Yes | New status |
| errorMessage | string | No | Error message if failed |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video Analysis Updated Successfully",
  "data": {
    "_id": "string",
    "sessionId": "string",
    "examId": "string",
    "invigilatorId": "string",
    "originalVideo": "string",
    "processedVideo": "string",
    "status": "string",
    "processingTime": number,
    "errorMessage": "string",
    "uploadedAt": "date",
    "completedAt": "date",
    "createdAt": "date",
    "updatedAt": "date"
  }
}
```

**Source:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

---

#### Delete Video Analysis

**Endpoint:** `DELETE /api/videoAnalysis/:id`

**Authentication:** Required (JWT, admin role)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video Analysis Deleted Successfully",
  "data": null
}
```

**Source:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

---

## AI Services (FastAPI) API

**Base URL:** `http://localhost:8000`

**Authentication:** JWT via HttpOnly cookies (shared with Express backend)

**API Documentation:** http://localhost:8000/api/docs (Swagger UI)

### Health Endpoints

#### Health Check

**Endpoint:** `GET /api/v1/health`

**Authentication:** None

**Response:** 200 OK
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

**Source:** `AI SERVICES/app/api/routes/health.py`

---

### Student Endpoints

#### Create Student

**Endpoint:** `POST /api/v1/students`

**Authentication:** Required (admin or invigilator role)

**Request:** Multipart form data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| full_name | string | Yes | Student's full name (2-100 chars) |
| registration_number | string | Yes | Unique registration number (3-30 chars) |
| email | string | Yes | Student's email |
| department | string | Yes | Academic department (2-100 chars) |
| semester | number | Yes | Current semester (1-8) |
| profile_image | file | Yes | Face photo (JPEG/PNG, max 5MB) |

**Response:** 201 Created
```json
{
  "success": true,
  "message": "Student registered successfully.",
  "data": {
    "id": "string",
    "full_name": "string",
    "registration_number": "string",
    "email": "string",
    "department": "string",
    "semester": number,
    "profile_image": "string",
    "cloudinary_public_id": "string",
    "face_embeddings": [
      {
        "pose": "front",
        "embedding": [512 floats],
        "quality_score": 0.95,
        "captured_at": "date"
      },
      {
        "pose": "left",
        "embedding": [],
        "quality_score": 0.0,
        "captured_at": null
      },
      ...
    ],
    "is_face_registered": true,
    "is_active": true,
    "created_at": "date",
    "updated_at": "date"
  }
}
```

**Source:** `AI SERVICES/app/api/routes/student.py`

---

#### List Students

**Endpoint:** `GET /api/v1/students`

**Authentication:** Required (admin or invigilator role)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|--------|-------------|
| page | number | 1 | Page number (1-indexed) |
| limit | number | 10 | Items per page (1-100) |
| search | string | - | Search query (name, email, reg number, department) |
| sort_by | string | created_at | Sort field |
| sort_order | string | desc | Sort direction (asc/desc) |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Students retrieved successfully.",
  "data": [...],
  "total": number,
  "page": number,
  "limit": number
}
```

**Source:** `AI SERVICES/app/api/routes/student.py`

---

#### Get Student by ID

**Endpoint:** `GET /api/v1/students/{student_id}`

**Authentication:** Required (admin or invigilator role)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Student retrieved successfully.",
  "data": {
    "id": "string",
    "full_name": "string",
    "registration_number": "string",
    "email": "string",
    "department": "string",
    "semester": number,
    "profile_image": "string",
    "cloudinary_public_id": "string",
    "face_embeddings": [...],
    "is_face_registered": boolean,
    "is_active": boolean,
    "created_at": "date",
    "updated_at": "date"
  }
}
```

**Source:** `AI SERVICES/app/api/routes/student.py`

---

#### Update Student Face

**Endpoint:** `PUT /api/v1/students/{student_id}/face`

**Authentication:** Required (admin or invigilator role)

**Request:** Multipart form data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pose | string | Yes | Head pose (front/left/right/up/down) |
| image | file | Yes | Face photo for this pose |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Face embedding for pose 'left' updated successfully.",
  "data": {
    "id": "string",
    "full_name": "string",
    "registration_number": "string",
    "email": "string",
    "department": "string",
    "semester": number,
    "profile_image": "string",
    "cloudinary_public_id": "string",
    "face_embeddings": [...],
    "is_face_registered": boolean,
    "is_active": boolean,
    "created_at": "date",
    "updated_at": "date"
  }
}
```

**Source:** `AI SERVICES/app/api/routes/student.py`

---

#### Delete Student

**Endpoint:** `DELETE /api/v1/students/{student_id}`

**Authentication:** Required (admin or invigilator role)

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Student deleted successfully.",
  "data": {
    "deleted_id": "string"
  }
}
```

**Source:** `AI SERVICES/app/api/routes/student.py`

---

### Video Processing Endpoints

#### Process Video

**Endpoint:** `POST /api/v1/video/process`

**Authentication:** Required (invigilator role)

**Request:** Multipart form data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| video | file | Yes | Video file (MP4, AVI, MOV, max 500MB) |
| sessionId | string | Yes | Exam session ID |
| examId | string | Yes | Exam ID |

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Video processed successfully",
  "data": {
    "videoAnalysis": {
      "_id": "string",
      "sessionId": "string",
      "examId": "string",
      "invigilatorId": "string",
      "originalVideo": "string",
      "processedVideo": "string",
      "status": "completed",
      "processingTime": number,
      "uploadedAt": "date",
      "completedAt": "date",
      "createdAt": "date",
      "updatedAt": "date"
    },
    "processingTime": number
  }
}
```

**Socket.IO Events:** During processing, the following events are emitted:
- `pipeline_info` - General pipeline information
- `pipeline_warning` - Pipeline warnings
- `pipeline_error` - Pipeline errors
- `stage_started` - Stage started
- `stage_completed` - Stage completed
- `pipeline_started` - Pipeline started
- `pipeline_completed` - Pipeline completed
- `pipeline_failed` - Pipeline failed

**Source:** `AI SERVICES/app/api/routes/video.py`

---

## Error Responses

All endpoints return errors in a consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "errors": [...]
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Related Documentation

- [09 - Database Reference](09%20-%20Database%20Reference.md) - Database models
- [10 - Socket.IO Events](10%20-%20Socket.IO%20Events.md) - Real-time events
- [04 - End-to-End Workflows](04%20-%20End-to-End%20Workflows.md) - API usage in workflows

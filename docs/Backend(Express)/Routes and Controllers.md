---
title: Routes and Controllers
project: NeuroProctor
type: reference
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - routes
  - controllers
last_reviewed: 2026-08-03
---

# Routes and Controllers

This document details all API routes and controllers in the Backend (Express) application.

## User Routes

### Route File

**File:** `Backend(Express)/src/Routes/user.route.js`

**Base Path:** `/api/users`

### Endpoints

#### POST `/api/users/register`

**Purpose:** Register a new user

**Controller:** `registerUser` in `user.controller.js`

**Middleware:**
- `upload.single('profileImage')` - Multer for profile image upload
- `validateRegister` - Request validation

**Request:**
- `Content-Type: multipart/form-data`
- Body: `fullName`, `email`, `password`, `phoneNumber`, `role`, `profileImage` (file)

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "_id": "user_id",
    "fullName": "John Doe",
    "email": "john@example.com",
    "role": "invigilator",
    "profileImage": "cloudinary_url"
  }
}
```

**Status Codes:**
- 201 - Success
- 400 - Validation error
- 409 - Duplicate email

---

#### POST `/api/users/login`

**Purpose:** Login user

**Controller:** `loginUser` in `user.controller.js`

**Middleware:** `validateLogin` - Request validation

**Request:**
```json
{
  "email": "john@example.com",
  "password": "password123",
  "role": "invigilator"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User logged in successfully",
  "data": {
    "_id": "user_id",
    "email": "john@example.com",
    "fullName": "John Doe",
    "role": "invigilator"
  }
}
```

**Cookies Set:**
- `accessToken` (HttpOnly, 15 min expiry)
- `refreshToken` (HttpOnly, 7 day expiry)

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Invalid credentials
- 403 - Role mismatch
- 404 - User not found

---

#### POST `/api/users/logout`

**Purpose:** Logout user

**Controller:** `logoutUser` in `user.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Request:** None (requires JWT in cookie)

**Response:**
```json
{
  "success": true,
  "message": "User logged out successfully"
}
```

**Cookies Cleared:** `accessToken`, `refreshToken`

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

#### GET `/api/users/`

**Purpose:** Get current user

**Controller:** `getUser` in `user.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Request:** None (requires JWT in cookie)

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "user_id",
    "fullName": "John Doe",
    "email": "john@example.com",
    "role": "invigilator",
    "profileImage": "cloudinary_url"
  }
}
```

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

## Exam Routes

### Route File

**File:** `Backend(Express)/src/Routes/exam.route.js`

**Base Path:** `/api/exams`

### Endpoints

#### POST `/api/exams/create`

**Purpose:** Create a new exam

**Controller:** `createExam` in `exam.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- `validateExam` - Request validation

**Request:**
```json
{
  "title": "Midterm Exam",
  "description": "Midterm examination",
  "courseName": "Computer Science",
  "courseCode": "CS101",
  "duration": 90,
  "startTime": "2024-01-01T09:00:00Z",
  "endTime": "2024-01-01T11:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Exam created successfully",
  "data": {
    "_id": "exam_id",
    "title": "Midterm Exam",
    "status": "scheduled",
    "createdBy": "user_id"
  }
}
```

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized

---

#### GET `/api/exams`

**Purpose:** List exams with pagination

**Controller:** `getExams` in `exam.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 10)
- `status` - Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "exams": [...],
    "total": 100,
    "page": 1,
    "pages": 10
  }
}
```

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

#### GET `/api/exams/:id`

**Purpose:** Get exam by ID

**Controller:** `getExamById` in `exam.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "exam_id",
    "title": "Midterm Exam",
    "description": "...",
    "status": "scheduled"
  }
}
```

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 404 - Exam not found

---

#### PUT `/api/exams/update/:id`

**Purpose:** Update exam

**Controller:** `updateExam` in `exam.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- `validateExam` - Request validation

**Request:** Same as create

**Response:** Updated exam object

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized
- 403 - Forbidden (not creator)
- 404 - Exam not found

---

#### DELETE `/api/exams/delete/:id`

**Purpose:** Delete exam

**Controller:** `deleteExam` in `exam.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:**
```json
{
  "success": true,
  "message": "Exam deleted successfully"
}
```

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 403 - Forbidden (not creator)
- 404 - Exam not found

---

## Exam Session Routes

### Route File

**File:** `Backend(Express)/src/Routes/examSession.route.js`

**Base Path:** `/api/examSessions`

### Endpoints

#### POST `/api/examSessions/create`

**Purpose:** Create exam session

**Controller:** `createExamSession` in `examSession.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- `validateExamSession` - Request validation

**Request:**
```json
{
  "examId": "exam_id",
  "sessionCode": "SESSION123",
  "mode": "offline"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session created successfully",
  "data": {
    "_id": "session_id",
    "examId": "exam_id",
    "invigilatorId": "user_id",
    "sessionCode": "SESSION123",
    "status": "scheduled"
  }
}
```

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized
- 404 - Exam not found

---

#### GET `/api/examSessions/`

**Purpose:** List exam sessions

**Controller:** `getExamSessions` in `examSession.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Query Parameters:**
- `page` - Page number
- `limit` - Items per page
- `status` - Filter by status

**Response:** Paginated session list

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

#### GET `/api/examSessions/:id`

**Purpose:** Get session by ID

**Controller:** `getExamSessionById` in `examSession.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:** Session object

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 404 - Session not found

---

#### GET `/api/examSessions/invigilator/:id`

**Purpose:** Get invigilator's sessions

**Controller:** `getInvigilatorSessions` in `examSession.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:** Invigilator's session list

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

#### PUT `/api/examSessions/update/:id`

**Purpose:** Update session

**Controller:** `updateExamSession` in `examSession.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- `validateExamSession` - Request validation

**Response:** Updated session object

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized
- 403 - Forbidden (not invigilator)
- 404 - Session not found

---

#### DELETE `/api/examSessions/delete/:id`

**Purpose:** Delete session

**Controller:** `deleteExamSession` in `examSession.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:** Success message

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 403 - Forbidden (not invigilator)
- 404 - Session not found

---

## Video Analysis Routes

### Route File

**File:** `Backend(Express)/src/Routes/videoAnalysis.route.js`

**Base Path:** `/api/videoAnalysis`

### Endpoints

#### POST `/api/videoAnalysis`

**Purpose:** Create video analysis record

**Controller:** `createVideoAnalysis` in `videoAnalysis.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- Role check (invigilator only)

**Request:**
```json
{
  "sessionId": "session_id",
  "examId": "exam_id",
  "originalVideo": "cloudinary_url",
  "processedVideo": "cloudinary_url",
  "processingTime": 120.5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video analysis created successfully",
  "data": {
    "_id": "analysis_id",
    "sessionId": "session_id",
    "status": "completed"
  }
}
```

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized
- 403 - Forbidden (not invigilator)

---

#### GET `/api/videoAnalysis/session/:sessionId`

**Purpose:** Get video analysis by session

**Controller:** `getVideoAnalysisBySession` in `videoAnalysis.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:** Video analysis object

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 404 - Not found

---

#### GET `/api/videoAnalysis/invigilator`

**Purpose:** Get invigilator's video analyses

**Controller:** `getVideoAnalysesByInvigilator` in `videoAnalysis.controller.js`

**Middleware:** `verifyJWT` - JWT verification

**Response:** Invigilator's analysis list

**Status Codes:**
- 200 - Success
- 401 - Unauthorized

---

#### PUT `/api/videoAnalysis/:id`

**Purpose:** Update video analysis

**Controller:** `updateVideoAnalysis` in `videoAnalysis.controller.js`

**Middleware:**
- `verifyJWT` - JWT verification
- Role check (invigilator only)

**Response:** Updated analysis object

**Status Codes:**
- 200 - Success
- 400 - Validation error
- 401 - Unauthorized
- 403 - Forbidden (not invigilator)
- 404 - Not found

---

#### DELETE `/api/videoAnalysis/:id`

**Purpose:** Delete video analysis

**Controller:** `deleteVideoAnalysis` in `videoAnalysis.controller.js`

**Middleware:** `verifyJWT` - JWT verification
- Role check (invigilator only)

**Response:** Success message

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 403 - Forbidden (not invigilator)
- 404 - Not found

---

## Admin Routes

### Route File

**File:** `Backend(Express)/src/Routes/admin.route.js`

**Base Path:** `/api/admin`

### Endpoints

#### GET `/api/admin/users`

**Purpose:** Get all users (admin only)

**Controller:** Admin user controller

**Middleware:**
- `verifyJWT` - JWT verification
- Role check (admin only)

**Response:** User list

**Status Codes:**
- 200 - Success
- 401 - Unauthorized
- 403 - Forbidden (not admin)

---

## Related Documentation

- [Backend/Backend Architecture](Backend/Backend%20Architecture.md) - Backend architecture
- [Backend/Services and Repositories](Backend/Services%20and%20Repositories.md) - Services
- [Backend/Models and Schemas](Backend/Models%20and%20Schemas.md) - Models
- [Backend/Backend File Reference](Backend/Backend%20File%20Reference.md) - File reference

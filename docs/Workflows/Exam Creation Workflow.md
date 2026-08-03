---
title: Exam Creation Workflow
project: NeuroProctor
type: workflow
status: active
tags:
  - neuroproctor
  - workflow
  - exam-creation
last_reviewed: 2026-08-03
---

# Exam Creation Workflow

## Overview

This workflow describes the complete exam creation and management process.

## Exam Creation Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Frontend
    participant Backend
    participant MongoDB
    
    Admin->>Frontend: Click "Create Exam"
    Frontend->>Frontend: Show exam creation form
    Admin->>Frontend: Fill exam details
    Frontend->>Frontend: Validate form data
    Frontend->>Backend: POST /api/exams/create
    Note over Frontend,Backend: JWT cookie + exam data
    Backend->>Backend: Validate request (Joi)
    Backend->>Backend: Verify user from JWT
    Backend->>Backend: Set default status to "scheduled"
    Backend->>MongoDB: Create exam document
    MongoDB->>Backend: Confirmation
    Backend->>Frontend: Return exam data (200)
    Frontend->>Admin: Show success, redirect to exams list
```

### Steps

1. **Admin clicks "Create Exam"**
   - Navigate to exam management section
   - Click create button

2. **Fill exam form**
   - Title
   - Description
   - Course name
   - Course code
   - Duration (in minutes)
   - Start time (ISO date)
   - End time (ISO date)

3. **Frontend validation**
   - Required fields check
   - Duration positive number
   - End time after start time
   - Date format validation

4. **Backend validation**
   - Joi schema validation
   - Verify user is admin
   - Verify end time > start time

5. **Exam creation**
   - Create exam document in MongoDB
   - Set status to "scheduled"
   - Set createdBy to user ID
   - Set timestamps

6. **Response**
   - Return exam data
   - Status: 200 OK

### Source Files

- Frontend: `Frontend/src/components/Exams/Exam.jsx`
- Frontend API: `Frontend/src/apis/Exams/index.js`
- Backend Route: `Backend(Express)/src/Routes/exam.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/exam.controller.js`
- Backend Model: `Backend(Express)/src/Models/exam.models.js`

---

## Exam Session Creation Flow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant Backend
    participant MongoDB
    
    Invigilator->>Frontend: Select exam
    Invigilator->>Frontend: Click "Create Session"
    Frontend->>Frontend: Show session creation form
    Invigilator->>Frontend: Fill session details
    Frontend->>Frontend: Validate form data
    Frontend->>Backend: POST /api/examSessions/create
    Backend->>Backend: Validate request
    Backend->>Backend: Verify invigilator role
    Backend->>Backend: Generate session code
    Backend->>MongoDB: Create session document
    MongoDB->>Backend: Confirmation
    Backend->>Frontend: Return session data (200)
    Frontend->>Invigilator: Show success, redirect to sessions
```

### Steps

1. **Invigilator selects exam**
   - Browse exam list
   - Select exam for session

2. **Fill session form**
   - Exam ID (auto-filled)
   - Invigilator ID (auto-filled from JWT)
   - Session code (auto-generated or manual)
   - Mode (offline/live)

3. **Frontend validation**
   - Required fields check
   - Mode validation

4. **Backend validation**
   - Joi schema validation
   - Verify user is invigilator
   - Verify exam exists

5. **Session creation**
   - Create session document in MongoDB
   - Set status to "scheduled"
   - Set verified to false
   - Set timestamps

6. **Response**
   - Return session data
   - Status: 200 OK

### Source Files

- Frontend: `Frontend/src/components/ExamSessions/ExamSessionsList.jsx`
- Frontend API: `Frontend/src/apis/ExamSessions/index.js`
- Backend Route: `Backend(Express)/src/Routes/examSession.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/examSession.controller.js`
- Backend Model: `Backend(Express)/src/Models/examSession.models.js`

---

## Exam Status Flow

```mermaid
stateDiagram-v2
    [*] --> Scheduled: Exam created
    Scheduled --> Ongoing: Start time reached
    Ongoing --> Completed: End time reached
    Scheduled --> Cancelled: Admin cancels
    Ongoing --> Cancelled: Admin cancels
    Completed --> [*]
    Cancelled --> [*]
```

### Status Descriptions

| Status | Description | Transitions |
|--------|-------------|-------------|
| `scheduled` | Exam is scheduled for future | → ongoing, → cancelled |
| `ongoing` | Exam is currently in progress | → completed, → cancelled |
| `completed` | Exam has finished | (final) |
| `cancelled` | Exam was cancelled | (final) |

---

## Session Status Flow

```mermaid
stateDiagram-v2
    [*] --> Scheduled: Session created
    Scheduled --> Waiting: Invigilator joins
    Waiting --> Processing: Video uploaded
    Processing --> Active: Processing complete
    Active --> Completed: Session ends
    Scheduled --> Cancelled: Admin cancels
    Waiting --> Cancelled: Admin cancels
    Processing --> Cancelled: Admin cancels
    Active --> Cancelled: Admin cancels
    Completed --> [*]
    Cancelled --> [*]
```

### Status Descriptions

| Status | Description | Transitions |
|--------|-------------|-------------|
| `scheduled` | Session is scheduled | → waiting, → cancelled |
| `waiting` | Invigilator has joined, waiting for video | → processing, → cancelled |
| `processing` | Video is being processed | → active, → cancelled |
| `active` | Session is active for monitoring | → completed, → cancelled |
| `completed` | Session has finished | (final) |
| `cancelled` | Session was cancelled | (final) |

---

## Error Handling

### Exam Creation Errors

| Error | Status | Description |
|-------|--------|-------------|
| Invalid input | 422 | Validation failed |
| Unauthorized | 401 | Invalid or missing JWT |
| Forbidden | 403 | User not admin |
| End time before start time | 422 | Time validation failed |

### Session Creation Errors

| Error | Status | Description |
|-------|--------|-------------|
| Invalid input | 422 | Validation failed |
| Unauthorized | 401 | Invalid or missing JWT |
| Forbidden | 403 | User not invigilator |
| Exam not found | 404 | Exam ID does not exist |
| Duplicate session code | 409 | Session code already exists |

---

## Related Documentation

- [04 - End-to-End Workflows](04%20-%20End-to-End%20Workflows.md) - Other workflows
- [08 - API Reference](08%20-%20API%20Reference.md) - API endpoints
- [09 - Database Reference](09%20-%20Database%20Reference.md) - Database models

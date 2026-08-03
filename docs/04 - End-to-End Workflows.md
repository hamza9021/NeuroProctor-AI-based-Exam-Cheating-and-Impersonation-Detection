---
title: End-to-End Workflows
project: NeuroProctor
type: workflow
status: active
tags:
  - neuroproctor
  - workflows
  - sequences
last_reviewed: 2026-08-03
---

# End-to-End Workflows

This document traces the complete execution paths for key user and system workflows through the NeuroProctor system.

## User Authentication Workflow

### Registration Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant MongoDB
    participant Cloudinary
    
    User->>Frontend: Fill registration form
    User->>Frontend: Upload profile image
    Frontend->>Backend: POST /api/users/register
    Note over Frontend,Backend: Multipart form data
    Backend->>Backend: Validate input (Joi)
    Backend->>Backend: Check duplicate user
    Backend->>Cloudinary: Upload profile image
    Cloudinary->>Backend: Return image URL
    Backend->>Backend: Hash password (bcrypt)
    Backend->>MongoDB: Create user document
    MongoDB->>Backend: Confirmation
    Backend->>Frontend: Return user data (201)
    Frontend->>User: Redirect to login
```

**Source Files:**
- Frontend: `Frontend/src/Pages/Auth/Register.jsx`
- Frontend API: `Frontend/src/apis/Users/index.js`
- Backend Route: `Backend(Express)/src/Routes/user.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/user.controller.js`
- Backend Model: `Backend(Express)/src/Models/user.models.js`

### Login Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant MongoDB
    
    User->>Frontend: Enter credentials
    Frontend->>Backend: POST /api/users/login
    Backend->>Backend: Validate input
    Backend->>MongoDB: Find user by email
    MongoDB->>Backend: User document
    Backend->>Backend: Verify password (bcrypt)
    Backend->>Backend: Check role match
    Backend->>Backend: Check verification status
    Backend->>Backend: Generate access token (JWT)
    Backend->>Backend: Generate refresh token (JWT)
    Backend->>Frontend: Set HttpOnly cookies
    Backend->>Frontend: Return user data
    Frontend->>Frontend: Update AuthContext
    Frontend->>User: Redirect to dashboard
```

**Source Files:**
- Frontend: `Frontend/src/Pages/Auth/Login.jsx`
- Frontend API: `Frontend/src/apis/Users/index.js`
- Backend Route: `Backend(Express)/src/Routes/user.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/user.controller.js`

## Student Enrollment Workflow

### Face Registration Flow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant AI Services
    participant InsightFace
    participant Cloudinary
    participant MongoDB
    
    Invigilator->>Frontend: Fill student form
    Invigilator->>Frontend: Upload face photo
    Frontend->>AI Services: POST /api/v1/students
    Note over Frontend,AI Services: Multipart form data + JWT cookie
    AI Services->>AI Services: Validate request (Pydantic)
    AI Services->>AI Services: Check duplicate registration
    AI Services->>Cloudinary: Upload profile image
    Cloudinary->>AI Services: Return image URL
    AI Services->>InsightFace: Generate face embedding
    InsightFace->>AI Services: 512-dim ArcFace vector
    AI Services->>AI Services: Create placeholder poses
    AI Services->>MongoDB: Insert student document
    MongoDB->>AI Services: Confirmation
    AI Services->>Frontend: Return student data (201)
    Frontend->>Invigilator: Show success message
```

**Source Files:**
- Frontend: `Frontend/src/components/Students/Student.jsx`
- Frontend API: `Frontend/src/apis/Students/index.js`
- AI Services Route: `AI SERVICES/app/api/routes/student.py`
- AI Services Service: `AI SERVICES/app/services/backend/student_service.py`
- AI Services Model: `AI SERVICES/app/models/student.py`

### Multi-Pose Enrollment Flow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant AI Services
    participant InsightFace
    participant MongoDB
    
    Invigilator->>Frontend: Select pose (left/right/up/down)
    Invigilator->>Frontend: Upload pose photo
    Frontend->>AI Services: PUT /api/v1/students/{id}/face
    AI Services->>AI Services: Validate request
    AI Services->>MongoDB: Find student by ID
    MongoDB->>AI Services: Student document
    AI Services->>InsightFace: Generate face embedding
    InsightFace->>AI Services: 512-dim ArcFace vector
    AI Services->>AI Services: Update specific pose
    AI Services->>AI Services: Check if all poses registered
    AI Services->>MongoDB: Update student document
    MongoDB->>AI Services: Confirmation
    AI Services->>Frontend: Return updated student
    Frontend->>Invigilator: Show success
```

**Source Files:**
- Frontend: `Frontend/src/components/Students/StudentDetail.jsx`
- AI Services Route: `AI SERVICES/app/api/routes/student.py`
- AI Services Service: `AI SERVICES/app/services/backend/student_service.py`

## Exam Creation Workflow

```mermaid
sequenceDiagram
    participant Admin
    participant Frontend
    participant Backend
    participant MongoDB
    
    Admin->>Frontend: Fill exam form
    Frontend->>Backend: POST /api/exams/create
    Note over Frontend,Backend: JWT cookie + exam data
    Backend->>Backend: Validate request (Joi)
    Backend->>Backend: Verify user from JWT
    Backend->>MongoDB: Create exam document
    MongoDB->>Backend: Confirmation
    Backend->>Frontend: Return exam data (201)
    Frontend->>Admin: Show success, redirect to exams list
```

**Source Files:**
- Frontend: `Frontend/src/components/Exams/Exam.jsx`
- Frontend API: `Frontend/src/apis/Exams/index.js`
- Backend Route: `Backend(Express)/src/Routes/exam.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/exam.controller.js`
- Backend Model: `Backend(Express)/src/Models/exam.models.js`

## Exam Session Workflow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant Backend
    participant MongoDB
    
    Invigilator->>Frontend: Create session for exam
    Frontend->>Backend: POST /api/examSessions/create
    Backend->>Backend: Validate request
    Backend->>Backend: Verify invigilator role
    Backend->>MongoDB: Create session document
    MongoDB->>Backend: Confirmation
    Backend->>Frontend: Return session data (201)
    Frontend->>Invigilator: Show session details
```

**Source Files:**
- Frontend: `Frontend/src/components/ExamSessions/ExamSessionsList.jsx`
- Frontend API: `Frontend/src/apis/ExamSessions/index.js`
- Backend Route: `Backend(Express)/src/Routes/examSession.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/examSession.controller.js`
- Backend Model: `Backend(Express)/src/Models/examSession.models.js`

## Video Upload Workflow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant AI Services
    participant TempStorage
    participant AI Pipeline
    participant Cloudinary
    participant Backend
    
    Invigilator->>Frontend: Select video file
    Invigilator->>Frontend: Select session
    Frontend->>AI Services: POST /api/v1/video/process
    Note over Frontend,AI Services: Multipart form data + JWT cookie
    AI Services->>AI Services: Validate video (type, size)
    AI Services->>TempStorage: Save temporary file
    AI Services->>Invigilator: Socket.IO: "Video received"
    AI Services->>Invigilator: Socket.IO: "Video validated"
    
    AI Services->>AI Pipeline: Process video
    Note over AI Services,AI Pipeline: YOLO → DeepSORT → Pose → Head Pose → Phone
    AI Pipeline->>Invigilator: Socket.IO: Progress updates
    AI Pipeline->>AI Services: Annotated video
    
    AI Services->>Cloudinary: Upload original video
    Cloudinary->>AI Services: Original URL
    AI Services->>Invigilator: Socket.IO: "Original video uploaded"
    
    AI Services->>Cloudinary: Upload processed video
    Cloudinary->>AI Services: Processed URL
    AI Services->>Invigilator: Socket.IO: "Processed video uploaded"
    
    AI Services->>Backend: POST /api/videoAnalysis
    Note over AI Services,Backend: Create video analysis record
    Backend->>MongoDB: Insert video analysis
    MongoDB->>Backend: Confirmation
    Backend->>AI Services: Video analysis record
    AI Services->>TempStorage: Delete temporary files
    AI Services->>Frontend: Return video analysis data
    Frontend->>Invigilator: Show success, download links
```

**Source Files:**
- Frontend: `Frontend/src/components/VideoUpload/VideoUpload.jsx`
- Frontend API: `Frontend/src/apis/VideoAnalysis/index.js`
- AI Services Route: `AI SERVICES/app/api/routes/video.py`
- AI Services Service: `AI SERVICES/app/services/backend/video_service.py`
- AI Services Processor: `AI SERVICES/app/services/ai/processors/video_processor.py`
- Backend Route: `Backend(Express)/src/Routes/videoAnalysis.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

## Video Processing Workflow (AI Pipeline)

```mermaid
graph TD
    Input[Video File] --> FE[Frame Extractor]
    FE -->|Frame by frame| YOLO[YOLO Detection Stage]
    YOLO -->|Detections| NonPerson[Draw Non-Person Detections]
    YOLO -->|Person detections| DeepSORT[DeepSORT Tracking Stage]
    DeepSORT -->|Tracks| Phone[Phone Detection Service]
    Phone -->|Phone tracks| Pose[Pose Estimation Stage]
    Pose -->|Poses| HeadPose[Head Pose Estimation Stage]
    HeadPose -->|Head poses| PhoneDraw[Draw Phone Detections]
    NonPerson -->|Annotated frame| Writer[Video Writer]
    PhoneDraw -->|Annotated frame| Writer
    Writer --> Output[Annotated Video]
    
    style Input fill:#ffe1e1
    style Output fill:#e1ffe1
    style YOLO fill:#fff4e1
    style DeepSORT fill:#fff4e1
    style Phone fill:#fff4e1
    style Pose fill:#fff4e1
    style HeadPose fill:#fff4e1
```

**Source Files:**
- AI Services Processor: `AI SERVICES/app/services/ai/processors/video_processor.py`
- YOLO Stage: `AI SERVICES/app/services/ai/detectors/yolo/stage.py`
- DeepSORT Stage: `AI SERVICES/app/services/ai/trackers/deepsort/stage.py`
- Pose Stage: `AI SERVICES/app/services/ai/analyzers/pose/stage.py`
- Head Pose Stage: `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py`
- Phone Service: `AI SERVICES/app/services/ai/detectors/phone/service.py`

## Real-Time Logging Workflow

```mermaid
sequenceDiagram
    participant AI Pipeline
    participant EventEmitter
    participant PipelineLogger
    participant SocketManager
    participant SocketIOServer
    participant Frontend
    participant Invigilator
    
    AI Pipeline->>EventEmitter: emit_info("Stage started")
    EventEmitter->>PipelineLogger: info(message, emit_event="pipeline_info")
    PipelineLogger->>PipelineLogger: Build event data
    PipelineLogger->>SocketManager: emit(event, data, room)
    SocketManager->>SocketIOServer: emit(event, data, room)
    SocketIOServer->>Frontend: Socket.IO event
    Frontend->>Invigilator: Display progress update
```

**Source Files:**
- AI Services EventEmitter: `AI SERVICES/app/services/ai/monitoring/event_emitter.py`
- AI Services Logger: `AI SERVICES/app/services/ai/monitoring/pipeline_logger.py`
- AI Services Socket Manager: `AI SERVICES/app/services/ai/monitoring/socket_manager.py`

## Phone Association Workflow

```mermaid
graph TD
    Phone[Phone Detection] --> ROI[ROI Detection]
    ROI --> Merge[Merge Detections]
    Phone --> Merge
    Merge --> Associator[Phone Student Associator]
    Associator -->|With pose data| Wrist[Calculate Wrist Distance]
    Wrist --> Priority[Apply Priority Scoring]
    Priority -->|1. Wrist distance| Score1[Score 2.0]
    Priority -->|2. ROI source| Score2[Score 1.5]
    Priority -->|3. Center inside| Score3[Score 1.0]
    Priority -->|4. Area overlap| Score4[Score 0.7]
    Priority -->|5. Distance to center| Score5[Score 0.3]
    Priority -->|6. Expanded bbox| Score6[Score 0.5]
    Score1 --> Total[Combined Score]
    Score2 --> Total
    Score3 --> Total
    Score4 --> Total
    Score5 --> Total
    Score6 --> Total
    Total --> Best[Select Best Association]
    Best --> Temporal[Temporal Tracker]
    Temporal --> Confirmed[Confirmed Tracks]
    
    style Phone fill:#ffe1e1
    style Confirmed fill:#e1ffe1
```

**Source Files:**
- AI Services Associator: `AI SERVICES/app/services/ai/analyzers/phone/associator.py`
- AI Services Temporal Tracker: `AI SERVICES/app/services/ai/detectors/phone/temporal_tracker.py`

## Processed Video Download Workflow

```mermaid
sequenceDiagram
    participant Invigilator
    participant Frontend
    participant Backend
    participant MongoDB
    participant Cloudinary
    
    Invigilator->>Frontend: Request video analysis
    Frontend->>Backend: GET /api/videoAnalysis/session/:sessionId
    Backend->>Backend: Verify JWT
    Backend->>MongoDB: Find video analysis by session
    MongoDB->>Backend: Video analysis document
    Backend->>Frontend: Return video analysis data
    Frontend->>Invigilator: Display download links
    Invigilator->>Frontend: Click download
    Frontend->>Cloudinary: Direct download from URL
    Cloudinary->>Invigilator: Video file
```

**Source Files:**
- Frontend: `Frontend/src/Pages/Dashboard/InvigilatorSessions.jsx`
- Frontend API: `Frontend/src/apis/VideoAnalysis/index.js`
- Backend Route: `Backend(Express)/src/Routes/videoAnalysis.route.js`
- Backend Controller: `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

## Related Documentation

- [02 - System Architecture](02%20-%20System%20Architecture.md) - System design details
- [08 - API Reference](08%20-%20API%20Reference.md) - Complete API documentation
- [10 - Socket.IO Events](10%20-%20Socket.IO%20Events.md) - Real-time event reference
- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - AI pipeline details

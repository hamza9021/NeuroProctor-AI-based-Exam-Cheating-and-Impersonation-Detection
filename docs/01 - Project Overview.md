---
title: Project Overview
project: NeuroProctor
type: overview
status: active
tags:
  - neuroproctor
  - overview
last_reviewed: 2026-08-03
---

# NeuroProctor Project Overview

## Purpose

NeuroProctor is an AI-powered exam integrity platform designed to detect cheating behaviors in recorded exam videos. The system uses computer vision and machine learning to analyze student behavior during exams, identifying potential violations such as phone usage, head movements, and impersonation.

## Main Users and Roles

### Users
- **Admin** - System administrators who manage users, verify invigilators, and oversee the entire system
- **Invigilator** - Exam proctors who create exams, manage exam sessions, and upload videos for analysis
- **Student** - Students who are enrolled in exams and whose behavior is monitored (currently no student-facing interface)

### Roles
- `admin` - Full system access, user management, exam oversight
- `invigilator` - Exam creation, session management, video upload and analysis

## Main Problems Solved

1. **Cheating Detection** - Automatically detects phone usage and suspicious head movements in exam videos
2. **Impersonation Prevention** - Uses face embeddings to verify student identity (enrollment phase)
3. **Remote Proctoring** - Enables remote exam monitoring through video analysis
4. **Evidence Generation** - Produces annotated videos with detection bounding boxes for review

## Main Modules

### Frontend (React)
- User authentication (login, register, logout)
- Role-based dashboards (Admin Dashboard, Invigilator Dashboard)
- Exam management (create, view, update, delete exams)
- Exam session management
- Student enrollment and face registration
- Video upload interface
- Real-time processing log viewer
- Processed video download

### Backend (Express)
- User authentication and authorization (JWT)
- User management (CRUD operations)
- Exam management (CRUD operations)
- Exam session management
- Video analysis record management
- Cloudinary integration for file storage
- MongoDB data persistence

### AI Services (FastAPI)
- Student face enrollment with multi-pose embeddings
- Video processing pipeline
- YOLO object detection (person, cell phone, laptop, etc.)
- DeepSORT person tracking
- YOLO Pose estimation
- 6DRepNet head pose estimation
- Phone detection and temporal tracking
- Phone-to-student association (with wrist-based priority)
- Real-time Socket.IO event broadcasting
- Cloudinary video upload
- Express backend API integration

## Implemented Capabilities

### Authentication & Authorization
- ✅ User registration with profile image upload
- ✅ User login with JWT tokens (access + refresh)
- ✅ Role-based access control (admin, invigilator)
- ✅ Cookie-based token storage (HttpOnly)
- ✅ User verification workflow (admin verifies invigilators)

### Exam Management
- ✅ Exam creation (title, description, course, duration, schedule)
- ✅ Exam listing with pagination and search
- ✅ Exam updates and deletion
- ✅ Exam status management (scheduled, ongoing, completed, cancelled)

### Exam Sessions
- ✅ Session creation with unique session codes
- ✅ Session assignment to invigilators
- ✅ Session status tracking (scheduled, waiting, processing, active, completed)
- ✅ Session mode support (offline, live)

### Student Management
- ✅ Student registration with profile image
- ✅ Multi-pose face enrollment (front, left, right, up, down)
- ✅ InsightFace ArcFace embeddings (512-dimensional)
- ✅ Face quality scoring
- ✅ Student listing with pagination and search
- ✅ Student updates and deletion
- ✅ Cloudinary image management

### Video Processing
- ✅ Video upload (MP4, AVI, MOV, max 500MB)
- ✅ YOLO object detection (person, cell phone, laptop, book, bottle)
- ✅ DeepSORT person tracking with stable track IDs
- ✅ YOLO Pose estimation (17 COCO keypoints)
- ✅ 6DRepNet head pose estimation (yaw, pitch, roll)
- ✅ Phone detection with temporal tracking
- ✅ Phone-to-student association with wrist-based priority
- ✅ ROI-based phone detection within person bounding boxes
- ✅ Annotated video generation with bounding boxes
- ✅ Real-time Socket.IO progress updates
- ✅ Cloudinary video upload (original and processed)
- ✅ Video analysis record creation via Express backend

### Real-Time Communication
- ✅ Socket.IO server integration
- ✅ Real-time pipeline event broadcasting
- ✅ Progress updates during video processing
- ✅ Room-based event routing

## Incomplete Capabilities

### Face Identification in Video
- ❌ Face detection in video frames
- ❌ Face embedding extraction from video
- ❌ Face matching against enrolled students
- ❌ Impersonation detection
- ❌ Face tracking across frames

### Cheating Rule Engine
- ❌ Rule definition system
- ❌ Rule evaluation engine
- ❌ Custom rule creation
- ❌ Rule-based event generation

### Suspicion Scoring
- ❌ Per-student suspicion scoring
- ❌ Temporal suspicion accumulation
- ❌ Weighted rule contributions
- ❌ Threshold-based alerting

### Report Generation
- ❌ PDF report generation
- ❌ Evidence compilation
- ❌ Timeline visualization
- ❌ Statistical summaries
- ❌ Flagged event highlighting

### Live Monitoring
- ❌ Real-time video streaming
- ❌ Live frame processing
- ❌ Real-time alert generation
- ❌ Live intervention capabilities

### Evidence Management
- ❌ Evidence frame capture
- ❌ Evidence storage and retrieval
- ❌ Evidence annotation
- ❌ Evidence export

## Current Project Maturity

**Maturity Level:** Early Development / Prototype

### Strengths
- Solid authentication and authorization foundation
- Working video processing pipeline with multiple AI stages
- Real-time communication infrastructure
- Cloud integration for storage
- Good separation of concerns between services
- Comprehensive test coverage for AI components

### Weaknesses
- Missing face identification in video (core feature)
- No rule engine or suspicion scoring
- No report generation
- Limited error handling in some areas
- Some hardcoded configuration
- Incomplete integration between AI stages
- No live monitoring capabilities

### Technical Debt
- Phone association recently refactored (wrist-based priority)
- Track ID 0 rendering bug recently fixed
- Some test files may be outdated
- Configuration scattered across multiple files
- Limited documentation in code

## Architecture Notes

The system follows a microservices-like architecture with three separate applications:

1. **Frontend** - Single-page React application
2. **Backend (Express)** - RESTful API server
3. **AI Services** - FastAPI AI processing server

Communication flows:
- Frontend ↔ Backend: REST API + JWT cookies
- Frontend ↔ AI Services: REST API + JWT cookies + Socket.IO
- AI Services ↔ Backend: REST API (for video analysis record creation)
- AI Services → Frontend: Socket.IO events (real-time updates)

All three services share the same MongoDB database but use different drivers:
- Backend: Mongoose (sync)
- AI Services: Motor (async)

## Next Priority Areas

Based on current implementation status, the logical next priorities are:

1. **Face Identification in Video** - Core missing feature for impersonation detection
2. **Rule Engine** - Required for automated cheating detection
3. **Suspicion Scoring** - Required for quantifying cheating behavior
4. **Report Generation** - Required for human review and evidence
5. **Live Monitoring** - Required for real-time exam proctoring

## Related Documentation

- [02 - System Architecture](02%20-%20System%20Architecture.md) - Detailed system design
- [05 - Current Implementation Status](05%20-%20Current%20Implementation%20Status.md) - Detailed status matrix
- [14 - Development Roadmap](14%20-%20Development%20Roadmap.md) - Recommended development order

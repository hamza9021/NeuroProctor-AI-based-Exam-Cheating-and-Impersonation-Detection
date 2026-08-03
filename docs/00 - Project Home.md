---
title: NeuroProctor - Project Home
project: NeuroProctor
type: home
status: active
tags:
  - neuroproctor
  - home
last_reviewed: 2026-08-03
---

# NeuroProctor Project Home

NeuroProctor is an AI-powered exam integrity platform that detects cheating behaviors in recorded exam videos using computer vision and machine learning.

## Quick Navigation

### Core Documentation
- [01 - Project Overview](01%20-%20Project%20Overview.md) - What NeuroProctor does and current status
- [02 - System Architecture](02%20-%20System%20Architecture.md) - High-level system design and components
- [03 - Repository Map](03%20-%20Repository%20Map.md) - Complete directory structure
- [04 - End-to-End Workflows](04%20-%20End-to-End%20Workflows.md) - Key user and system workflows
- [05 - Current Implementation Status](05%20-%20Current%20Implementation%20Status.md) - What's implemented vs missing
- [06 - Setup and Running Guide](06%20-%20Setup%20and%20Running%20Guide.md) - How to set up and run the project
- [07 - Environment Variables](07%20-%20Environment%20Variables.md) - Configuration reference
- [08 - API Reference](08%20-%20API%20Reference.md) - All API endpoints documented
- [09 - Database Reference](09%20-%20Database%20Reference.md) - Database models and relationships
- [10 - Socket.IO Events](10%20-%20Socket.IO%20Events.md) - Real-time event reference
- [11 - Security and Authentication](11%20-%20Security%20and%20Authentication.md) - Auth implementation details
- [12 - Testing Guide](12%20-%20Testing%20Guide.md) - Testing approach and coverage
- [13 - Known Issues and Technical Debt](13%20-%20Known%20Issues%20and%20Technical%20Debt.md) - Current issues and improvements needed
- [14 - Development Roadmap](14%20-%20Development%20Roadmap.md) - Recommended development priorities
- [15 - Agent Context Guide](15%20-%20Agent%20Context%20Guide.md) - Guide for AI coding agents

### Service-Specific Documentation
- [Frontend/Frontend Overview](Frontend/Frontend%20Overview.md) - React frontend architecture
- [Backend/Backend Overview](Backend/Backend%20Overview.md) - Express backend architecture
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - FastAPI AI backend architecture

### Workflow Documentation
- [Workflows/User Authentication Workflow](Workflows/User%20Authentication%20Workflow.md)
- [Workflows/Student Enrollment Workflow](Workflows/Student%20Enrollment%20Workflow.md)
- [Workflows/Face Enrollment Workflow](Workflows/Face%20Enrollment%20Workflow.md)
- [Workflows/Exam Creation Workflow](Workflows/Exam%20Creation%20Workflow.md)
- [Workflows/Exam Session Workflow](Workflows/Exam%20Session%20Workflow.md)
- [Workflows/Video Upload Workflow](Workflows/Video%20Upload%20Workflow.md)
- [Workflows/Video Processing Workflow](Workflows/Video%20Processing%20Workflow.md)
- [Workflows/Real-Time Logging Workflow](Workflows/Real-Time%20Logging%20Workflow.md)
- [Workflows/Processed Video Download Workflow](Workflows/Processed%20Video%20Download%20Workflow.md)

### Reference Documentation
- [Reference/Glossary](Reference/Glossary.md) - Terminology definitions
- [Reference/Dependencies](Reference/Dependencies.md) - All dependencies and versions
- [Reference/Configuration Matrix](Reference/Configuration%20Matrix.md) - Configuration reference
- [Reference/API-to-Frontend Mapping](Reference/API-to-Frontend%20Mapping.md) - API endpoints to frontend components
- [Reference/Model Relationships](Reference/Model%20Relationships.md) - Database model relationships
- [Reference/Event and Data Contracts](Reference/Event%20and%20Data%20Contracts.md) - Data contracts and schemas
- [Reference/Decision Log](Reference/Decision%20Log.md) - Architectural decisions

### Diagrams
- [Diagrams/High-Level Architecture](Diagrams/High-Level%20Architecture.md)
- [Diagrams/Backend Request Flow](Diagrams/Backend%20Request%20Flow.md)
- [Diagrams/AI Pipeline Flow](Diagrams/AI%20Pipeline%20Flow.md)
- [Diagrams/Video Processing Sequence](Diagrams/Video%20Processing%20Sequence.md)
- [Diagrams/Authentication Sequence](Diagrams/Authentication%20Sequence.md)
- [Diagrams/Database Relationships](Diagrams/Database%20Relationships.md)

## Project Status

**Overall Status:** Partially Implemented

### Working Components
- ✅ User authentication (register, login, logout)
- ✅ Role-based access control (admin, invigilator)
- ✅ Exam creation and management
- ✅ Exam session creation
- ✅ Student face enrollment with multi-pose embeddings
- ✅ Video upload and processing
- ✅ AI pipeline (YOLO detection, DeepSORT tracking, pose estimation, head pose, phone detection)
- ✅ Real-time Socket.IO logging during video processing
- ✅ Cloudinary integration for images and videos
- ✅ MongoDB persistence

### Known Issues
- ⚠️ Phone association with overlapping persons (recently fixed with wrist-based priority)
- ⚠️ Track ID 0 rendering bug (recently fixed)
- ⚠️ No face identification/verification in video pipeline
- ⚠️ No rule engine for cheating detection
- ⚠️ No suspicion scoring system
- ⚠️ No report generation

### Incomplete Features
- ❌ Face identification during video processing
- ❌ Cheating rule engine
- ❌ Suspicion scoring
- ❌ Report generation
- ❌ Evidence capture and storage
- ❌ Real-time exam monitoring (live mode)

## Architecture Summary

NeuroProctor consists of three main applications:

1. **Frontend** - React/Vite application for user interface
2. **Backend (Express)** - Node.js/Express backend for business logic and data persistence
3. **AI Services** - FastAPI backend for AI-powered video processing

### Technology Stack

**Frontend:**
- React 19
- React Router 7
- TanStack Query
- Socket.IO Client
- Axios
- TailwindCSS

**Backend (Express):**
- Express 5
- MongoDB (Mongoose)
- JWT authentication
- Cloudinary
- Multer (file uploads)

**AI Services:**
- FastAPI
- MongoDB (Motor - async)
- YOLOv8 (object detection)
- DeepSORT (person tracking)
- YOLO Pose (pose estimation)
- 6DRepNet (head pose estimation)
- InsightFace (face embeddings)
- Socket.IO
- Cloudinary

## Important Warnings

> [!warning] CORS Configuration
> The AI Services currently allows all origins (`allow_origins=["*"]`). This should be restricted to the actual frontend origin in production.

> [!warning] Secret Management
> JWT secrets and Cloudinary credentials are stored in `.env` files. Ensure these are not committed to version control.

> [!warning] GPU Requirements
> The AI pipeline requires GPU support for optimal performance. ONNX Runtime GPU is configured but falls back to CPU if unavailable.

## Recent Changes

- Fixed phone association to use wrist distance as priority evidence
- Fixed Track ID 0 rendering bug (was showing "Student Unknown")
- Added comprehensive end-to-end trace logging for phone detection pipeline
- Enhanced phone-to-student association with pose keypoints

## Recommended Reading Order for New Developers

1. Start with [01 - Project Overview](01%20-%20Project%20Overview.md) to understand the system
2. Review [02 - System Architecture](02%20-%20System%20Architecture.md) for high-level design
3. Read [06 - Setup and Running Guide](06%20-%20Setup%20and%20Running%20Guide.md) to get the system running
4. Study [04 - End-to-End Workflows](04%20-%20End-to-End%20Workflows.md) to understand key processes
5. Review service-specific documentation for your area of work
6. Read [15 - Agent Context Guide](15%20-%20Agent%20Context%20Guide.md) if you're an AI coding agent

## Contact

- GitHub: https://github.com/hamza9021/NeuroProctor-AI-based-Exam-Cheating-and-Impersonation-Detection

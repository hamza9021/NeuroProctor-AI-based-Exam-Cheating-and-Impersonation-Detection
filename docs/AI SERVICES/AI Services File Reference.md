---
title: AI Services File Reference
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - file-reference
last_reviewed: 2026-08-03
---

# AI Services File Reference

This document provides detailed information about every relevant AI Services source file.

## Entry Points

### `main.py`

**Purpose:** FastAPI application entry point

**Used by:** Uvicorn server

**Depends on:**
- FastAPI
- Socket.IO
- API routes
- Database connection
- AI pipeline components

**Key Symbols:**
- `app` - FastAPI application
- `socketio` - Socket.IO server
- `lifespan` - Startup/shutdown events

**Runtime Role:** Bootstraps the FastAPI application with Socket.IO integration

**Status:** Implemented

**Notes:** Includes CORS middleware, exception handlers, and route inclusion

---

## Configuration

### `app/config/settings.py`

**Purpose:** Application settings using Pydantic BaseSettings

**Used by:** All modules

**Depends on:**
- Pydantic
- Environment variables

**Key Symbols:**
- `Settings` - Settings class
- All configuration constants

**Runtime Role:** Provides validated configuration from environment variables

**Status:** Implemented

**Notes:** Strict validation, loads from .env file

---

### `app/config/cloudinary_config.py`

**Purpose:** Cloudinary configuration

**Used by:** Cloudinary service

**Depends on:**
- cloudinary

**Key Symbols:** Cloudinary configuration

**Runtime Role:** Configures Cloudinary SDK

**Status:** Implemented

---

## API Layer

### `app/api/dependencies.py`

**Purpose:** Authentication and authorization dependencies

**Used by:** API routes

**Depends on:**
- JWT
- User model

**Key Symbols:**
- `verify_jwt` - JWT verification dependency
- `require_roles` - Role-based authorization factory

**Runtime Role:** Provides auth dependencies for route protection

**Status:** Implemented

---

### `app/api/routes/health.py`

**Purpose:** Health check endpoint

**Used by:** main.py

**Depends on:** None

**Key Symbols:** Health check route

**Runtime Role:** Provides health status endpoint

**Status:** Implemented

---

### `app/api/routes/student.py`

**Purpose:** Student CRUD endpoints

**Used by:** main.py

**Depends on:**
- Student service
- Student repository
- Auth dependencies

**Key Symbols:**
- `create_student` - Create student endpoint
- `get_students` - List students endpoint
- `get_student` - Get student endpoint
- `update_student_face` - Update face pose endpoint
- `delete_student` - Delete student endpoint

**Runtime Role:** Handles student API requests

**Status:** Implemented

---

### `app/api/routes/video.py`

**Purpose:** Video processing endpoint

**Used by:** main.py

**Depends on:**
- Video service
- Auth dependencies
- Socket.IO event emitter

**Key Symbols:**
- `process_video` - Video upload and processing endpoint

**Runtime Role:** Handles video upload and triggers AI pipeline

**Status:** Implemented

**Notes:** Emits real-time Socket.IO events during processing

---

### `app/api/routes/root.py`

**Purpose:** Root endpoint

**Used by:** main.py

**Depends on:** None

**Key Symbols:** Root route

**Runtime Role:** Provides API root information

**Status:** Implemented

---

## Models

### `app/models/student.py`

**Purpose:** Student Pydantic models

**Used by:** Student API, Student repository

**Depends on:**
- Pydantic
- BSON

**Key Symbols:**
- `StudentDocument` - Student document model
- `FaceEmbedding` - Face embedding model
- `StudentCreate` - Student creation schema
- `StudentUpdate` - Student update schema

**Runtime Role:** Defines student data schema and validation

**Status:** Implemented

---

## Repositories

### `app/repositories/base_repository.py`

**Purpose:** Base repository class

**Used by:** All repositories

**Depends on:**
- Motor (MongoDB)

**Key Symbols:**
- `BaseRepository` - Base repository class

**Runtime Role:** Provides common database operations

**Status:** Implemented

---

### `app/repositories/student_repository.py`

**Purpose:** Student repository

**Used by:** Student service

**Depends on:**
- BaseRepository
- Student model

**Key Symbols:**
- `StudentRepository` - Student repository class
- CRUD methods

**Runtime Role:** Handles student database operations

**Status:** Implemented

---

## Services

### `app/services/embedding/embedding_service.py`

**Purpose:** Face embedding generation using InsightFace

**Used by:** Student service

**Depends on:**
- InsightFace

**Key Symbols:**
- `EmbeddingService` - Embedding service class
- `get_embedding()` - Generate embedding

**Runtime Role:** Generates face embeddings for student enrollment

**Status:** Implemented

---

### `app/services/backend/video_service.py`

**Purpose:** Video processing orchestration

**Used by:** Video route

**Depends on:**
- Video processor
- Cloudinary service
- Backend API client
- Socket.IO event emitter

**Key Symbols:**
- `VideoService` - Video service class
- `process_video()` - Process video method

**Runtime Role:** Orchestrates video processing workflow

**Status:** Implemented

**Notes:** Handles validation, AI pipeline, Cloudinary upload, and backend record creation

---

### `app/services/backend/video_client.py`

**Purpose:** Backend API client

**Used by:** Video service

**Depends on:**
- httpx

**Key Symbols:**
- `VideoClient` - Backend API client class
- `create_video_analysis()` - Create video analysis record

**Runtime Role:** Communicates with Express backend

**Status:** Implemented

---

### `app/services/backend/cloudinary_service.py`

**Purpose:** Cloudinary operations

**Used by:** Video service

**Depends on:**
- cloudinary

**Key Symbols:**
- `CloudinaryService` - Cloudinary service class
- `upload_video()` - Upload video
- `delete_video()` - Delete video

**Runtime Role:** Handles Cloudinary video operations

**Status:** Implemented

---

### `app/services/student/student_service.py`

**Purpose:** Student business logic

**Used by:** Student routes

**Depends on:**
- Student repository
- Embedding service
- Cloudinary service

**Key Symbols:**
- `StudentService` - Student service class
- CRUD methods

**Runtime Role:** Handles student business logic

**Status:** Implemented

---

## AI Pipeline

### `app/services/ai/pipeline/frame_context.py`

**Purpose:** Shared data object for pipeline stages

**Used by:** All pipeline stages

**Depends on:** None

**Key Symbols:**
- `FrameContext` - Frame context dataclass

**Runtime Role:** Shares data between pipeline stages

**Status:** Implemented

---

### `app/services/ai/pipeline/offline_pipeline.py`

**Purpose:** Offline pipeline for pre-recorded videos

**Used by:** Video processor

**Depends on:**
- Pipeline stages

**Key Symbols:**
- `OfflinePipeline` - Offline pipeline class
- `process()` - Process video method

**Runtime Role:** Orchestrates AI pipeline stages

**Status:** Implemented

---

### `app/services/ai/pipeline/pipeline_stage.py`

**Purpose:** Base class for pipeline stages

**Used by:** All pipeline stages

**Depends on:** None

**Key Symbols:**
- `PipelineStage` - Base stage class
- `process()` - Abstract process method

**Runtime Role:** Provides interface for pipeline stages

**Status:** Implemented

---

## AI Detectors

### `app/services/ai/detectors/yolo/stage.py`

**Purpose:** YOLO detection pipeline stage

**Used by:** Video processor

**Depends on:**
- YOLO detector
- YOLO mapper

**Key Symbols:**
- `YOLODetectionStage` - YOLO stage class

**Runtime Role:** Detects objects in video frames

**Status:** Implemented

---

### `app/services/ai/detectors/yolo/detector.py`

**Purpose:** YOLO detector wrapper

**Used by:** YOLO stage

**Depends on:**
- ultralytics

**Key Symbols:**
- `YOLODetector` - YOLO detector class

**Runtime Role:** Wraps Ultralytics YOLO model

**Status:** Implemented

---

### `app/services/ai/detectors/phone/service.py`

**Purpose:** Phone detection service

**Used by:** Video processor

**Depends on:**
- YOLO detector
- Phone associator

**Key Symbols:**
- `PhoneDetectionService` - Phone detection class

**Runtime Role:** Detects and tracks phones

**Status:** Implemented

---

### `app/services/ai/detectors/phone/associator.py`

**Purpose:** Phone-to-student association

**Used by:** Phone detection service

**Depends on:** None

**Key Symbols:**
- `PhoneAssociator` - Associator class

**Runtime Role:** Associates phones with students

**Status:** Implemented

---

## AI Trackers

### `app/services/ai/trackers/deepsort/stage.py`

**Purpose:** DeepSORT tracking pipeline stage

**Used by:** Video processor

**Depends on:**
- DeepSORT service

**Key Symbols:**
- `DeepSORTStage` - DeepSORT stage class

**Runtime Role:** Tracks persons across frames

**Status:** Implemented

---

### `app/services/ai/trackers/deepsort/service.py`

**Purpose:** DeepSORT tracker wrapper

**Used by:** DeepSORT stage

**Depends on:**
- deep-sort-realtime

**Key Symbols:**
- `DeepSORTService` - DeepSORT service class

**Runtime Role:** Wraps DeepSORT tracker

**Status:** Implemented

---

## AI Analyzers

### `app/services/ai/analyzers/pose/stage.py`

**Purpose:** Pose estimation pipeline stage

**Used by:** Video processor

**Depends on:**
- Pose service

**Key Symbols:**
- `YoloPoseStage` - Pose stage class

**Runtime Role:** Estimates pose keypoints

**Status:** Implemented

---

### `app/services/ai/analyzers/pose/service.py`

**Purpose:** Pose estimation service

**Used by:** Pose stage

**Depends on:**
- ultralytics

**Key Symbols:**
- `PoseService` - Pose service class

**Runtime Role:** Wraps YOLO Pose model

**Status:** Implemented

---

### `app/services/ai/analyzers/head_pose/stage.py`

**Purpose:** Head pose estimation pipeline stage

**Used by:** Video processor

**Depends on:**
- Head pose service

**Key Symbols:**
- `SixDRepNetHeadPoseStage` - Head pose stage class

**Runtime Role:** Estimates head orientation

**Status:** Implemented

---

### `app/services/ai/analyzers/head_pose/service.py`

**Purpose:** Head pose estimation service

**Used by:** Head pose stage

**Depends on:**
- 6DRepNet

**Key Symbols:**
- `HeadPoseService` - Head pose service class

**Runtime Role:** Wraps 6DRepNet model

**Status:** Implemented

---

### `app/services/ai/analyzers/head_pose/temporal_smoother.py`

**Purpose:** Temporal smoothing for head poses

**Used by:** Head pose service

**Depends on:** None

**Key Symbols:**
- `TemporalSmoother` - Smoother class

**Runtime Role:** Smooths head pose angles over time

**Status:** Implemented

---

## AI Processors

### `app/services/ai/processors/video_processor.py`

**Purpose:** Main video processor

**Used by:** Video service

**Depends on:**
- All AI components
- Frame extractor
- Video writer

**Key Symbols:**
- `VideoProcessor` - Video processor class
- `process_video()` - Process video method

**Runtime Role:** Orchestrates complete AI pipeline

**Status:** Implemented

---

### `app/services/ai/processors/frame_extractor.py`

**Purpose:** Frame extraction from video

**Used by:** Video processor

**Depends on:**
- OpenCV

**Key Symbols:**
- `FrameExtractor` - Frame extractor class

**Runtime Role:** Extracts frames from video file

**Status:** Implemented

---

## AI Monitoring

### `app/services/ai/monitoring/socket_manager.py`

**Purpose:** Socket.IO server management

**Used by:** main.py, event emitter

**Depends on:**
- python-socketio

**Key Symbols:**
- `SocketManager` - Socket manager class

**Runtime Role:** Manages Socket.IO server and connections

**Status:** Implemented

---

### `app/services/ai/monitoring/event_emitter.py`

**Purpose:** Event emission helper

**Used by:** Video service, pipeline stages

**Depends on:**
- Socket manager
- Pipeline logger

**Key Symbols:**
- `EventEmitter` - Event emitter class

**Runtime Role:** Emits standardized pipeline events

**Status:** Implemented

---

### `app/services/ai/monitoring/pipeline_logger.py`

**Purpose:** Pipeline logging

**Used by:** Event emitter, pipeline stages

**Depends on:**
- Loguru

**Key Symbols:**
- `PipelineLogger` - Pipeline logger class

**Runtime Role:** Logs pipeline events

**Status:** Implemented

---

## Configuration

### `requirements.txt`

**Purpose:** Python dependencies

**Used by:** pip

**Depends on:** None

**Key Symbols:** Package list

**Runtime Role:** Defines Python dependencies

**Status:** Implemented

---

### `.env`

**Purpose:** Environment variables

**Used by:** Application

**Depends on:** None

**Key Symbols:** Environment variables

**Runtime Role:** Provides configuration

**Status:** Implemented

**Notes:** Not in source control (gitignored)

---

## Related Documentation

- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture
- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/AI Configuration](AI%20Services/AI%20Configuration.md) - Configuration

---
title: Repository Map
project: NeuroProctor
type: reference
status: active
tags:
  - neuroproctor
  - repository
  - structure
last_reviewed: 2026-08-03
---

# Repository Map

## Root Structure

```
NeuroProctor-AI-based-Exam-Cheating-and-Impersonation-Detection/
├── .git/
├── .gitignore
├── what_we_have_done.md
├── Frontend/                    # React frontend application
├── Backend(Express)/            # Express backend application
└── AI SERVICES/                 # FastAPI AI backend
```

## Frontend Directory Structure

```
Frontend/
├── .Prettierignore
├── .Prettierrc
├── .env                         # Environment variables
├── .gitignore
├── .oxlintrc.json
├── README.md
├── index.html                   # HTML entry point
├── node_modules/                # Dependencies (ignored)
├── package-lock.json
├── package.json                 # Dependencies and scripts
├── postcss.config.js
├── src/
│   ├── App.jsx                  # Main app component with routing
│   ├── index.css                # Global styles
│   ├── main.jsx                 # React entry point
│   ├── Assets/                  # Static assets
│   ├── AxiosInstance/           # Axios configuration
│   │   └── index.js
│   ├── Pages/                   # Page components
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── Dashboard/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── InvigilatorDashboard.jsx
│   │   │   └── InvigilatorSessions.jsx
│   │   ├── Error/
│   │   │   ├── Error401.jsx
│   │   │   ├── Error403.jsx
│   │   │   └── Error404.jsx
│   │   ├── Homepage.jsx
│   │   └── index.js
│   ├── apis/                    # API client modules
│   │   ├── Admin/
│   │   │   └── index.js
│   │   ├── ExamSessions/
│   │   │   └── index.js
│   │   ├── Exams/
│   │   │   └── index.js
│   │   ├── Health/
│   │   ├── Students/
│   │   │   └── index.js
│   │   ├── Users/
│   │   │   └── index.js
│   │   └── VideoAnalysis/
│   │       └── index.js
│   ├── components/              # Reusable components
│   │   ├── Admin/
│   │   │   ├── Admin.jsx
│   │   │   ├── AdminDetail.jsx
│   │   │   ├── AdminExamDetail.jsx
│   │   │   └── InvigilatorDetail.jsx
│   │   ├── ExamSessions/
│   │   │   ├── ExamSessionDetail.jsx
│   │   │   └── ExamSessionsList.jsx
│   │   ├── Exams/
│   │   │   ├── Exam.jsx
│   │   │   └── ExamDetail.jsx
│   │   ├── Layout/
│   │   │   ├── Footer.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Layout.jsx
│   │   ├── Students/
│   │   │   ├── Student.jsx
│   │   │   └── StudentDetail.jsx
│   │   ├── VideoUpload/
│   │   │   ├── VideoUpload.jsx
│   │   │   └── VideoUploadForm.jsx
│   │   ├── ui/                 # UI components
│   │   ├── AdminProtectedRoute.jsx
│   │   ├── InvigilatorProtectedRoute.jsx
│   │   └── ProtectedRoute.jsx
│   ├── contexts/               # React contexts
│   │   └── AuthContext.jsx
│   └── utils/                  # Utility functions
├── tailwind.config.js
└── vite.config.js
```

## Backend (Express) Directory Structure

```
Backend(Express)/
├── .Prettierignore
├── .Prettierrc
├── .env                         # Environment variables
├── .gitignore
├── Public/                      # Static files
├── node_modules/                # Dependencies (ignored)
├── package-lock.json
├── package.json                 # Dependencies and scripts
├── src/
│   ├── app.js                   # Express app configuration
│   ├── index.js                 # Server entry point
│   ├── Config/
│   │   └── db.js                # MongoDB connection
│   ├── Controllers/             # Request handlers
│   │   ├── exam.controller.js
│   │   ├── examSession.controller.js
│   │   ├── user.controller.js
│   │   └── videoAnalysis.controller.js
│   ├── Middleware/              # Middleware
│   │   ├── auth.middleware.js
│   │   └── index.middleware.js
│   ├── Models/                  # Mongoose schemas
│   │   ├── exam.models.js
│   │   ├── examSession.models.js
│   │   ├── user.models.js
│   │   └── videoAnalysis.models.js
│   ├── Options/                 # Configuration options
│   │   └── cookie.options.js
│   ├── Routes/                  # Route definitions
│   │   ├── admin.route.js
│   │   ├── exam.route.js
│   │   ├── examSession.route.js
│   │   ├── index.route.js
│   │   ├── user.route.js
│   │   └── videoAnalysis.route.js
│   ├── Services/                # Business logic
│   │   └── cloudinary.service.js
│   ├── Utils/                   # Utility functions
│   │   └── index.utils.js
│   └── Validation/              # Request validation
│       └── validateExam.middleware.js
```

## AI Services Directory Structure

```
AI SERVICES/
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── .gitignore
├── .idea/                       # IDE config (ignored)
├── .pytest_cache/               # Pytest cache (ignored)
├── .venv/                       # Virtual environment (ignored)
├── __pycache__/                 # Python cache (ignored)
├── annotated_videos/            # Processed video output
├── app/                         # Application code
│   ├── __init__.py
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Auth dependencies
│   │   ├── middleware/
│   │   │   └── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── root.py
│   │       ├── student.py
│   │       └── video.py
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   ├── cloudinary_config.py
│   │   ├── database.py
│   │   └── settings.py
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── responses.py
│   ├── middleware/              # Middleware
│   │   ├── __init__.py
│   │   └── logging.py
│   ├── models/                  # MongoDB models
│   │   ├── __init__.py
│   │   └── student.py
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── student_repository.py
│   │   └── base_repository.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── video.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ai/                  # AI pipeline
│   │   │   ├── __init__.py
│   │   │   ├── analyzers/       # AI analyzers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── head_pose/  # Head pose estimation
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── annotator.py
│   │   │   │   │   ├── axis_drawer.py
│   │   │   │   │   ├── batch_processor.py
│   │   │   │   │   ├── bbox_locator.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── constants.py
│   │   │   │   │   ├── cropper.py
│   │   │   │   │   ├── estimator.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── face_locator.py
│   │   │   │   │   ├── head_pose.py
│   │   │   │   │   ├── keypoint_locator.py
│   │   │   │   │   ├── loader.py
│   │   │   │   │   ├── mapper.py
│   │   │   │   │   ├── monitor.py
│   │   │   │   │   ├── parser.py
│   │   │   │   │   ├── quality_evaluator.py
│   │   │   │   │   ├── result_mapper.py
│   │   │   │   │   ├── result_validator.py
│   │   │   │   │   ├── service.py
│   │   │   │   │   ├── service_initializer.py
│   │   │   │   │   ├── stage.py
│   │   │   │   │   ├── temporal_smoother.py
│   │   │   │   │   ├── text_drawer.py
│   │   │   │   │   ├── track_processor.py
│   │   │   │   │   ├── track_selector.py
│   │   │   │   │   └── validator.py
│   │   │   │   ├── phone/       # Phone detection
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── associator.py
│   │   │   │   │   └── config.py
│   │   │   │   └── pose/        # Pose estimation
│   │   │   │       ├── __init__.py
│   │   │   │       ├── associator.py
│   │   │   │       ├── config.py
│   │   │   │       ├── constants.py
│   │   │   │       ├── estimator.py
│   │   │   │       ├── exceptions.py
│   │   │   │       ├── pose_inference.py
│   │   │   │       ├── pose_pipeline.py
│   │   │   │       ├── pose.py
│   │   │   │       └── validator.py
│   │   │   ├── common/
│   │   │   │   └── __init__.py
│   │   │   ├── detectors/       # Object detectors
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── phone/       # Phone detection
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── service.py
│   │   │   │   │   └── temporal_tracker.py
│   │   │   │   └── yolo/        # YOLO detection
│   │   │   │       ├── __init__.py
│   │   │   │       ├── config.py
│   │   │   │       ├── constants.py
│   │   │   │       ├── detector.py
│   │   │   │       ├── exceptions.py
│   │   │   │       ├── loader.py
│   │   │   │       ├── mapper.py
│   │   │   │       ├── parser.py
│   │   │   │       ├── service.py
│   │   │   │       ├── stage.py
│   │   │   │       └── validator.py
│   │   │   ├── monitoring/      # Logging & events
│   │   │   │   ├── __init__.py
│   │   │   │   ├── event_emitter.py
│   │   │   │   ├── pipeline_logger.py
│   │   │   │   └── socket_manager.py
│   │   │   ├── pipeline/         # Pipeline framework
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base/
│   │   │   │   ├── base_pipeline.py
│   │   │   │   ├── context/
│   │   │   │   ├── factory/
│   │   │   │   ├── frame_context.py
│   │   │   │   ├── interfaces/
│   │   │   │   ├── live_pipeline.py
│   │   │   │   ├── manager/
│   │   │   │   ├── offline/
│   │   │   │   ├── offline_pipeline.py
│   │   │   │   ├── pipeline_factory.py
│   │   │   │   └── pipeline_manager.py
│   │   │   ├── processors/      # Video processors
│   │   │   │   ├── __init__.py
│   │   │   │   ├── frame_extractor.py
│   │   │   │   └── video_processor.py
│   │   │   ├── recognition/     # Face recognition
│   │   │   │   ├── __init__.py
│   │   │   │   └── face_recognizer.py
│   │   │   ├── trackers/        # Object trackers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   └── deepsort/    # DeepSORT tracking
│   │   │   │       ├── __init__.py
│   │   │   │       ├── annotator.py
│   │   │   │       ├── centroid_tracker.py
│   │   │   │       ├── config.py
│   │   │   │       ├── constants.py
│   │   │   │       ├── exceptions.py
│   │   │   │       ├── loader.py
│   │   │   │       ├── mapper.py
│   │   │   │       ├── monitor.py
│   │   │   │       ├── parser.py
│   │   │   │       ├── service.py
│   │   │   │       ├── stage.py
│   │   │   │       ├── track.py
│   │   │   │       ├── track_state_manager.py
│   │   │   │       ├── tracker.py
│   │   │   │       └── validator.py
│   │   │   ├── evidence/         # Evidence capture (empty)
│   │   │   └── reports/          # Report generation (empty)
│   │   ├── backend/              # Backend integration
│   │   │   ├── __init__.py
│   │   │   ├── cloudinary_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── student_service.py
│   │   │   ├── video_client.py
│   │   │   └── video_service.py
│   │   └── utils/                # Utilities
│   │       ├── __init__.py
│   │       ├── objectid.py
│   │       └── validation.py
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── image.py
│   │   └── objectid.py
├── evidence/                    # Evidence storage (empty)
├── logs/                        # Log files
├── main.py                      # FastAPI entry point
├── models/                      # AI model weights
│   ├── 6drepnet/
│   │   └── 6DRepNet_300W_LP_AFLW2000.pth
├── outputs/                     # General output
├── reports/                     # Generated reports (empty)
├── requirements.txt             # Python dependencies
├── scripts/                     # Utility scripts (empty)
├── temp/                        # Temporary files
├── test_deepsort_tracking.py    # DeepSORT test script
├── test_phone_association.py    # Phone association test
├── test_phone_video.py          # Phone video test
├── test_pipeline.py             # Pipeline test
├── test_pose_integration.py     # Pose integration test
├── test_yolo_detection.py       # YOLO detection test
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_deepsort_fixes.py
│   ├── test_head_pose.py
│   ├── test_head_pose_integration.py
│   ├── test_head_pose_pose_keypoints.py
│   ├── test_head_pose_quality_evaluator.py
│   ├── test_phone_detection.py
│   ├── test_pose_estimation.py
│   └── test_temporal_smoothing.py
├── yolo26m-pose.pt              # YOLO model (pose)
├── yolo26m.pt                   # YOLO model (detection)
├── yolov8m-pose.pt              # YOLO model (pose)
└── yolov8m.pt                   # YOLO model (detection)
```

## Important Files by Purpose

### Entry Points
- `Frontend/src/main.jsx` - React entry point
- `Backend(Express)/src/index.js` - Express server entry point
- `AI SERVICES/main.py` - FastAPI entry point

### Configuration
- `Frontend/.env` - Frontend environment variables
- `Backend(Express)/.env` - Backend environment variables
- `AI SERVICES/.env` - AI Services environment variables
- `AI SERVICES/app/config/settings.py` - AI Services settings

### Dependencies
- `Frontend/package.json` - Frontend dependencies
- `Backend(Express)/package.json` - Backend dependencies
- `AI SERVICES/requirements.txt` - Python dependencies

### Database Models
- `Backend(Express)/src/Models/user.models.js` - User schema
- `Backend(Express)/src/Models/exam.models.js` - Exam schema
- `Backend(Express)/src/Models/examSession.models.js` - Exam session schema
- `Backend(Express)/src/Models/videoAnalysis.models.js` - Video analysis schema
- `AI SERVICES/app/models/student.py` - Student model

### API Routes
- `Backend(Express)/src/Routes/user.route.js` - User routes
- `Backend(Express)/src/Routes/exam.route.js` - Exam routes
- `Backend(Express)/src/Routes/examSession.route.js` - Exam session routes
- `Backend(Express)/src/Routes/videoAnalysis.route.js` - Video analysis routes
- `AI SERVICES/app/api/routes/student.py` - Student API
- `AI SERVICES/app/api/routes/video.py` - Video processing API

### AI Pipeline
- `AI SERVICES/app/services/ai/processors/video_processor.py` - Main video processor
- `AI SERVICES/app/services/ai/detectors/yolo/stage.py` - YOLO detection stage
- `AI SERVICES/app/services/ai/trackers/deepsort/stage.py` - DeepSORT tracking stage
- `AI SERVICES/app/services/ai/analyzers/pose/stage.py` - Pose estimation stage
- `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py` - Head pose stage
- `AI SERVICES/app/services/ai/detectors/phone/service.py` - Phone detection service

### Phone Association
- `AI SERVICES/app/services/ai/analyzers/phone/associator.py` - Phone-to-student associator
- `AI SERVICES/app/services/ai/detectors/phone/temporal_tracker.py` - Phone temporal tracker

### Socket.IO
- `AI SERVICES/app/services/ai/monitoring/socket_manager.py` - Socket.IO manager
- `AI SERVICES/app/services/ai/monitoring/pipeline_logger.py` - Pipeline logger
- `AI SERVICES/app/services/ai/monitoring/event_emitter.py` - Event emitter

### Tests
- `AI SERVICES/tests/test_phone_detection.py` - Phone detection tests
- `AI SERVICES/tests/test_head_pose.py` - Head pose tests
- `AI SERVICES/tests/test_deepsort_fixes.py` - DeepSORT tests

## Ignored Directories

The following directories are ignored in documentation as they contain dependencies, caches, or generated files:

- `node_modules/` - npm dependencies
- `.venv/` - Python virtual environment
- `__pycache__/` - Python cache
- `.pytest_cache/` - Pytest cache
- `.git/` - Git repository
- `.idea/` - IDE configuration
- `annotated_videos/` - Generated video output
- `temp/` - Temporary files
- `logs/` - Log files
- `outputs/` - General output

## Related Documentation

- [02 - System Architecture](02%20-%20System%20Architecture.md) - System design overview
- [Frontend/Frontend File Reference](Frontend/Frontend%20File%20Reference.md) - Frontend file details
- [Backend/Backend File Reference](Backend/Backend%20File%20Reference.md) - Backend file details
- [AI Services/AI Services File Reference](AI%20Services/AI%20Services%20File%20Reference.md) - AI Services file details

---
title: Agent Context Guide
project: NeuroProctor
type: guide
status: active
tags:
  - neuroproctor
  - agent
  - context
last_reviewed: 2026-08-03
---

# Agent Context Guide

This guide provides context for AI coding agents working on the NeuroProctor project.

## Project Context

NeuroProctor is an AI-powered exam integrity platform with three main applications:
- **Frontend:** React/Vite application
- **Backend (Express):** Node.js/Express backend
- **AI Services:** FastAPI AI processing backend

## Repository Structure

```
NeuroProctor-AI-based-Exam-Cheating-and-Impersonation-Detection/
├── Frontend/                    # React frontend
├── Backend(Express)/            # Express backend
└── AI SERVICES/                 # FastAPI AI backend
```

## Key Technical Decisions

### Authentication
- JWT tokens shared between Backend and AI Services
- HttpOnly cookies for token storage
- Role-based access control (admin, invigilator)
- `verifyJWT` middleware in Backend
- `require_roles` dependency in AI Services

### Database
- MongoDB shared by all services
- Backend uses Mongoose (sync)
- AI Services uses Motor (async)
- Collections: users, exams, examSessions, videoAnalysis, students

### AI Pipeline
- YOLO object detection (person, cell phone, etc.)
- DeepSORT person tracking
- YOLO Pose estimation (17 COCO keypoints)
- 6DRepNet head pose estimation
- Phone detection with temporal tracking
- Phone-to-student association with wrist-based priority

### Real-Time Communication
- Socket.IO server in AI Services
- Events: pipeline_info, pipeline_error, stage_started, stage_completed, etc.
- Room-based communication for session-specific updates

### Cloud Storage
- Cloudinary for images and videos
- Folders: neuroproctor/students, videos/original, videos/processed

## Recent Bug Fixes

### Phone Association Bug (Fixed)
- **Issue:** Phones incorrectly associated when person bounding boxes overlapped
- **Solution:** Implemented wrist-based priority scoring using COCO keypoints
- **Files:** `AI SERVICES/app/services/ai/analyzers/phone/associator.py`

### Track ID 0 Bug (Fixed)
- **Issue:** Track ID 0 rendered as "Student Unknown"
- **Solution:** Changed boolean check to `is not None` check
- **Files:** `AI SERVICES/app/services/ai/processors/video_processor.py`

## Important Files by Feature

### Authentication
- Backend: `Backend(Express)/src/Middleware/auth.middleware.js`
- Backend: `Backend(Express)/src/Utils/index.utils.js`
- AI Services: `AI SERVICES/app/api/dependencies.py`

### Video Processing
- AI Services: `AI SERVICES/app/services/ai/processors/video_processor.py`
- AI Services: `AI SERVICES/app/services/backend/video_service.py`

### Phone Detection
- AI Services: `AI SERVICES/app/services/ai/detectors/phone/service.py`
- AI Services: `AI SERVICES/app/services/ai/detectors/phone/temporal_tracker.py`
- AI Services: `AI SERVICES/app/services/ai/analyzers/phone/associator.py`

### Socket.IO
- AI Services: `AI SERVICES/app/services/ai/monitoring/socket_manager.py`
- AI Services: `AI SERVICES/app/services/ai/monitoring/pipeline_logger.py`
- AI Services: `AI SERVICES/app/services/ai/monitoring/event_emitter.py`

### Database Models
- Backend: `Backend(Express)/src/Models/`
- AI Services: `AI SERVICES/app/models/`

## Configuration

### Environment Variables
- Frontend: `Frontend/.env`
- Backend: `Backend(Express)/.env`
- AI Services: `AI SERVICES/.env`

**Critical:** `ACCESS_TOKEN_SECRET` must be identical in Backend and AI Services

## Testing

### AI Services Tests
- Location: `AI SERVICES/tests/`
- Framework: pytest
- Run: `cd "AI SERVICES" && pytest tests/ -v`

### Key Test Files
- `test_phone_detection.py` - Phone detection and association
- `test_head_pose.py` - Head pose estimation
- `test_deepsort_fixes.py` - DeepSORT tracking

## Common Patterns

### Adding a New API Endpoint (Backend)

1. Create controller method in `Backend(Express)/src/Controllers/`
2. Add route in `Backend(Express)/src/Routes/`
3. Add `verifyJWT` middleware if protected
4. Add validation if needed

### Adding a New API Endpoint (AI Services)

1. Create route handler in `AI SERVICES/app/api/routes/`
2. Add `require_roles` dependency for authorization
3. Use Pydantic schemas for validation
4. Include router in `main.py`

### Adding a New AI Pipeline Stage

1. Create stage class inheriting from `PipelineStage`
2. Implement `process(context: FrameContext)` method
3. Add configuration class
4. Register in pipeline factory

### Adding Socket.IO Event

1. Use `EventEmitter` helper methods
2. Events: `emit_info`, `emit_warning`, `emit_error`, `emit_stage_started`, etc.
3. Events are automatically broadcast to connected clients

## Code Style

### Backend (Express)
- Use async/await for database operations
- Use wrapperFunction for error handling
- Use ApiError and ApiResponse for consistent responses
- Follow existing naming conventions

### AI Services
- Use type hints (Python 3.10+)
- Use Pydantic for validation
- Use async/await for I/O operations
- Follow existing naming conventions (snake_case)

### Frontend
- Use functional components with hooks
- Use TanStack Query for data fetching
- Use React Hook Form for forms
- Follow existing naming conventions (camelCase)

## Debugging Tips

### Enable Debug Logging
- Backend: Console logs output to terminal
- AI Services: Set `APP_DEBUG=True` in `.env`
- Frontend: Use browser DevTools

### Socket.IO Debugging
- Monitor WebSocket connection in DevTools Network tab
- Check room membership
- Verify event names match exactly

### AI Pipeline Debugging
- Set `PHONE_DEBUG_ENABLED=True` for phone detection debug
- Set `YOLO_VERBOSE=True` for YOLO debug output
- Check logs in `AI SERVICES/logs/`

## Common Pitfalls

### JWT Verification
- Ensure `ACCESS_TOKEN_SECRET` matches between Backend and AI Services
- Check token expiry (15 minutes for access token)
- Verify cookies are being sent (HttpOnly)

### CORS Issues
- Check `CORS_ORIGIN` in AI Services `.env`
- Ensure `allow_credentials=True` is set
- Verify origin matches exactly

### Database Connection
- Ensure MongoDB is running
- Check connection string in `.env`
- Verify database name matches

### Model Loading
- Ensure AI models are downloaded
- Check model paths in `.env`
- Verify GPU availability if using CUDA

## Documentation

### Obsidian Documentation
- Location: `c:\Users\Hamza\Desktop\NeuroProctor\`
- Main entry: `00 - Project Home.md`
- Use `[wikilinks](wikilinks.md)` for internal references

### Code Documentation
- Add docstrings to functions and classes
- Use type hints in Python
- Add JSDoc comments in JavaScript

## When to Ask for Help

### Before Asking
1. Check existing documentation
2. Review similar existing code
3. Check error logs
4. Try to reproduce the issue

### When to Ask
- Architecture decisions
- Security concerns
- Breaking changes
- Unclear requirements
- Blocked by external dependencies

## Related Documentation

- [00 - Project Home](00%20-%20Project%20Home.md) - Main documentation entry
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System design
- [03 - Repository Map](03%20-%20Repository%20Map.md) - File structure
- [05 - Current Implementation Status](05%20-%20Current%20Implementation%20Status.md) - What's implemented

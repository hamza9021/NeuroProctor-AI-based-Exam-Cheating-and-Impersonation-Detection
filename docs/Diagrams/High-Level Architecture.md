---
title: High-Level Architecture
project: NeuroProctor
type: diagram
status: active
tags:
  - neuroproctor
  - diagram
  - architecture
last_reviewed: 2026-08-03
---

# High-Level Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[User Interface]
        Auth[Auth Context]
        API[API Client]
        Socket[Socket.IO Client]
    end
    
    subgraph "Backend (Express)"
        APIRouter[API Router]
        AuthMiddleware[JWT Middleware]
        Controllers[Controllers]
        Services[Services]
        MongoDB[(MongoDB)]
        Cloudinary1[Cloudinary]
    end
    
    subgraph "AI Services (FastAPI)"
        FastAPI[FastAPI App]
        SocketIOServer[Socket.IO Server]
        Pipeline[AI Pipeline]
        YOLO[YOLO Detection]
        DeepSORT[DeepSORT Tracking]
        Pose[Pose Estimation]
        HeadPose[Head Pose]
        Phone[Phone Detection]
        InsightFace[InsightFace]
        MongoDB2[(MongoDB)]
        Cloudinary2[Cloudinary]
    end
    
    UI --> Auth
    UI --> API
    UI --> Socket
    API -->|REST + JWT Cookies| APIRouter
    Socket -->|Socket.IO| SocketIOServer
    APIRouter --> AuthMiddleware
    AuthMiddleware --> Controllers
    Controllers --> Services
    Services --> MongoDB
    Services --> Cloudinary1
    
    FastAPI --> Pipeline
    Pipeline --> YOLO
    Pipeline --> DeepSORT
    Pipeline --> Pose
    Pipeline --> HeadPose
    Pipeline --> Phone
    FastAPI --> InsightFace
    FastAPI --> MongoDB2
    FastAPI --> Cloudinary2
    FastAPI -->|REST API| Services
    
    style Frontend fill:#e1f5ff
    style Backend fill:#fff4e1
    style AI fill:#e1ffe1
```

## Component Descriptions

### Frontend (React)
- **User Interface:** React components for user interaction
- **Auth Context:** Manages authentication state
- **API Client:** Axios for HTTP requests
- **Socket.IO Client:** Real-time event handling

### Backend (Express)
- **API Router:** Route definitions
- **JWT Middleware:** Token verification
- **Controllers:** Request handlers
- **Services:** Business logic
- **MongoDB:** Data persistence
- **Cloudinary:** Image storage

### AI Services (FastAPI)
- **FastAPI App:** API server
- **Socket.IO Server:** Real-time events
- **AI Pipeline:** Video processing stages
- **YOLO Detection:** Object detection
- **DeepSORT Tracking:** Person tracking
- **Pose Estimation:** Body keypoints
- **Head Pose:** Head orientation
- **Phone Detection:** Phone detection
- **InsightFace:** Face recognition
- **MongoDB:** Student data
- **Cloudinary:** Video storage

## Related Documentation

- [02 - System Architecture](02%20-%20System%20Architecture.md) - Detailed architecture
- [Frontend/Frontend Overview](Frontend/Frontend%20Overview.md) - Frontend details
- [Backend/Backend Overview](Backend/Backend%20Overview.md) - Backend details
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services details

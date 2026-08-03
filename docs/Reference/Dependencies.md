---
title: Dependencies
project: NeuroProctor
type: reference
status: active
tags:
  - neuroproctor
  - dependencies
  - packages
last_reviewed: 2026-08-03
---

# Dependencies

This document lists all dependencies used across the three NeuroProctor applications.

## Frontend Dependencies

**File:** `Frontend/package.json`

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^19.0.0 | UI framework |
| react-dom | ^19.0.0 | React DOM renderer |
| react-router-dom | ^7.1.1 | Routing |
| @tanstack/react-query | ^5.62.7 | Server state management |
| axios | ^1.7.9 | HTTP client |
| socket.io-client | ^4.8.1 | Real-time communication |

### UI & Styling

| Package | Version | Purpose |
|---------|---------|---------|
| tailwindcss | ^3.4.17 | CSS framework |
| lucide-react | ^0.468.0 | Icon library |
| clsx | ^2.1.1 | Conditional class names |
| tailwind-merge | ^2.6.0 | Tailwind class merging |

### Forms

| Package | Version | Purpose |
|---------|---------|---------|
| react-hook-form | ^7.54.2 | Form management |
| @hookform/resolvers | ^3.10.0 | Form validation resolvers |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @vitejs/plugin-react | ^4.3.4 | Vite React plugin |
| vite | ^6.0.7 | Build tool |
| eslint | ^9.17.0 | Linting |
| prettier | ^3.4.2 | Code formatting |

---

## Backend (Express) Dependencies

**File:** `Backend(Express)/package.json`

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| express | ^5.0.1 | Web framework |
| mongoose | ^8.9.2 | MongoDB ODM |
| jsonwebtoken | ^9.0.2 | JWT authentication |
| bcrypt | ^5.1.1 | Password hashing |
| cookie-parser | ^1.4.7 | Cookie parsing |
| cors | ^2.8.5 | CORS support |
| multer | ^1.4.5-lts.1 | File uploads |
| cloudinary | ^2.5.1 | Cloud storage |
| joi | ^17.13.3 | Validation |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| nodemon | ^3.1.9 | Auto-reload server |
| prettier | ^3.4.2 | Code formatting |
| eslint | ^9.17.0 | Linting |

---

## AI Services Dependencies

**File:** `AI SERVICES/requirements.txt`

### Core Framework

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ^0.115.0 | Web framework |
| uvicorn | ^0.32.1 | ASGI server |
| python-socketio | ^5.11.4 | Socket.IO |
| aiofiles | ^24.1.0 | Async file operations |
| python-multipart | ^0.0.20 | Multipart form data |

### Database

| Package | Version | Purpose |
|---------|---------|---------|
| motor | ^3.6.0 | Async MongoDB driver |
| pymongo | ^4.10.1 | MongoDB driver |
| pydantic | ^2.10.3 | Data validation |
| pydantic-settings | ^2.6.1 | Settings management |
| bson | ^0.5.0 | BSON encoding/decoding |

### AI/ML

| Package | Version | Purpose |
|---------|---------|---------|
| ultralytics | ^8.3.40 | YOLO models |
| insightface | ^0.7.3 | Face recognition |
| onnxruntime-gpu | ^1.18.0 | ONNX runtime (GPU) |
| onnxruntime | ^1.18.0 | ONNX runtime (CPU fallback) |
| opencv-python | ^4.10.0.88 | Computer vision |
| numpy | ^2.1.3 | Numerical computing |
| pillow | ^11.0.0 | Image processing |
| scikit-learn | ^1.5.2 | Machine learning utilities |
| scipy | ^1.14.1 | Scientific computing |
| sixdrepnet | - | Head pose estimation |

### Cloud Storage

| Package | Version | Purpose |
|---------|---------|---------|
| cloudinary | ^1.41.0 | Cloud storage |

### HTTP Client

| Package | Version | Purpose |
|---------|---------|---------|
| httpx | ^0.28.1 | Async HTTP client |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| python-dotenv | ^1.0.1 | Environment variables |
| loguru | ^0.7.3 | Logging |

### Testing

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ^8.3.4 | Testing framework |
| pytest-asyncio | ^0.24.0 | Async testing |
| pytest-cov | ^6.0.0 | Coverage reporting |

---

## AI Models

### YOLO Models

| Model | Purpose | Source |
|-------|---------|--------|
| yolov8m.pt | Object detection | Ultralytics (auto-download) |
| yolov8m-pose.pt | Pose estimation | Ultralytics (auto-download) |
| yolo26m.pt | Alternative detection | Ultralytics |
| yolo26m-pose.pt | Alternative pose | Ultralytics |

### Head Pose Model

| Model | Purpose | Source |
|-------|---------|--------|
| 6DRepNet_300W_LP_AFLW2000.pth | Head pose estimation | 6DRepNet GitHub (manual download) |

### InsightFace Model

| Model | Purpose | Source |
|-------|---------|--------|
| buffalo_l | Face recognition | InsightFace (auto-download) |

---

## System Requirements

### Frontend

- **Node.js:** v18 or higher
- **npm:** v9 or higher

### Backend (Express)

- **Node.js:** v18 or higher
- **npm:** v9 or higher
- **MongoDB:** v6 or higher

### AI Services

- **Python:** v3.10 or higher
- **MongoDB:** v6 or higher
- **CUDA Toolkit:** Optional (for GPU acceleration)
- **NVIDIA GPU:** Optional (for faster processing)

---

## Related Documentation

- [06 - Setup and Running Guide](06%20-%20Setup%20and%20Running%20Guide.md) - Installation instructions
- [07 - Environment Variables](07%20-%20Environment%20Variables.md) - Configuration reference

---
title: Setup and Running Guide
project: NeuroProctor
type: guide
status: active
tags:
  - neuroproctor
  - setup
  - installation
last_reviewed: 2026-08-03
---

# Setup and Running Guide

## Prerequisites

### Required Software
- **Node.js** (v18 or higher) - For Frontend and Backend
- **Python** (v3.10 or higher) - For AI Services
- **MongoDB** (v6 or higher) - Database
- **Git** - Version control

### Optional but Recommended
- **NVIDIA GPU** with CUDA - For AI processing acceleration
- **CUDA Toolkit** - For GPU support in PyTorch

### Cloud Services
- **Cloudinary Account** - For image and video storage
- Get API Key, API Secret, and Cloud Name from Cloudinary dashboard

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/hamza9021/NeuroProctor-AI-based-Exam-Cheating-and-Impersonation-Detection.git
cd NeuroProctor-AI-based-Exam-Cheating-and-Impersonation-Detection
```

### 2. Setup MongoDB

**Windows:**
- Download MongoDB Community Server from https://www.mongodb.com/try/download/community
- Install with default settings
- MongoDB will start automatically as a Windows service

**Linux/Mac:**
```bash
# Using package manager (Ubuntu/Debian)
sudo apt-get install mongodb

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Verify MongoDB is running:**
```bash
mongosh
# Should connect to mongodb://127.0.0.1:27017
```

### 3. Setup Backend (Express)

```bash
cd "Backend(Express)"

# Install dependencies
npm install

# Create .env file
# Copy from .env.example if available, or create manually
```

**Backend .env file:**
```env
PORT=8080
MONGODB_URI=mongodb://localhost:27017/neuroproctor
ACCESS_TOKEN_SECRET=your-secret-key-change-this
REFRESH_TOKEN_SECRET=your-refresh-secret-change-this
ACCESS_TOKEN_EXPIRY=15m
REFRESH_TOKEN_EXPIRY=7d
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Start Backend:**
```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

Backend will run on `http://localhost:8080`

### 4. Setup Frontend

```bash
cd ../Frontend

# Install dependencies
npm install

# Create .env file
```

**Frontend .env file:**
```env
VITE_API_URL=http://localhost:8080
VITE_AI_API_URL=http://localhost:8000
```

**Start Frontend:**
```bash
# Development mode
npm run dev

# Production build
npm run build
npm run preview
```

Frontend will run on `http://localhost:5173`

### 5. Setup AI Services

```bash
cd ../"AI SERVICES"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
# Copy from .env.example
cp .env.example .env
```

**AI Services .env file:**
```env
# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=True

# CORS
CORS_ORIGIN=http://localhost:5173

# Express Backend
EXPRESS_BACKEND_URL=http://localhost:8080

# MongoDB
MONGO_URI=mongodb://localhost:27017/neuroproctor
MONGO_DB_NAME=neuroproctor

# JWT (MUST match Express backend)
ACCESS_TOKEN_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_STUDENT_FOLDER=neuroproctor/students

# InsightFace
INSIGHTFACE_MODEL_NAME=buffalo_l
INSIGHTFACE_CTX_ID=0
INSIGHTFACE_DET_SIZE=640

# YOLO Detection
YOLO_MODEL=yolov8m.pt
YOLO_DEVICE=auto
YOLO_CONFIDENCE=0.25
YOLO_IOU=0.45
YOLO_IMAGE_SIZE=640
YOLO_VERBOSE=False

# Phone Detection
PHONE_DETECTION_ENABLED=True
PHONE_MODEL_PATH=
PHONE_CLASS_NAME=cell phone
PHONE_CONFIDENCE=0.10
PHONE_IMAGE_SIZE=960
PHONE_FALLBACK_IMAGE_SIZES=768,640
PHONE_MIN_BOX_AREA=10
PHONE_ROI_ENABLED=True
PHONE_ROI_EXPANSION=0.15
PHONE_TEMPORAL_CONFIRM_FRAMES=3
PHONE_TEMPORAL_MAX_MISSED_FRAMES=2
PHONE_ASSOCIATION_IOU=0.10
PHONE_DEDUPLICATION_IOU=0.50
PHONE_DEBUG_ENABLED=False
PHONE_DEBUG_MAX_FRAMES=20
PHONE_RAW_DEBUG_CONFIDENCE=0.01
PHONE_RAW_DEBUG_IMAGE_SIZE=1280
PHONE_TEST_MAX_FRAMES=0
PHONE_TEST_START_FRAME=0
PHONE_TEST_END_FRAME=0
PHONE_TEST_FRAME_STEP=1
PHONE_ASSOCIATION_SWITCH_CONFIRM_FRAMES=3
PHONE_ASSOCIATION_SWITCH_MARGIN=0.20
PHONE_MAX_CENTRE_DISTANCE=100.0
PHONE_MIN_ASSOCIATION_SCORE=0.3

# Head Pose Estimation
HEAD_POSE_MODEL_PATH=models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth
HEAD_POSE_DEVICE=auto
HEAD_POSE_INPUT_SIZE=224
HEAD_POSE_FACE_PADDING=0.20
HEAD_POSE_MIN_FACE_SIZE=40
_head_POSE_MAX_ABS_ANGLE=90.0
HEAD_POSE_ANNOTATION_ENABLED=True
HEAD_POSE_DRAW_AXIS=True
HEAD_POSE_LOG_LEVEL=detailed
HEAD_POSE_FRAME_LOG_INTERVAL=10
HEAD_POSE_SMOOTHING_ENABLED=True
HEAD_POSE_SMOOTHING_ALPHA=0.35
HEAD_POSE_SMOOTHING_MAX_MISSING_FRAMES=5
HEAD_POSE_MAX_SINGLE_FRAME_DELTA=45.0

# Image Validation
MAX_IMAGE_SIZE_MB=5
EMBEDDING_DIMENSION=512

# Directories
OUTPUT_DIR=outputs
LOGS_DIR=logs
TEMP_DIR=temp
ANNOTATED_VIDEOS_DIR=annotated_videos
REPORTS_DIR=reports
EVIDENCE_DIR=evidence
```

**Download AI Models:**

The system will automatically download YOLO models on first run. However, for the head pose model, you need to manually download it:

```bash
# Create models directory
mkdir -p models/6drepnet

# Download 6DRepNet model
# Download from: https://github.com/thohemp/6DRepNet/releases
# Place the file at: models/6drepnet/6DRepNet_300W_LP_AFLW2000.pth
```

**Start AI Services:**
```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

AI Services will run on `http://localhost:8000`

## Running the Complete System

### Start All Services

Open three terminal windows:

**Terminal 1 - Backend:**
```bash
cd "Backend(Express)"
npm run dev
```

**Terminal 2 - AI Services:**
```bash
cd "AI SERVICES"
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd Frontend
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8080
- **AI Services API:** http://localhost:8000
- **AI Services Docs:** http://localhost:8000/api/docs

## Initial Setup Steps

### 1. Create Admin User

1. Navigate to http://localhost:5173
2. Click "Register"
3. Fill in admin details:
   - Role: Select "admin"
   - Upload profile image
4. Register the account

### 2. Create Invigilator User

1. Login as admin
2. Navigate to Admin Dashboard
3. Register a new invigilator user
4. Verify the invigilator (set isVerified to true via database or admin panel)

### 3. Create First Exam

1. Login as invigilator
2. Navigate to Invigilator Dashboard
3. Click "Create Exam"
4. Fill in exam details:
   - Title
   - Description
   - Course name and code
   - Duration
   - Start and end time
5. Create the exam

### 4. Create Exam Session

1. From the exam, click "Create Session"
2. Assign to yourself as invigilator
3. Set session mode (offline/live)
4. Create the session

### 5. Enroll Students

1. Navigate to Students section
2. Click "Add Student"
3. Fill in student details
4. Upload front-facing photo
5. Upload additional pose photos (left, right, up, down)
6. Complete enrollment

### 6. Upload and Process Video

1. Navigate to an exam session
2. Click "Upload Video"
3. Select video file (MP4, AVI, MOV)
4. Watch real-time processing progress
5. Download processed video with annotations

## Troubleshooting

### MongoDB Connection Issues

**Problem:** Backend cannot connect to MongoDB

**Solutions:**
1. Verify MongoDB is running: `mongosh`
2. Check MongoDB URI in .env file
3. Ensure MongoDB is on port 27017
4. Check firewall settings

### GPU Not Detected

**Problem:** AI Services falls back to CPU

**Solutions:**
1. Verify NVIDIA GPU is installed: `nvidia-smi`
2. Install CUDA Toolkit
3. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
4. Set `YOLO_DEVICE=cuda:0` in .env

### CORS Errors

**Problem:** Frontend cannot connect to backend/AI services

**Solutions:**
1. Check CORS_ORIGIN in AI Services .env
2. Ensure it matches frontend URL exactly
3. Check backend CORS middleware configuration

### Model Download Failures

**Problem:** YOLO models fail to download

**Solutions:**
1. Check internet connection
2. Manually download models from Ultralytics
3. Place models in `AI SERVICES/` directory
4. Update YOLO_MODEL path in .env

### Port Conflicts

**Problem:** Services fail to start due to port conflicts

**Solutions:**
1. Change PORT in Backend .env
2. Change APP_PORT in AI Services .env
3. Vite uses random port if 5173 is occupied

### Memory Issues

**Problem:** Video processing runs out of memory

**Solutions:**
1. Reduce PHONE_IMAGE_SIZE in .env
2. Reduce YOLO_IMAGE_SIZE in .env
3. Process shorter videos
4. Close other applications

## Development Tips

### Hot Reloading

- **Frontend:** Vite provides hot module replacement
- **Backend:** Nodemon auto-restarts on changes
- **AI Services:** Uvicorn --reload flag enables auto-reload

### Debugging

- **Frontend:** Use browser DevTools
- **Backend:** Console logs are output to terminal
- **AI Services:** Logs output to terminal with detailed formatting

### Testing

**AI Services Tests:**
```bash
cd "AI SERVICES"
pytest tests/ -v
```

**Run specific test:**
```bash
pytest tests/test_phone_detection.py -v
```

## Production Deployment

### Environment Variables

For production, ensure:
- Set `APP_DEBUG=False` in AI Services
- Use strong JWT secrets
- Restrict CORS origins
- Use HTTPS
- Set up proper logging
- Configure GPU settings appropriately

### Database

- Use MongoDB Atlas or hosted MongoDB
- Set up backups
- Configure indexes for performance

### Cloudinary

- Use production Cloudinary account
- Configure upload presets
- Set up CDN caching

### Deployment Options

- **Frontend:** Vercel, Netlify, or any static hosting
- **Backend:** Heroku, AWS EC2, DigitalOcean
- **AI Services:** AWS EC2 with GPU, Google Cloud GPU

## Related Documentation

- [07 - Environment Variables](07%20-%20Environment%20Variables.md) - Detailed configuration reference
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System design overview
- [01 - Project Overview](01%20-%20Project%20Overview.md) - Project status

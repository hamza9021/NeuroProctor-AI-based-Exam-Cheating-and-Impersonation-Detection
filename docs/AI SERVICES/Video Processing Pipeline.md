---
title: Video Processing Pipeline
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - pipeline
  - video-processing
last_reviewed: 2026-08-03
---

# Video Processing Pipeline

This document details the video processing pipeline in the AI Services application.

## Pipeline Overview

The video processing pipeline processes exam videos through multiple AI stages to detect cheating behaviors.

**Entry Point:** `AI SERVICES/app/services/backend/video_service.py`

**Main Processor:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Pipeline Type:** Offline (pre-recorded video processing)

---

## Pipeline Stages

### Stage 1: Frame Extraction

**Component:** `FrameExtractor`

**File:** `AI SERVICES/app/services/ai/processors/frame_extractor.py`

**Purpose:** Extract frames from video file

**Input:** Video file path

**Output:** Iterator of (frame_number, frame) tuples

**Process:**
1. Open video file using OpenCV VideoCapture
2. Get total frame count
3. Iterate through frames one by one
4. Yield frame number and frame data
5. Close video file on completion

**FrameContext Fields Written:** None (input to pipeline)

**Status:** Implemented

---

### Stage 2: YOLO Detection

**Component:** `YOLODetectionStage`

**File:** `AI SERVICES/app/services/ai/detectors/yolo/stage.py`

**Purpose:** Detect objects in each frame

**Input:** Frame from FrameContext

**Output:** List of Detection objects

**Model:** YOLOv8m (ultralytics)

**Configuration:**
- Confidence threshold: 0.25
- IOU threshold: 0.45
- Image size: 640

**Detected Classes:**
- person
- cell phone
- laptop
- book
- bottle
- (other COCO classes)

**FrameContext Fields Read:** `frame`

**FrameContext Fields Written:** `detections`

**Logging:** Emits `stage_started` and `stage_completed` events

**Status:** Implemented

---

### Stage 3: Non-Person Annotation

**Component:** `_draw_non_person_detections`

**File:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Purpose:** Draw bounding boxes for non-person detections

**Input:** Frame, detections

**Output:** Annotated frame

**Process:**
1. Iterate through detections
2. Skip person detections
3. Draw bounding box with class-specific color
4. Draw label with confidence score

**FrameContext Fields Read:** `detections`

**FrameContext Fields Written:** None (modifies frame directly)

**Status:** Implemented

---

### Stage 4: DeepSORT Tracking

**Component:** `DeepSORTStage`

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/stage.py`

**Purpose:** Track persons across frames

**Input:** Person detections from YOLO

**Output:** List of Track objects

**Model:** DeepSORT

**Configuration:**
- MIN_HITS_TO_CONFIRM: 3
- MAX_AGE: 30
- IOU_THRESHOLD: 0.3

**Track States:**
- `tentative` - New track, not yet confirmed
- `confirmed` - Track has enough hits
- `deleted` - Track has been deleted

**FrameContext Fields Read:** `detections`

**FrameContext Fields Written:** `tracks`

**Logging:** Emits `stage_started` and `stage_completed` events

**Status:** Implemented

---

### Stage 5: Phone Detection

**Component:** `PhoneDetectionService`

**File:** `AI SERVICES/app/services/ai/detectors/phone/service.py`

**Purpose:** Detect phones with temporal tracking and student association

**Input:** Frame, person tracks

**Output:** List of PhoneTrack objects

**Model:** YOLOv8 (phone class)

**Configuration:**
- Confidence threshold: 0.10
- Image size: 960
- Temporal confirm frames: 3
- Temporal max missed frames: 2
- ROI enabled: true
- ROI expansion: 0.15

**Detection Methods:**
- Full-frame detection
- ROI detection (within person bounding boxes)

**Association Method:** Wrist-based priority scoring using COCO keypoints

**FrameContext Fields Read:** `frame`, `tracks`

**FrameContext Fields Written:** `phone_tracks`

**Status:** Implemented

---

### Stage 6: Pose Estimation

**Component:** `YoloPoseStage`

**File:** `AI SERVICES/app/services/ai/analyzers/pose/stage.py`

**Purpose:** Estimate pose keypoints for each person

**Input:** Frame, person tracks

**Output:** List of PoseResult objects

**Model:** YOLO Pose (yolov8m-pose.pt)

**Keypoints:** 17 COCO keypoints (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles)

**Configuration:**
- Confidence threshold: 0.25
- Visibility threshold: 0.5

**FrameContext Fields Read:** `frame`, `tracks`

**FrameContext Fields Written:** `poses`

**Logging:** Emits `stage_started` and `stage_completed` events

**Status:** Implemented

---

### Stage 7: Head Pose Estimation

**Component:** `SixDRepNetHeadPoseStage`

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py`

**Purpose:** Estimate head orientation (yaw, pitch, roll)

**Input:** Frame, poses

**Output:** List of HeadPoseResult objects

**Model:** 6DRepNet

**Configuration:**
- Input size: 224x224
- Face padding: 0.20
- Min face size: 40 pixels
- Smoothing enabled: true
- Smoothing alpha: 0.35
- Max single-frame delta: 45 degrees

**Angles:**
- Yaw - Horizontal rotation
- Pitch - Vertical rotation
- Roll - Tilt rotation

**FrameContext Fields Read:** `frame`, `poses`

**FrameContext Fields Written:** `head_poses`

**Logging:** Emits `stage_started` and `stage_completed` events

**Status:** Implemented

---

### Stage 8: Phone Annotation

**Component:** `_draw_phone_detections`

**File:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Purpose:** Draw phone detections with student association

**Input:** Frame, phone tracks

**Output:** Annotated frame

**Process:**
1. For each phone track
2. Get bounding box coordinates
3. Determine color based on state
4. Draw bounding box
5. Draw label with state, confidence, student association

**FrameContext Fields Read:** `phone_tracks`

**FrameContext Fields Written:** None (modifies frame directly)

**Status:** Implemented

---

### Stage 9: Video Writing

**Component:** OpenCV VideoWriter

**File:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Purpose:** Write annotated frames to output video

**Input:** Annotated frames

**Output:** Annotated video file

**Process:**
1. Get video properties (FPS, width, height)
2. Create VideoWriter with MP4 codec
3. Write each annotated frame
4. Release writer on completion

**FrameContext Fields Read:** None (reads from video processor state)

**FrameContext Fields Written:** None

**Status:** Implemented

---

## FrameContext

**File:** `AI SERVICES/app/services/ai/pipeline/frame_context.py`

**Purpose:** Shared data object passed through pipeline stages

**Structure:**
```python
class FrameContext:
    frame: numpy.ndarray
    frame_number: int
    timestamp: datetime
    detections: List[Detection]
    tracks: List[Track]
    poses: List[PoseResult]
    head_poses: List[HeadPoseResult]
    phone_tracks: List[PhoneTrack]
```

**Usage:** Each stage reads from and writes to FrameContext

---

## Pipeline Orchestration

**File:** `AI SERVICES/app/services/ai/processors/video_processor.py`

**Class:** `VideoProcessor`

**Method:** `process_video(video_path, session_id, exam_id)`

**Process:**
1. Initialize FrameExtractor
2. Initialize AI components (YOLO, DeepSORT, Pose, Head Pose, Phone)
3. Create VideoWriter
4. For each frame:
   - Extract frame
   - Run YOLO detection
   - Draw non-person detections
   - Run DeepSORT tracking
   - Run phone detection
   - Run pose estimation
   - Run head pose estimation
   - Draw phone detections
   - Write annotated frame
   - Emit progress events
5. Close VideoWriter
6. Return processing results

**Socket.IO Events:**
- `pipeline_started`
- `stage_started` (for each stage)
- `stage_completed` (for each stage)
- `pipeline_info` (frame progress)
- `pipeline_completed`

**Status:** Implemented

---

## Related Documentation

- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture
- [AI Services/Object Detection](AI%20Services/Object%20Detection.md) - Object detection details
- [AI Services/DeepSORT Tracking](AI%20Services/DeepSORT%20Tracking.md) - DeepSORT details
- [AI Services/Pose Estimation](AI%20Services/Pose%20Estimation.md) - Pose estimation details
- [AI Services/Head Pose Estimation](AI%20Services/Head%20Pose%20Estimation.md) - Head pose details
- [AI Services/Phone Detection and Association](AI%20Services/Phone%20Detection%20and%20Association.md) - Phone detection details
- [Workflows/Video Processing Workflow](Workflows/Video%20Processing%20Workflow.md) - Video processing workflow

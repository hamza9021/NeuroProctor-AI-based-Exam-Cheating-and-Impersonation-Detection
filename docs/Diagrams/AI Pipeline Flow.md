---
title: AI Pipeline Flow
project: NeuroProctor
type: diagram
status: active
tags:
  - neuroproctor
  - diagram
  - ai-pipeline
last_reviewed: 2026-08-03
---

# AI Pipeline Flow Diagram

## Pipeline Stages

```mermaid
graph LR
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

## Stage Details

### Frame Extractor
- Extracts frames from video file
- Yields (frame_number, frame) tuples
- Uses OpenCV VideoCapture

### YOLO Detection Stage
- Detects objects (person, cell phone, laptop, etc.)
- Returns bounding boxes and confidence scores
- Confidence threshold: 0.25
- IOU threshold: 0.45

### DeepSORT Tracking Stage
- Tracks persons across frames
- Assigns stable track IDs
- States: tentative, confirmed, deleted
- Min hits to confirm: 3

### Phone Detection Service
- Detects phones (full-frame + ROI)
- Temporal tracking for confirmation
- Phone-to-student association with wrist-based priority
- Confirm frames: 3
- Max missed frames: 2

### Pose Estimation Stage
- Estimates 17 COCO keypoints per person
- Associates poses with DeepSORT tracks
- Filters by confidence and visibility

### Head Pose Estimation Stage
- Estimates yaw, pitch, roll angles
- Uses face crops from pose keypoints
- Temporal smoothing (EMA, alpha: 0.35)
- Quality evaluation for filtering

### Video Writer
- Writes annotated frames to output video
- Uses MP4 codec
- Maintains original FPS and resolution

## Related Documentation

- [Workflows/Video Processing Workflow](Workflows/Video%20Processing%20Workflow.md) - Detailed workflow
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services details

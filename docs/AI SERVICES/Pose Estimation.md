---
title: Pose Estimation
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - pose-estimation
  - yolo-pose
last_reviewed: 2026-08-03
---

# Pose Estimation

This document details pose estimation in the AI Services application.

## YOLO Pose Estimation

### Component

**File:** `AI SERVICES/app/services/ai/analyzers/pose/stage.py`

**Class:** `YoloPoseStage`

**Purpose:** Estimate pose keypoints for each person using YOLO Pose

**Status:** Implemented

---

## Input

**FrameContext Fields Read:**
- `frame` - Current video frame
- `tracks` - DeepSORT person tracks

**Input Format:** Frame (numpy array), list of Track objects

---

## Output

**FrameContext Fields Written:**
- `poses` - List of PoseResult objects

**PoseResult Structure:**
```python
class PoseResult:
    track_id: int                    # Associated track ID
    keypoints: [(x, y, conf, vis), ...]  # 17 COCO keypoints
    bbox: [x1, y1, x2, y2]          # Person bounding box
    confidence: float                # Overall confidence
```

**Keypoint Format:** (x, y, confidence, visibility)

---

## Model

**Model:** YOLO Pose (yolov8m-pose.pt)

**Framework:** Ultralytics YOLO

**Keypoints:** 17 COCO keypoints

---

## Configuration

**File:** `AI SERVICES/app/services/ai/analyzers/pose/config.py`

**Settings:**
```python
CONFIDENCE_THRESHOLD: 0.25
VISIBILITY_THRESHOLD: 0.5
IMAGE_SIZE: 640
DEVICE: 'cuda' or 'cpu'
```

---

## COCO Keypoints

**17 Keypoints (in order):**
0. nose
1. left_eye
2. right_eye
3. left_ear
4. right_ear
5. left_shoulder
6. right_shoulder
7. left_elbow
8. right_elbow
9. left_wrist
10. right_wrist
11. left_hip
12. right_hip
13. left_knee
14. right_knee
15. left_ankle
16. right_ankle

---

## Main Classes

### YoloPoseStage

**File:** `AI SERVICES/app/services/ai/analyzers/pose/stage.py`

**Methods:**
- `__init__(config)` - Initialize YOLO Pose model
- `process(context: FrameContext)` - Process frame and return poses

**Dependencies:**
- YOLO Pose model (ultralytics)
- Pose mapper
- Pose validator

---

### PoseService

**File:** `AI SERVICES/app/services/ai/analyzers/pose/service.py`

**Purpose:** Wrapper around YOLO Pose model

**Methods:**
- `estimate(frame, bboxes)` - Estimate poses for given bounding boxes
- `get_model()` - Get YOLO Pose model instance

---

## Main Functions

### estimate_poses

**File:** `AI SERVICES/app/services/ai/analyzers/pose/service.py`

**Purpose:** Run pose estimation on frame

**Input:** Frame, person bounding boxes

**Output:** List of pose results

---

## Dependencies

**Internal:**
- `app/services/ai/analyzers/pose/config.py` - Configuration
- `app/services/ai/analyzers/pose/loader.py` - Model loading
- `app/services/ai/analyzers/pose/mapper.py` - Result mapping
- `app/services/ai/analyzers/pose/validator.py` - Validation

**External:**
- ultralytics - YOLO framework
- torch - PyTorch (backend for YOLO)
- numpy - Array operations

---

## Pipeline Integration Point

**Stage:** Stage 6 (after Phone Detection)

**Integration:** Called by `VideoProcessor.process_video()`

**Sequence:**
```
Phone Detection Service
→ YoloPoseStage
→ Head Pose Estimation Stage
```

---

## FrameContext Fields Read

- `frame` - Current video frame
- `tracks` - DeepSORT person tracks (for bounding boxes)

---

## FrameContext Fields Written

- `poses` - List of PoseResult objects

---

## Logging

**Events Emitted:**
- `stage_started` - When stage begins
- `stage_completed` - When stage completes

**Logging:** Uses PipelineLogger for stage progress

---

## Error Handling

**Errors:**
- Model loading failure
- Invalid frame format
- Estimation failure

**Handling:** Raises custom exceptions from `app/services/ai/analyzers/pose/exceptions.py`

---

## Tests

**File:** `AI SERVICES/tests/test_pose_estimation.py`

**Coverage:** Pose estimation tests

**Status:** Tests implemented

---

## Known Limitations

1. **Fixed Image Size:** All frames resized to 640x640 for estimation
2. **Single Model:** Uses single YOLO Pose model (no ensemble)
3. **No Custom Training:** Uses pre-trained COCO weights
4. **Confidence Threshold:** Fixed at 0.25 (not adaptive)
5. **Visibility Threshold:** Fixed at 0.5 (not adaptive)

---

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/Head Pose Estimation](AI%20Services/Head%20Pose%20Estimation.md) - Head pose details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

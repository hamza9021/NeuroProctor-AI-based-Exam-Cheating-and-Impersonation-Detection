---
title: Head Pose Estimation
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - head-pose
  - 6drepnet
last_reviewed: 2026-08-03
---

# Head Pose Estimation

This document details head pose estimation in the AI Services application.

## 6DRepNet Head Pose Estimation

### Component

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py`

**Class:** `SixDRepNetHeadPoseStage`

**Purpose:** Estimate head orientation (yaw, pitch, roll) using 6DRepNet

**Status:** Implemented

---

## Input

**FrameContext Fields Read:**
- `frame` - Current video frame
- `poses` - YOLO Pose results (for face crops)

**Input Format:** Frame (numpy array), list of PoseResult objects

---

## Output

**FrameContext Fields Written:**
- `head_poses` - List of HeadPoseResult objects

**HeadPoseResult Structure:**
```python
class HeadPoseResult:
    track_id: int          # Associated track ID
    yaw: float             # Horizontal rotation (degrees)
    pitch: float           # Vertical rotation (degrees)
    roll: float            # Tilt rotation (degrees)
    confidence: float      # Detection confidence
    quality_score: float   # Quality evaluation score
```

---

## Model

**Model:** 6DRepNet (6D Rotation Net)

**Model File:** `6DRepNet_300W_LP_AFLW2000.pth`

**Framework:** PyTorch

**Input:** Face crop (224x224)

**Output:** Euler angles (yaw, pitch, roll)

---

## Configuration

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/config.py`

**Settings:**
```python
INPUT_SIZE: 224
FACE_PADDING: 0.20
MIN_FACE_SIZE: 40
SMOOTHING_ENABLED: true
SMOOTHING_ALPHA: 0.35
MAX_SINGLE_FRAME_DELTA: 45
QUALITY_THRESHOLD: 0.5
```

---

## Angles

### Yaw

**Description:** Horizontal rotation (left/right)

**Range:** -90 to +90 degrees

**Positive:** Looking right

**Negative:** Looking left

---

### Pitch

**Description:** Vertical rotation (up/down)

**Range:** -90 to +90 degrees

**Positive:** Looking down

**Negative:** Looking up

---

### Roll

**Description:** Tilt rotation (clockwise/counter-clockwise)

**Range:** -90 to +90 degrees

**Positive:** Tilted right

**Negative:** Tilted left

---

## Main Classes

### SixDRepNetHeadPoseStage

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/stage.py`

**Methods:**
- `__init__(config)` - Initialize 6DRepNet model
- `process(context: FrameContext)` - Process frame and return head poses

**Dependencies:**
- 6DRepNet model
- Head pose service
- Head pose mapper
- Head pose validator

---

### HeadPoseService

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/service.py`

**Purpose:** Wrapper around 6DRepNet model

**Methods:**
- `estimate(frame, poses)` - Estimate head poses for given poses
- `get_model()` - Get 6DRepNet model instance

---

### TemporalSmoother

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/temporal_smoother.py`

**Purpose:** Apply temporal smoothing to head pose angles

**Methods:**
- `smooth(track_id, yaw, pitch, roll)` - Smooth angles using EMA
- `reset_track(track_id)` - Reset smoothing for a track

**Smoothing Algorithm:** Exponential Moving Average (EMA)

---

## Main Functions

### estimate_head_poses

**File:** `AI SERVICES/app/services/ai/analyzers/head_pose/service.py`

**Purpose:** Run head pose estimation on face crops

**Input:** Frame, pose results

**Output:** List of head pose results

---

## Dependencies

**Internal:**
- `app/services/ai/analyzers/head_pose/config.py` - Configuration
- `app/services/ai/analyzers/head_pose/loader.py` - Model loading
- `app/services/ai/analyzers/head_pose/mapper.py` - Result mapping
- `app/services/ai/analyzers/head_pose/validator.py` - Validation
- `app/services/ai/analyzers/head_pose/temporal_smoother.py` - Temporal smoothing
- `app/services/ai/analyzers/head_pose/quality_evaluator.py` - Quality evaluation

**External:**
- torch - PyTorch (backend for 6DRepNet)
- numpy - Array operations
- sixdrepnet - 6DRepNet implementation

---

## Pipeline Integration Point

**Stage:** Stage 7 (after Pose Estimation)

**Integration:** Called by `VideoProcessor.process_video()`

**Sequence:**
```
YoloPoseStage
→ SixDRepNetHeadPoseStage
→ Phone Annotation
```

---

## FrameContext Fields Read

- `frame` - Current video frame
- `poses` - YOLO Pose results (for face crop locations)

---

## FrameContext Fields Written

- `head_poses` - List of HeadPoseResult objects

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
- Face crop failure
- Estimation failure

**Handling:** Raises custom exceptions from `app/services/ai/analyzers/head_pose/exceptions.py`

---

## Tests

**File:** `AI SERVICES/tests/test_head_pose.py`

**Coverage:** Comprehensive head pose tests

**Status:** Tests implemented

**Additional Tests:**
- `test_head_pose_integration.py` - Integration tests
- `test_head_pose_pose_keypoints.py` - Keypoint tests
- `test_head_pose_quality_evaluator.py` - Quality evaluation tests
- `test_temporal_smoothing.py` - Smoothing tests

---

## Known Limitations

1. **Fixed Input Size:** Face crops resized to 224x224
2. **Face Crop Quality:** Dependent on pose estimation accuracy
3. **Single Model:** Uses single 6DRepNet model (no ensemble)
4. **Smoothing Parameters:** Fixed alpha value (not adaptive)
5. **Quality Threshold:** Fixed at 0.5 (not adaptive)

---

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/Pose Estimation](AI%20Services/Pose%20Estimation.md) - Pose estimation details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

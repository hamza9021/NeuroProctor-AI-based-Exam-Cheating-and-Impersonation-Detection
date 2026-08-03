---
title: Phone Detection and Association
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - phone-detection
  - association
last_reviewed: 2026-08-03
---

# Phone Detection and Association

This document details phone detection and student association in the AI Services application.

## Phone Detection Service

### Component

**File:** `AI SERVICES/app/services/ai/detectors/phone/service.py`

**Class:** `PhoneDetectionService`

**Purpose:** Detect phones with temporal tracking and associate with students

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
- `phone_tracks` - List of PhoneTrack objects

**PhoneTrack Structure:**
```python
class PhoneTrack:
    phone_track_id: int     # Phone track ID
    bounding_box: [x1, y1, x2, y2]  # Bounding box
    confidence: float       # Detection confidence
    state: PhoneState       # candidate, confirmed, lost
    student_track_id: int or None  # Associated person track ID
    association_method: str # Method used for association
    last_seen_frame: int    # Last frame where phone was seen
```

---

## Model

**Model:** YOLOv8 (phone class)

**Model File:** `yolov8m.pt` (same as object detection)

**Framework:** Ultralytics YOLO

---

## Configuration

**File:** `AI SERVICES/app/services/ai/detectors/phone/config.py`

**Settings:**
```python
CONFIDENCE_THRESHOLD: 0.10
IMAGE_SIZE: 960
TEMPORAL_CONFIRM_FRAMES: 3
TEMPORAL_MAX_MISSED_FRAMES: 2
ROI_ENABLED: true
ROI_EXPANSION: 0.15
```

---

## Detection Methods

### Full-Frame Detection

**Description:** Detect phones in entire frame

**Usage:** Initial detection

**Pros:** Detects phones anywhere in frame

**Cons:** Higher false positive rate

---

### ROI Detection

**Description:** Detect phones within person bounding boxes (Region of Interest)

**Usage:** Focused detection after initial detection

**Pros:** Lower false positive rate, faster

**Cons:** May miss phones outside person bounding boxes

---

## Phone States

### candidate

**Description:** New phone detection, not yet confirmed

**Transition:** Confirmed after `TEMPORAL_CONFIRM_FRAMES` detections

**Usage:** Phone is not yet reliable

---

### confirmed

**Description:** Phone has been detected consistently

**Transition:** Lost after `TEMPORAL_MAX_MISSED_FRAMES` frames without detection

**Usage:** Reliable phone detection

---

### lost

**Description:** Phone has not been detected for several frames

**Transition:** Candidate if detected again

**Usage:** Phone was confirmed but is now lost

---

## Association Methods

### Wrist-Based Association

**File:** `AI SERVICES/app/services/ai/detectors/phone/associator.py`

**Description:** Associate phone with student based on wrist proximity

**Process:**
1. Get wrist keypoints from pose (left_wrist, right_wrist)
2. Calculate distance from phone bounding box to each wrist
3. Assign phone to student with closest wrist
4. Use priority scoring for tie-breaking

**Priority:**
- Right wrist (higher priority for right-handed users)
- Left wrist (lower priority)

**Threshold:** Maximum distance for association

---

## Main Classes

### PhoneDetectionService

**File:** `AI SERVICES/app/services/ai/detectors/phone/service.py`

**Methods:**
- `__init__(config)` - Initialize phone detector
- `detect(frame, tracks)` - Detect phones and update tracks
- `get_phone_tracks()` - Get current phone tracks
- `reset()` - Reset phone tracks

**Dependencies:**
- YOLO model
- Phone associator
- Temporal tracker

---

### PhoneAssociator

**File:** `AI SERVICES/app/services/ai/detectors/phone/associator.py`

**Purpose:** Associate phone detections with student tracks

**Methods:**
- `associate(phone_bbox, tracks, poses)` - Associate phone with student
- `calculate_wrist_distance(phone_bbox, wrist_keypoint)` - Calculate distance

**Dependencies:**
- Pose keypoints
- Track bounding boxes

---

## Main Functions

### detect_phones

**File:** `AI SERVICES/app/services/ai/detectors/phone/service.py`

**Purpose:** Run phone detection on frame

**Input:** Frame, person tracks

**Output:** Updated phone tracks

---

## Dependencies

**Internal:**
- `app/services/ai/detectors/phone/config.py` - Configuration
- `app/services/ai/detectors/phone/associator.py` - Association logic
- `app/services/ai/detectors/phone/validator.py` - Validation

**External:**
- ultralytics - YOLO framework
- torch - PyTorch (backend for YOLO)
- numpy - Array operations

---

## Pipeline Integration Point

**Stage:** Stage 5 (after DeepSORT Tracking)

**Integration:** Called by `VideoProcessor.process_video()`

**Sequence:**
```
DeepSORTStage
→ PhoneDetectionService
→ YoloPoseStage
```

---

## FrameContext Fields Read

- `frame` - Current video frame
- `tracks` - DeepSORT person tracks

---

## FrameContext Fields Written

- `phone_tracks` - List of PhoneTrack objects

---

## Logging

**Events Emitted:** None (phone detection is internal to pipeline)

**Logging:** Uses PipelineLogger for debug logging

---

## Error Handling

**Errors:**
- Detection failure
- Association failure
- Invalid frame format

**Handling:** Raises custom exceptions

---

## Tests

**File:** `AI SERVICES/tests/test_phone_detection.py`

**Coverage:** Comprehensive phone detection tests

**Status:** Tests implemented

---

## Known Limitations

1. **Fixed Thresholds:** Confidence and distance thresholds are fixed
2. **Wrist-Only Association:** Only uses wrist keypoints (may miss other associations)
3. **No Hand Detection:** Does not detect hands directly
4. **Temporal Parameters:** Fixed confirm/missed frame counts
5. **ROI Expansion:** Fixed expansion factor (not adaptive)

---

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/Object Detection](AI%20Services/Object%20Detection.md) - Object detection details
- [AI Services/DeepSORT Tracking](AI%20Services/DeepSORT%20Tracking.md) - DeepSORT details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

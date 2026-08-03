---
title: DeepSORT Tracking
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - tracking
  - deepsort
last_reviewed: 2026-08-03
---

# DeepSORT Tracking

This document details person tracking using DeepSORT in the AI Services application.

## DeepSORT Tracking

### Component

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/stage.py`

**Class:** `DeepSORTStage`

**Purpose:** Track persons across video frames using DeepSORT

**Status:** Implemented

---

## Input

**FrameContext Fields Read:**
- `detections` - YOLO person detections
- `frame` - Current video frame

**Input Format:** List of Detection objects with class 'person'

---

## Output

**FrameContext Fields Written:**
- `tracks` - List of Track objects

**Track Structure:**
```python
class Track:
    track_id: int              # Stable track ID
    bbox: [x1, y1, x2, y2]   # Bounding box
    state: TrackState          # tentative, confirmed, deleted
    hits: int                  # Number of detections
    age: int                   # Track age in frames
    time_since_update: int     # Frames since last update
    class_name: str            # 'person'
```

---

## Model

**Model:** DeepSORT (Simple Online and Realtime Tracking)

**Components:**
- Kalman Filter - Motion prediction
- Hungarian Algorithm - Data association
- Re-Identification Model - Appearance matching

**Model File:** DeepSORT weights (auto-downloaded)

---

## Configuration

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/config.py`

**Settings:**
```python
MIN_HITS_TO_CONFIRM: 3
MAX_AGE: 30
IOU_THRESHOLD: 0.3
NN_BUDGET: 100
MAX_DIST: 0.2
```

---

## Track States

### tentative

**Description:** New track, not yet confirmed

**Transition:** Confirmed after `MIN_HITS_TO_CONFIRM` detections

**Usage:** Track is not yet reliable

---

### confirmed

**Description:** Track has enough detections to be confirmed

**Transition:** Deleted after `MAX_AGE` frames without update

**Usage:** Reliable track for analysis

---

### deleted

**Description:** Track has been lost for too long

**Transition:** None (terminal state)

**Usage:** Track is no longer active

---

## Main Classes

### DeepSORTStage

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/stage.py`

**Methods:**
- `__init__(config)` - Initialize DeepSORT tracker
- `process(context: FrameContext)` - Process detections and update tracks

**Dependencies:**
- DeepSORT service
- Track mapper
- Track validator

---

### DeepSORTService

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/service.py`

**Purpose:** Wrapper around DeepSORT tracker

**Methods:**
- `update(detections, frame)` - Update tracker with new detections
- `get_tracks()` - Get current tracks
- `get_tracker()` - Get DeepSORT instance

---

## Main Functions

### update_tracks

**File:** `AI SERVICES/app/services/ai/trackers/deepsort/service.py`

**Purpose:** Update DeepSORT tracker with new detections

**Input:** Person detections, current frame

**Output:** Updated track list

---

## Dependencies

**Internal:**
- `app/services/ai/trackers/deepsort/config.py` - Configuration
- `app/services/ai/trackers/deepsort/loader.py` - Model loading
- `app/services/ai/trackers/deepsort/mapper.py` - Result mapping
- `app/services/ai/trackers/deepsort/validator.py` - Validation
- `app/services/ai/trackers/deepsort/track.py` - Track class
- `app/services/ai/trackers/deepsort/track_state_manager.py` - State management

**External:**
- deep-sort-realtime - DeepSORT implementation
- torch - PyTorch (backend for re-ID model)
- numpy - Array operations

---

## Pipeline Integration Point

**Stage:** Stage 4 (after YOLO Detection and Non-Person Annotation)

**Integration:** Called by `VideoProcessor.process_video()`

**Sequence:**
```
YOLODetectionStage
→ DeepSORTStage
→ Phone Detection Service
```

---

## FrameContext Fields Read

- `detections` - YOLO detections (filtered for 'person' class)
- `frame` - Current video frame (for appearance matching)

---

## FrameContext Fields Written

- `tracks` - List of Track objects

---

## Logging

**Events Emitted:**
- `stage_started` - When stage begins
- `stage_completed` - When stage completes

**Logging:** Uses PipelineLogger for stage progress

---

## Error Handling

**Errors:**
- Tracker initialization failure
- Invalid detection format
- Update failure

**Handling:** Raises custom exceptions from `app/services/ai/trackers/deepsort/exceptions.py`

---

## Tests

**File:** `AI SERVICES/tests/test_deepsort_fixes.py`

**Coverage:** DeepSORT tracking tests

**Status:** Tests implemented

---

## Known Limitations

1. **Fixed Parameters:** MIN_HITS_TO_CONFIRM and MAX_AGE are fixed
2. **No Re-Training:** Uses pre-trained re-ID model
3. **Occlusion Handling:** Limited occlusion handling
4. **ID Switching:** May occur with similar-looking persons

---

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/Object Detection](AI%20Services/Object%20Detection.md) - Object detection details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

---
title: Object Detection
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - object-detection
  - yolo
last_reviewed: 2026-08-03
---

# Object Detection

This document details object detection in the AI Services application.

## YOLO Detection

### Component

**File:** `AI SERVICES/app/services/ai/detectors/yolo/stage.py`

**Class:** `YOLODetectionStage`

**Purpose:** Detect objects in video frames using YOLOv8

**Status:** Implemented

---

## Input

**FrameContext Fields Read:**
- `frame` - Current video frame (numpy array)

**Input Format:** RGB image (height, width, 3)

---

## Output

**FrameContext Fields Written:**
- `detections` - List of Detection objects

**Detection Structure:**
```python
class Detection:
    bbox: [x1, y1, x2, y2]  # Bounding box coordinates
    confidence: float         # Detection confidence (0-1)
    class_name: str           # Class name
    class_id: int            # COCO class ID
```

---

## Model

**Model:** YOLOv8m (ultralytics)

**Model File:** `yolov8m.pt` (auto-downloaded)

**Framework:** Ultralytics YOLO

---

## Configuration

**File:** `AI SERVICES/app/services/ai/detectors/yolo/config.py`

**Settings:**
```python
CONFIDENCE_THRESHOLD: 0.25
IOU_THRESHOLD: 0.45
IMAGE_SIZE: 640
DEVICE: 'cuda' or 'cpu'
```

---

## Detected Classes

**COCO Classes:**
- person (class_id: 0)
- cell phone (class_id: 67)
- laptop (class_id: 63)
- book (class_id: 84)
- bottle (class_id: 44)
- (other 80 COCO classes)

**Classes of Interest:**
- person - For tracking and pose estimation
- cell phone - For phone detection
- laptop - For cheating detection
- book - For cheating detection

---

## Main Classes

### YOLODetectionStage

**File:** `AI SERVICES/app/services/ai/detectors/yolo/stage.py`

**Methods:**
- `__init__(config)` - Initialize YOLO model
- `process(context: FrameContext)` - Process frame and return detections

**Dependencies:**
- YOLO model (ultralytics)
- Detection mapper
- Detection validator

---

### YOLODetector

**File:** `AI SERVICES/app/services/ai/detectors/yolo/detector.py`

**Purpose:** Wrapper around Ultralytics YOLO model

**Methods:**
- `detect(frame)` - Run detection on frame
- `get_model()` - Get YOLO model instance

---

## Main Functions

### detect_objects

**File:** `AI SERVICES/app/services/ai/detectors/yolo/detector.py`

**Purpose:** Run YOLO detection on frame

**Input:** Frame (numpy array)

**Output:** Raw YOLO results

---

## Dependencies

**Internal:**
- `app/services/ai/detectors/yolo/config.py` - Configuration
- `app/services/ai/detectors/yolo/loader.py` - Model loading
- `app/services/ai/detectors/yolo/mapper.py` - Result mapping
- `app/services/ai/detectors/yolo/validator.py` - Validation

**External:**
- ultralytics - YOLO framework
- torch - PyTorch (backend for YOLO)
- numpy - Array operations

---

## Pipeline Integration Point

**Stage:** Stage 2 (after Frame Extraction)

**Integration:** Called by `VideoProcessor.process_video()`

**Sequence:**
```
FrameExtractor
→ YOLODetectionStage
→ DeepSORTStage
```

---

## FrameContext Fields Read

- `frame` - Current video frame

---

## FrameContext Fields Written

- `detections` - List of Detection objects

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
- Detection failure

**Handling:** Raises custom exceptions from `app/services/ai/detectors/yolo/exceptions.py`

---

## Tests

**File:** `AI SERVICES/tests/test_phone_detection.py`

**Coverage:** Phone detection tests (uses YOLO)

**Status:** Tests implemented

---

## Known Limitations

1. **Fixed Image Size:** All frames resized to 640x640 for detection
2. **Single Model:** Uses single YOLOv8m model (no ensemble)
3. **No Custom Training:** Uses pre-trained COCO weights
4. **Confidence Threshold:** Fixed at 0.25 (not adaptive)

---

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/DeepSORT Tracking](AI%20Services/DeepSORT%20Tracking.md) - DeepSORT details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

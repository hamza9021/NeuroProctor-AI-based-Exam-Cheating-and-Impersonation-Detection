---
title: FrameContext
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - framecontext
  - pipeline
last_reviewed: 2026-08-03
---

# FrameContext

This document details the FrameContext data structure used in the AI pipeline.

## Purpose

FrameContext is a shared data object that is passed through all pipeline stages. Each stage reads from and writes to FrameContext to share data between stages.

## File Location

**File:** `AI SERVICES/app/services/ai/pipeline/frame_context.py`

## Structure

```python
@dataclass
class FrameContext:
    frame: np.ndarray              # Current frame (numpy array)
    frame_number: int              # Frame number in video
    timestamp: datetime            # Frame timestamp
    detections: List[Detection]    # YOLO detections
    tracks: List[Track]            # DeepSORT person tracks
    poses: List[PoseResult]        # Pose estimation results
    head_poses: List[HeadPoseResult]  # Head pose results
    phone_tracks: List[PhoneTrack]  # Phone detection tracks
```

## Field Descriptions

### frame

**Type:** `numpy.ndarray`

**Purpose:** Current video frame

**Written by:** FrameExtractor (input to pipeline)

**Read by:** All stages

**Shape:** (height, width, 3) - RGB image

---

### frame_number

**Type:** `int`

**Purpose:** Frame number in the video sequence (0-indexed)

**Written by:** FrameExtractor

**Read by:** Pipeline for progress tracking

---

### timestamp

**Type:** `datetime`

**Purpose:** Timestamp of the frame

**Written by:** FrameExtractor

**Read by:** Pipeline for timing analysis

---

### detections

**Type:** `List[Detection]`

**Purpose:** YOLO object detection results

**Written by:** YOLO Detection Stage

**Read by:** DeepSORT Stage, Phone Detection Stage, Non-Person Annotation

**Detection Structure:**
```python
class Detection:
    bbox: [x1, y1, x2, y2]  # Bounding box coordinates
    confidence: float         # Detection confidence (0-1)
    class_name: str           # Class name (e.g., 'person', 'cell phone')
    class_id: int            # COCO class ID
```

---

### tracks

**Type:** `List[Track]`

**Purpose:** DeepSORT person tracking results

**Written by:** DeepSORT Stage

**Read by:** Phone Detection Stage, Pose Estimation Stage, Head Pose Estimation Stage

**Track Structure:**
```python
class Track:
    track_id: int              # Stable track ID
    bbox: [x1, y1, x2, y2]   # Bounding box
    state: TrackState          # tentative, confirmed, deleted
    hits: int                  # Number of detections
    age: int                   # Track age in frames
    time_since_update: int     # Frames since last update
```

---

### poses

**Type:** `List[PoseResult]`

**Purpose:** YOLO Pose estimation results

**Written by:** Pose Estimation Stage

**Read by:** Head Pose Estimation Stage

**PoseResult Structure:**
```python
class PoseResult:
    track_id: int                    # Associated track ID
    keypoints: [(x, y, conf, vis), ...]  # 17 COCO keypoints
    bbox: [x1, y1, x2, y2]          # Person bounding box
    confidence: float                # Overall confidence
```

**Keypoint Order (COCO):**
0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear,
5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow,
9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip,
13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle

---

### head_poses

**Type:** `List[HeadPoseResult]`

**Purpose:** 6DRepNet head pose estimation results

**Written by:** Head Pose Estimation Stage

**Read by:** (Currently not read by subsequent stages)

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

### phone_tracks

**Type:** `List[PhoneTrack]`

**Purpose:** Phone detection and tracking results

**Written by:** Phone Detection Service

**Read by:** Phone Annotation Stage

**PhoneTrack Structure:**
```python
class PhoneTrack:
    phone_track_id: int     # Phone track ID
    bounding_box: [x1, y1, x2, y2]  # Bounding box
    confidence: float       # Detection confidence
    state: PhoneState       # candidate, confirmed, lost
    student_track_id: int or None  # Associated person track ID
    association_method: str # Method used for association
```

---

## Data Flow Through Pipeline

```
FrameExtractor
→ frame, frame_number, timestamp

YOLO Detection
→ detections

DeepSORT
→ tracks

Phone Detection
→ phone_tracks

Pose Estimation
→ poses

Head Pose Estimation
→ head_poses

Video Writer
→ (reads annotated frame)
```

## Usage Example

```python
# Create context
context = FrameContext(
    frame=frame,
    frame_number=100,
    timestamp=datetime.now()
)

# Process through stages
context = yolo_stage.process(context)
context = deepsort_stage.process(context)
context = pose_stage.process(context)
```

## Related Documentation

- [AI Services/Video Processing Pipeline](AI%20Services/Video%20Processing%20Pipeline.md) - Pipeline details
- [AI Services/AI Architecture](AI%20Services/AI%20Architecture.md) - AI architecture

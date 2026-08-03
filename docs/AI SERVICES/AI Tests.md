---
title: AI Tests
project: NeuroProctor
type: reference
service: ai-services
status: active
tags:
  - neuroproctor
  - ai-services
  - testing
last_reviewed: 2026-08-03
---

# AI Tests

This document details the test suite for the AI Services application.

## Test Framework

**Framework:** pytest

**Async Support:** pytest-asyncio

**Coverage:** pytest-cov

---

## Test Directory

**Location:** `AI SERVICES/tests/`

---

## Test Files

### test_deepsort_fixes.py

**Purpose:** Test DeepSORT tracking fixes

**Coverage:**
- Track initialization
- Track state transitions
- Track deletion
- Track ID stability

**Status:** Implemented

---

### test_head_pose.py

**Purpose:** Comprehensive head pose estimation tests

**Coverage:**
- Model loading
- Head pose estimation
- Angle calculations
- Quality evaluation
- Temporal smoothing

**Status:** Implemented

---

### test_head_pose_integration.py

**Purpose:** Integration tests for head pose

**Coverage:**
- End-to-end head pose pipeline
- Integration with pose estimation
- Integration with tracking

**Status:** Implemented

---

### test_head_pose_pose_keypoints.py

**Purpose:** Test head pose with pose keypoints

**Coverage:**
- Keypoint extraction
- Face cropping from keypoints
- Head pose from face crops

**Status:** Implemented

---

### test_head_pose_quality_evaluator.py

**Purpose:** Test quality evaluation for head pose

**Coverage:**
- Quality score calculation
- Quality threshold filtering
- Quality metrics

**Status:** Implemented

---

### test_phone_detection.py

**Purpose:** Comprehensive phone detection tests

**Coverage:**
- Phone detection
- Temporal tracking
- Phone-to-student association
- ROI detection

**Status:** Implemented

---

### test_pose_estimation.py

**Purpose:** Test pose estimation

**Coverage:**
- YOLO Pose model loading
- Pose estimation
- Keypoint extraction
- Confidence filtering

**Status:** Implemented

---

### test_temporal_smoothing.py

**Purpose:** Test temporal smoothing algorithms

**Coverage:**
- Exponential moving average
- Angle smoothing
- Track-based smoothing
- Smoothing parameters

**Status:** Implemented

---

## Running Tests

### Run All Tests

```bash
cd AI SERVICES
pytest
```

### Run Specific Test File

```bash
pytest tests/test_head_pose.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run in Verbose Mode

```bash
pytest -v
```

---

## Test Coverage

**Current Coverage Areas:**
- DeepSORT tracking
- Head pose estimation
- Phone detection
- Pose estimation
- Temporal smoothing

**Missing Coverage:**
- YOLO detection (standalone)
- Student API endpoints
- Video processing endpoints
- Socket.IO events
- Integration tests for full pipeline

---

## Related Documentation

- [12 - Testing Guide](12%20-%20Testing%20Guide.md) - Testing guide
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services overview

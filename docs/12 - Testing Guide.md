---
title: Testing Guide
project: NeuroProctor
type: guide
status: active
tags:
  - neuroproctor
  - testing
  - quality
last_reviewed: 2026-08-03
---

# Testing Guide

This document describes the testing approach and coverage across the NeuroProctor system.

## Test Coverage Overview

### AI Services Tests

**Status:** Good coverage for AI components

**Test Directory:** `AI SERVICES/tests/`

**Test Framework:** pytest with pytest-asyncio

**Test Files:**
- `test_phone_detection.py` - Phone detection and association (43 tests)
- `test_head_pose.py` - Head pose estimation (comprehensive)
- `test_head_pose_integration.py` - Head pose integration
- `test_head_pose_pose_keypoints.py` - Pose keypoint handling
- `test_head_pose_quality_evaluator.py` - Quality evaluation
- `test_deepsort_fixes.py` - DeepSORT tracking fixes
- `test_pose_estimation.py` - Pose estimation
- `test_temporal_smoothing.py` - Temporal smoothing

### Frontend Tests

**Status:** No automated tests currently

**Recommendation:** Add React Testing Library and Jest for component testing

### Backend (Express) Tests

**Status:** No automated tests currently

**Recommendation:** Add Jest or Mocha for API endpoint testing

## Running AI Services Tests

### Prerequisites

```bash
cd "AI SERVICES"
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_phone_detection.py -v
```

### Run Specific Test

```bash
pytest tests/test_phone_detection.py::test_phone_association -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

## Test File Details

### test_phone_detection.py

**Purpose:** Test phone detection and association logic

**Key Test Cases:**
- Phone detection confidence filtering
- Phone-to-student association
- ROI-based phone detection
- Temporal phone tracking
- Phone deduplication
- Track ID 0 handling
- Unconfirmed track handling
- Wrist-based association priority

**Recent Updates:**
- Added tests for wrist-based association
- Added tests for Track ID 0 rendering
- Added tests for unconfirmed tracks with hits

**Source:** `AI SERVICES/tests/test_phone_detection.py`

---

### test_head_pose.py

**Purpose:** Test head pose estimation pipeline

**Key Test Areas:**
- Face localization
- Face cropping
- Head pose estimation
- Temporal smoothing
- Quality evaluation
- Rule evaluation
- Annotation

**Source:** `AI SERVICES/tests/test_head_pose.py`

---

### test_deepsort_fixes.py

**Purpose:** Test DeepSORT tracking fixes

**Key Test Areas:**
- Track creation and confirmation
- Track state management
- Track expiration
- Track ID stability

**Source:** `AI SERVICES/tests/test_deepsort_fixes.py`

---

### test_pose_estimation.py

**Purpose:** Test pose estimation integration

**Key Test Areas:**
- YOLO Pose inference
- Keypoint extraction
- Pose-to-track association
- Confidence filtering

**Source:** `AI SERVICES/tests/test_pose_estimation.py`

---

### test_temporal_smoothing.py

**Purpose:** Test temporal smoothing algorithms

**Key Test Areas:**
- Exponential moving average
- Spike protection
- Missing frame handling
- State persistence

**Source:** `AI SERVICES/tests/test_temporal_smoothing.py`

---

## Manual Testing Scripts

The AI Services directory includes several manual testing scripts:

### test_yolo_detection.py

**Purpose:** Test YOLO object detection on images/videos

**Usage:**
```bash
cd "AI SERVICES"
python test_yolo_detection.py
```

**Source:** `AI SERVICES/test_yolo_detection.py`

---

### test_phone_video.py

**Purpose:** Test phone detection on a video file

**Usage:**
```bash
cd "AI SERVICES"
python test_phone_video.py
```

**Source:** `AI SERVICES/test_phone_video.py`

---

### test_pipeline.py

**Purpose:** Test the complete AI pipeline

**Usage:**
```bash
cd "AI SERVICES"
python test_pipeline.py
```

**Source:** `AI SERVICES/test_pipeline.py`

---

### test_pose_integration.py

**Purpose:** Test pose integration with tracking

**Usage:**
```bash
cd "AI SERVICES"
python test_pose_integration.py
```

**Source:** `AI SERVICES/test_pose_integration.py`

---

## Integration Testing

### End-to-End Video Processing Test

**Purpose:** Test complete video upload and processing workflow

**Steps:**
1. Start Backend (Express) server
2. Start AI Services server
3. Start Frontend
4. Register as invigilator
5. Create exam and session
6. Enroll student with face
7. Upload test video
8. Verify processing completes
9. Download and review processed video
10. Verify video analysis record created

**Test Video:** Use a short video (10-30 seconds) with clear person and phone detections

---

### Face Enrollment Test

**Purpose:** Test multi-pose face enrollment

**Steps:**
1. Start AI Services server
2. Use Postman or frontend to create student
3. Upload front-facing photo
4. Upload left pose photo
5. Upload right pose photo
6. Upload up pose photo
7. Download up pose photo
8. Verify all poses registered
9. Verify embeddings generated

---

## Test Data

### Sample Images

Place sample images in appropriate directories for testing:
- Face images for enrollment: Any directory
- Test videos: Any directory

### Sample Video Requirements

For video processing tests:
- Format: MP4, AVI, or MOV
- Duration: 10-30 seconds
- Content: At least one person, optionally with phone
- Resolution: 720p or higher recommended
- File size: Under 100MB for faster testing

## Writing New Tests

### AI Services Test Template

```python
import pytest
from app.services.ai.detectors.phone.service import PhoneDetectionService
from app.services.ai.detectors.phone.config import PhoneDetectionConfig

@pytest.fixture
def phone_config():
    return PhoneDetectionConfig(
        enabled=True,
        confidence=0.10,
        temporal_confirm_frames=3,
    )

@pytest.fixture
def phone_service(phone_config):
    service = PhoneDetectionService(phone_config)
    service.initialize()
    return service

def test_phone_detection(phone_service):
    # Arrange
    # Set up test data
    
    # Act
    # Call method being tested
    
    # Assert
    # Verify expected results
    assert result is not None
```

### Backend Test Template (Future)

```javascript
const request = require('supertest');
const app = require('../src/app');

describe('User API', () => {
    describe('POST /api/users/register', () => {
        it('should register a new user', async () => {
            const response = await request(app)
                .post('/api/users/register')
                .send({
                    fullName: 'Test User',
                    email: 'test@example.com',
                    password: 'password123',
                    phoneNumber: '1234567890',
                    role: 'invigilator'
                });
            
            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
        });
    });
});
```

### Frontend Test Template (Future)

```javascript
import { render, screen } from '@testing-library/react';
import Login from '../Pages/Auth/Login';

describe('Login Component', () => {
    it('renders login form', () => {
        render(<Login />);
        expect(screen.getByLabelText('Email')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });
    
    it('submits login form', async () => {
        render(<Login />);
        // Test form submission
    });
});
```

## Test Environment Configuration

### AI Services Test Environment

Create a `.env.test` file for testing:

```env
APP_ENV=testing
APP_DEBUG=True
MONGO_URI=mongodb://localhost:27017/neuroproctor_test
# ... other test-specific settings
```

### Test Database

Use a separate test database to avoid polluting development data:

```env
MONGO_URI=mongodb://localhost:27017/neuroproctor_test
```

## Continuous Integration

### Recommended CI Setup

**GitHub Actions Example:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-ai-services:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd "AI SERVICES"
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd "AI SERVICES"
          pytest tests/ -v --cov=app
  
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd "Backend(Express)"
          npm install
      - name: Run tests
        run: |
          cd "Backend(Express)"
          npm test
  
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd Frontend
          npm install
      - name: Run tests
        run: |
          cd Frontend
          npm test
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with pdb debugger
pytest tests/test_phone_detection.py --pdb

# Run with verbose output
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l
```

### Common Test Issues

**Issue:** MongoDB connection failed

**Solution:** Ensure MongoDB is running and test URI is correct

**Issue:** Model files not found

**Solution:** Ensure AI models are downloaded and in correct directory

**Issue:** GPU not available

**Solution:** Set `YOLO_DEVICE=cpu` in test environment

## Test Coverage Goals

### Current Coverage

- **AI Services:** ~70% (AI pipeline components)
- **Backend:** 0% (no tests)
- **Frontend:** 0% (no tests)

### Target Coverage

- **AI Services:** 80%+ (critical AI components)
- **Backend:** 70%+ (API endpoints and business logic)
- **Frontend:** 60%+ (components and user flows)

### Priority Areas

1. **Phone Detection** - Critical for cheating detection
2. **Head Pose Estimation** - Critical for behavior analysis
3. **Authentication** - Critical for security
4. **Video Processing** - Critical for core functionality
5. **API Endpoints** - Critical for system reliability

## Related Documentation

- [05 - Current Implementation Status](05%20-%20Current%20Implementation%20Status.md) - Implementation status
- [06 - Setup and Running Guide](06%20-%20Setup%20and%20Running%20Guide.md) - Setup instructions
- [13 - Known Issues and Technical Debt](13%20-%20Known%20Issues%20and%20Technical%20Debt.md) - Known issues

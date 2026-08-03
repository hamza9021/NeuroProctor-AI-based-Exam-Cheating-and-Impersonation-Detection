---
title: Known Issues and Technical Debt
project: NeuroProctor
type: issues
status: active
tags:
  - neuroproctor
  - issues
  - technical-debt
last_reviewed: 2026-08-03
---

# Known Issues and Technical Debt

This document tracks known issues and technical debt in the NeuroProctor system.

## Recently Fixed Issues

### Phone Association with Overlapping Persons

**Status:** Fixed

**Description:** Phone detection was incorrectly associating phones with the wrong person when person bounding boxes overlapped.

**Root Cause:** Association logic relied solely on geometric metrics (IoU, center distance) without considering pose keypoints.

**Solution:** Implemented wrist-based priority scoring using COCO keypoints from pose estimation. Association evidence priority:
1. Wrist distance (highest priority)
2. ROI source track ID match
3. Phone center inside bounding box
4. Phone area overlap
5. Normalized distance to person center
6. Expanded bounding box fallback

**Files Modified:**
- `AI SERVICES/app/services/ai/analyzers/phone/associator.py`
- `AI SERVICES/app/services/ai/detectors/phone/service.py`

**Test Coverage:** Updated tests in `test_phone_detection.py`

---

### Track ID 0 Rendering Bug

**Status:** Fixed

**Description:** Phones belonging to Person #0 (Track ID 0) were rendered as "Student Unknown" instead of "Student 0".

**Root Cause:** Boolean check `if student_track_id:` evaluated to false for `student_track_id = 0`.

**Solution:** Changed check to `if student_track_id is not None:` to correctly handle zero as a valid ID.

**Files Modified:**
- `AI SERVICES/app/services/ai/processors/video_processor.py`

**Test Coverage:** Verified with existing tests

---

## Current Known Issues

### Missing Features

#### Face Identification in Video

**Severity:** High

**Description:** The system does not perform face identification during video processing. Faces are detected and embeddings could be extracted, but there is no matching against enrolled students.

**Impact:** Cannot detect impersonation during exams.

**Required Work:**
- Integrate face detection into video pipeline
- Extract face embeddings from detected faces
- Match embeddings against student database
- Track faces across frames
- Generate impersonation alerts

**Estimated Effort:** High

---

#### Cheating Rule Engine

**Severity:** High

**Description:** No rule evaluation system exists. The system detects behaviors (phone usage, head movements) but does not evaluate them against configurable rules.

**Impact:** No automated cheating detection based on configurable criteria.

**Required Work:**
- Design rule schema (conditions, actions, thresholds)
- Implement rule evaluation engine
- Create rule management UI
- Integrate with video pipeline

**Estimated Effort:** High

---

#### Suspicion Scoring

**Severity:** High

**Description:** No scoring system exists to quantify cheating behavior per student.

**Impact:** No way to rank students by suspicion level or set alert thresholds.

**Required Work:**
- Design scoring algorithm
- Implement temporal smoothing
- Create scoring dashboard
- Integrate with rule engine

**Estimated Effort:** Medium

---

#### Report Generation

**Severity:** Medium

**Description:** No PDF or report generation exists for exam results.

**Impact:** Invigilators cannot generate formal reports with evidence.

**Required Work:**
- Choose PDF generation library
- Design report template
- Compile evidence from video
- Generate statistical summaries
- Create report download endpoint

**Estimated Effort:** Medium

---

#### Live Monitoring

**Severity:** Medium

**Description:** No real-time video streaming or live processing exists.

**Impact:** Cannot monitor exams in real-time, only post-processing.

**Required Work:**
- Implement video streaming
- Adapt pipeline for real-time processing
- Create live monitoring UI
- Implement intervention controls

**Estimated Effort:** High

---

### Technical Debt

#### CORS Configuration

**Severity:** Medium

**Description:** AI Services CORS is configured to allow all origins (`allow_origins=["*"]`).

**Impact:** Security risk in production.

**Solution:** Restrict to actual frontend origin in production.

**Files:**
- `AI SERVICES/main.py`

---

#### No Refresh Token Endpoint

**Severity:** Low

**Description:** Refresh tokens are generated and stored but not used for token renewal.

**Impact:** Users must re-login after access token expires (15 minutes).

**Solution:** Implement refresh token endpoint to allow token renewal without re-login.

---

#### No Account Lockout

**Severity:** Low

**Description:** No mechanism to lock accounts after failed login attempts.

**Impact:** Vulnerable to brute force attacks.

**Solution:** Implement account lockout after N failed attempts.

---

#### No Password Complexity Requirements

**Severity:** Low

**Description:** No password strength validation during registration.

**Impact:** Users may choose weak passwords.

**Solution:** Implement password complexity requirements.

---

#### No Two-Factor Authentication

**Severity:** Low

**Description:** No 2FA implementation for sensitive operations.

**Impact:** Increased security risk for compromised credentials.

**Solution:** Implement 2FA for admin operations.

---

#### Configuration Scattered

**Severity:** Low

**Description:** Configuration is scattered across multiple files (`.env`, config classes, hardcoded values).

**Impact:** Difficult to maintain and change configuration.

**Solution:** Centralize configuration in settings classes.

---

#### Limited Error Handling

**Severity:** Low

**Description:** Some areas have limited error handling and generic error messages.

**Impact:** Difficult to debug issues in production.

**Solution:** Improve error handling with specific error types and messages.

---

#### No Automated Tests for Backend and Frontend

**Severity:** Medium

**Description:** Backend (Express) and Frontend have no automated tests.

**Impact:** Risk of regressions when making changes.

**Solution:** Add test suites for both Backend and Frontend.

---

### Code Quality Issues

#### Incomplete Integration Between AI Stages

**Severity:** Medium

**Description:** Some AI stages (pose, head pose) are not fully integrated with each other.

**Impact:** Missed opportunities for combined analysis (e.g., using head pose with phone detection).

**Solution:** Improve data sharing between stages via FrameContext.

---

#### Some Test Files May Be Outdated

**Severity:** Low

**Description:** Some test files may not reflect recent changes to the codebase.

**Impact:** Tests may pass but not actually test current functionality.

**Solution:** Review and update all test files to match current implementation.

---

#### Limited Documentation in Code

**Severity:** Low

**Description:** Some modules lack comprehensive docstrings and comments.

**Impact:** Difficult for new developers to understand code.

**Solution:** Add comprehensive docstrings and inline comments.

---

## Performance Issues

### GPU Memory Constraints

**Severity:** Medium

**Description:** Phone detection may fail on systems with limited GPU memory, requiring fallback to smaller image sizes.

**Impact:** Reduced detection accuracy on low-memory systems.

**Current Mitigation:** Fallback image sizes configured in `.env`

**Solution:** Implement dynamic memory management and automatic fallback.

---

### Video Processing Speed

**Severity:** Medium

**Description:** Video processing can be slow for long videos due to sequential frame processing.

**Impact:** Long wait times for invigilators.

**Current Mitigation:** Real-time progress updates via Socket.IO

**Solution:** Implement parallel frame processing or GPU optimization.

---

## Security Issues

### Secrets in .env Files

**Severity:** High (for production)

**Description:** Secrets are stored in `.env` files which may be committed to version control.

**Impact:** Credential exposure if repository is compromised.

**Solution:** Use secrets manager in production, add `.env` to `.gitignore`.

---

### No Request Signing

**Severity:** Low

**Description:** API requests rely solely on JWT in cookies without additional signing.

**Impact:** Vulnerable to replay attacks if cookies are compromised.

**Solution:** Add request signing for critical operations.

---

## Data Issues

### No Data Validation on Some Endpoints

**Severity:** Low

**Description:** Some endpoints may lack comprehensive input validation.

**Impact:** Invalid data may be stored in database.

**Solution:** Add comprehensive validation using Joi (Backend) and Pydantic (AI Services).

---

### No Database Indexes for Some Queries

**Severity:** Low

**Description:** Some frequently queried fields may lack indexes.

**Impact:** Slow query performance as data grows.

**Solution:** Review query patterns and add appropriate indexes.

---

## Prioritized Fix List

### High Priority

1. **Face Identification in Video** - Core missing feature
2. **Cheating Rule Engine** - Required for automated detection
3. **Suspicion Scoring** - Required for quantifying behavior
4. **Secrets Management** - Critical for production security

### Medium Priority

5. **Report Generation** - Required for human review
6. **Live Monitoring** - Required for real-time proctoring
7. **CORS Configuration** - Security issue
8. **Automated Tests for Backend/Frontend** - Quality assurance

### Low Priority

9. **Refresh Token Endpoint** - User experience improvement
10. **Account Lockout** - Security improvement
11. **Password Complexity** - Security improvement
12. **2FA** - Security improvement
13. **Configuration Centralization** - Maintainability improvement
14. **Code Documentation** - Maintainability improvement

## Related Documentation

- [05 - Current Implementation Status](05%20-%20Current%20Implementation%20Status.md) - Implementation status
- [14 - Development Roadmap](14%20-%20Development%20Roadmap.md) - Recommended development priorities
- [11 - Security and Authentication](11%20-%20Security%20and%20Authentication.md) - Security details

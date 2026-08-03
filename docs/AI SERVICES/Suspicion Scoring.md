---
title: Suspicion Scoring
project: NeuroProctor
type: reference
service: ai-services
status: missing
tags:
  - neuroproctor
  - ai-services
  - suspicion-scoring
  - cheating-detection
last_reviewed: 2026-08-03
---

# Suspicion Scoring

This document details suspicion scoring for cheating detection in the AI Services application.

## Implementation Status

**Status:** Missing

**Description:** Suspicion scoring system is not implemented.

---

## Current Implementation

### Detection Data

**Implemented:** Yes

**Available Data:**
- Phone detections (with temporal tracking)
- Head pose angles (yaw, pitch, roll)
- Pose keypoints (17 COCO keypoints)
- Person tracks (DeepSORT)

**Current Behavior:** System collects detection data but does not calculate suspicion scores

---

## Missing Components

### Scoring Algorithm

**Status:** Missing

**Description:** Algorithm to calculate suspicion scores from detection data

**Required Features:**
- Weighted scoring for different behaviors
- Temporal aggregation
- Threshold-based classification
- Confidence weighting

---

### Score Categories

**Status:** Missing

**Description:** Categories for suspicion levels

**Potential Categories:**
- Low suspicion (0-30%)
- Medium suspicion (30-60%)
- High suspicion (60-90%)
- Very high suspicion (90-100%)

---

### Scoring Factors

**Status:** Missing

**Description:** Factors contributing to suspicion score

**Potential Factors:**
- Phone usage frequency and duration
- Head pose deviation from forward-facing
- Multiple people in frame
- Leaving frame duration
- Suspicious objects presence
- Face not visible duration

---

### Score Aggregation

**Status:** Missing

**Description:** Method to aggregate scores over time

**Potential Methods:**
- Moving average
- Exponential smoothing
- Peak detection
- Time-window aggregation

---

## Related Documentation

- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services overview
- [AI Services/Rule Engine](AI%20Services/Rule%20Engine.md) - Rule engine
- [13 - Known Issues and Technical Debt](13%20-%20Known%20Issues%20and%20Technical%20Debt.md) - Known issues

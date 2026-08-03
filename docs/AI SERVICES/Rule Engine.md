---
title: Rule Engine
project: NeuroProctor
type: reference
service: ai-services
status: missing
tags:
  - neuroproctor
  - ai-services
  - rule-engine
  - cheating-detection
last_reviewed: 2026-08-03
---

# Rule Engine

This document details the rule engine for cheating detection in the AI Services application.

## Implementation Status

**Status:** Missing

**Description:** Rule engine for defining and evaluating cheating rules is not implemented.

---

## Current Implementation

### Detection Capabilities

**Implemented:** Yes

**Components:**
- Phone detection (with temporal tracking)
- Head pose estimation (yaw, pitch, roll)
- Pose estimation (17 COCO keypoints)
- Person tracking (DeepSORT)

**Current Behavior:** System detects behaviors but does not evaluate them against configurable rules

---

## Missing Components

### Rule Definition

**Status:** Missing

**Description:** System to define cheating rules

**Required Features:**
- Rule syntax/language
- Rule editor
- Rule storage
- Rule versioning

---

### Rule Evaluation Engine

**Status:** Missing

**Description:** Engine to evaluate rules against detection data

**Required Features:**
- Real-time rule evaluation
- Rule priority handling
- Rule conflict resolution
- Performance optimization

---

### Rule Categories

**Status:** Missing

**Description:** Pre-defined rule categories for common cheating behaviors

**Potential Categories:**
- Phone usage
- Looking away (head pose)
- Multiple people in frame
- Leaving frame
- Suspicious objects (laptop, book)
- Face not visible

---

### Rule Configuration

**Status:** Missing

**Description:** Configuration for rule parameters

**Potential Parameters:**
- Thresholds (e.g., head angle limits)
- Time windows (e.g., phone usage duration)
- Confidence thresholds
- Severity levels

---

## Related Documentation

- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services overview
- [13 - Known Issues and Technical Debt](13%20-%20Known%20Issues%20and%20Technical%20Debt.md) - Known issues

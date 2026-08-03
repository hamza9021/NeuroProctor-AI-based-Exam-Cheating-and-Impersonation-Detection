---
title: Models and Schemas
project: NeuroProctor
type: reference
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - models
  - schemas
last_reviewed: 2026-08-03
---

# Models and Schemas

This document details all Mongoose models and schemas in the Backend (Express) application.

## User Model

**File:** `Backend(Express)/src/Models/user.models.js`

**Purpose:** User schema for authentication and authorization

**Used by:** User controller

**Depends on:**
- Mongoose
- bcrypt (password hashing)
- jsonwebtoken (token generation)

**Key Symbols:**
- `User` - Mongoose model
- `isPasswordMatch()` - Password verification method
- `generateAccessToken()` - Access token generation
- `generateRefreshToken()` - Refresh token generation

**Schema Fields:**
```javascript
{
  fullName: String (required),
  email: String (required, unique),
  password: String (required),
  phoneNumber: String,
  role: String (enum: ['admin', 'invigilator'], required),
  profileImage: String,
  isVerified: Boolean (default: false),
  isActive: Boolean (default: false),
  refreshToken: String,
  createdAt: Date (default: Date.now),
  updatedAt: Date (default: Date.now)
}
```

**Indexes:**
- `email` (unique)

**Runtime Role:** Stores user authentication data and provides auth methods

**Status:** Implemented

**Notes:**
- Password hashed using bcrypt (10 salt rounds)
- Tokens stored in HttpOnly cookies, not in database (refreshToken is exception)

---

## Exam Model

**File:** `Backend(Express)/src/Models/exam.models.js`

**Purpose:** Exam schema for exam management

**Used by:** Exam controller

**Depends on:** Mongoose

**Key Symbols:**
- `Exam` - Mongoose model

**Schema Fields:**
```javascript
{
  title: String (required),
  description: String,
  courseName: String,
  courseCode: String,
  duration: Number (required),
  startTime: Date (required),
  endTime: Date (required),
  status: String (enum: ['scheduled', 'ongoing', 'completed', 'cancelled'], default: 'scheduled'),
  createdBy: ObjectId (ref: 'User', required),
  createdAt: Date (default: Date.now),
  updatedAt: Date (default: Date.now)
}
```

**Indexes:**
- `createdBy` (index)
- `status` (index)

**Runtime Role:** Stores exam information and scheduling

**Status:** Implemented

**Notes:**
- Status transitions: scheduled → ongoing → completed or cancelled
- Created by references User model

---

## Exam Session Model

**File:** `Backend(Express)/src/Models/examSession.models.js`

**Purpose:** Exam session schema for specific exam instances

**Used by:** Exam session controller

**Depends on:** Mongoose

**Key Symbols:**
- `ExamSession` - Mongoose model

**Schema Fields:**
```javascript
{
  examId: ObjectId (ref: 'Exam', required),
  invigilatorId: ObjectId (ref: 'User', required),
  sessionCode: String (required, unique),
  mode: String (enum: ['offline', 'live'], default: 'offline'),
  status: String (enum: ['scheduled', 'waiting', 'processing', 'active', 'completed', 'cancelled'], default: 'scheduled'),
  verified: Boolean (default: false),
  startedAt: Date,
  endedAt: Date,
  createdAt: Date (default: Date.now),
  updatedAt: Date (default: Date.now)
}
```

**Indexes:**
- `examId` (index)
- `invigilatorId` (index)
- `sessionCode` (unique)

**Runtime Role:** Stores exam session instances with invigilator assignment

**Status:** Implemented

**Notes:**
- Links exam to invigilator
- Session code is unique identifier
- Mode indicates offline (pre-recorded) or live (real-time) processing

---

## Video Analysis Model

**File:** `Backend(Express)/src/Models/videoAnalysis.models.js`

**Purpose:** Video analysis schema for processed exam videos

**Used by:** Video analysis controller

**Depends on:** Mongoose

**Key Symbols:**
- `VideoAnalysis` - Mongoose model

**Schema Fields:**
```javascript
{
  sessionId: ObjectId (ref: 'ExamSession', required),
  examId: ObjectId (ref: 'Exam', required),
  invigilatorId: ObjectId (ref: 'User', required),
  originalVideo: String (Cloudinary URL),
  processedVideo: String (Cloudinary URL),
  status: String (enum: ['pending', 'processing', 'completed', 'failed'], default: 'pending'),
  processingTime: Number,
  uploadedAt: Date (default: Date.now),
  completedAt: Date,
  errorMessage: String,
  createdAt: Date (default: Date.now),
  updatedAt: Date (default: Date.now)
}
```

**Indexes:**
- `sessionId` (unique)
- `examId` (index)
- `invigilatorId` (index)
- `status` (index)

**Runtime Role:** Stores video processing results and metadata

**Status:** Implemented

**Notes:**
- One-to-one relationship with exam session
- Stores Cloudinary URLs for original and processed videos
- Tracks processing time and status

---

## Related Documentation

- [Backend/Backend Architecture](Backend/Backend%20Architecture.md) - Backend architecture
- [Backend/Routes and Controllers](Backend/Routes%20and%20Controllers.md) - Routes and controllers
- [Backend/Services and Repositories](Backend/Services%20and%20Repositories.md) - Services
- [Backend/Backend File Reference](Backend/Backend%20File%20Reference.md) - File reference
- [09 - Database Reference](09%20-%20Database%20Reference.md) - Database reference

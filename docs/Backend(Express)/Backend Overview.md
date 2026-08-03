---
title: Backend Overview
project: NeuroProctor
type: service
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - express
last_reviewed: 2026-08-03
---

# Backend Overview

## Technology Stack

- **Framework:** Express 5
- **Runtime:** Node.js
- **Database:** MongoDB with Mongoose
- **Authentication:** JWT (access + refresh tokens)
- **File Upload:** Multer
- **Cloud Storage:** Cloudinary
- **Validation:** Joi
- **Language:** JavaScript

## Entry Point

**File:** `Backend(Express)/src/index.js`

**Description:** Starts Express server and connects to MongoDB

```javascript
import app from './app.js';
import connectDB from './Config/db.js';

const PORT = process.env.PORT || 8080;

connectDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  })
  .catch((error) => {
    console.log("MongoDB connection failed", error);
  });
```

## App Configuration

**File:** `Backend(Express)/src/app.js`

**Description:** Configures Express middleware and routes

**Middleware:**
- CORS
- Cookie parser
- JSON body parser
- Static file serving

**Routes:**
- `/api` - API routes
- `/api/users` - User routes
- `/api/exams` - Exam routes
- `/api/examSessions` - Exam session routes
- `/api/videoAnalysis` - Video analysis routes
- `/api/admin` - Admin routes

## Directory Structure

```
src/
├── app.js                      # Express app configuration
├── index.js                    # Server entry point
├── Config/
│   └── db.js                   # MongoDB connection
├── Controllers/                # Request handlers
│   ├── exam.controller.js
│   ├── examSession.controller.js
│   ├── user.controller.js
│   └── videoAnalysis.controller.js
├── Middleware/                 # Middleware
│   ├── auth.middleware.js
│   └── index.middleware.js
├── Models/                     # Mongoose schemas
│   ├── exam.models.js
│   ├── examSession.models.js
│   ├── user.models.js
│   └── videoAnalysis.models.js
├── Options/                    # Configuration options
│   └── cookie.options.js
├── Routes/                     # Route definitions
│   ├── admin.route.js
│   ├── exam.route.js
│   ├── examSession.route.js
│   ├── index.route.js
│   ├── user.route.js
│   └── videoAnalysis.route.js
├── Services/                   # Business logic
│   └── cloudinary.service.js
├── Utils/                      # Utility functions
│   └── index.utils.js
└── Validation/                 # Request validation
    └── validateExam.middleware.js
```

## Database Connection

**File:** `Backend(Express)/src/Config/db.js`

**Description:** Connects to MongoDB using Mongoose

```javascript
import mongoose from 'mongoose';

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log("MongoDB connected successfully");
  } catch (error) {
    console.log("MongoDB connection failed", error);
    process.exit(1);
  }
};

export default connectDB;
```

## Authentication

### JWT Middleware

**File:** `Backend(Express)/src/Middleware/auth.middleware.js`

**Purpose:** Verifies JWT tokens from HttpOnly cookies

**Function:** `verifyJWT`

**Process:**
1. Extract access token from cookies
2. Verify token signature
3. Decode token payload
4. Attach user to request object

---

### JWT Utilities

**File:** `Backend(Express)/src/Utils/index.utils.js`

**Functions:**
- `generateAccessToken()` - Generate JWT access token (15 min expiry)
- `generateRefreshToken()` - Generate JWT refresh token (7 day expiry)
- `isPasswordMatch()` - Compare password with hash

**Token Payload:**
```json
{
  "_id": "user_id",
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "invigilator"
}
```

---

## Database Models

### User Model

**File:** `Backend(Express)/src/Models/user.models.js`

**Fields:**
- `fullName` - User's full name
- `email` - User's email (unique)
- `password` - Hashed password
- `phoneNumber` - Phone number
- `role` - User role (invigilator/admin)
- `profileImage` - Cloudinary URL
- `isVerified` - Verification status
- `isActive` - Active status
- `refreshToken` - Refresh token
- `createdAt` - Creation timestamp
- `updatedAt` - Update timestamp

**Methods:**
- `isPasswordMatch(password)` - Compare password
- `generateAccessToken()` - Generate access token
- `generateRefreshToken()` - Generate refresh token

---

### Exam Model

**File:** `Backend(Express)/src/Models/exam.models.js`

**Fields:**
- `title` - Exam title
- `description` - Exam description
- `courseName` - Course name
- `courseCode` - Course code
- `duration` - Duration in minutes
- `startTime` - Start time
- `endTime` - End time
- `status` - Exam status
- `createdBy` - Creator user ID
- `createdAt` - Creation timestamp
- `updatedAt` - Update timestamp

---

### Exam Session Model

**File:** `Backend(Express)/src/Models/examSession.models.js`

**Fields:**
- `examId` - Reference to Exam
- `invigilatorId` - Reference to User
- `sessionCode` - Unique session code
- `mode` - Session mode (offline/live)
- `status` - Session status
- `verified` - Verification status
- `startedAt` - Start time
- `endedAt` - End time
- `createdAt` - Creation timestamp
- `updatedAt` - Update timestamp

---

### Video Analysis Model

**File:** `Backend(Express)/src/Models/videoAnalysis.models.js`

**Fields:**
- `sessionId` - Reference to ExamSession
- `examId` - Reference to Exam
- `invigilatorId` - Reference to User
- `originalVideo` - Cloudinary URL
- `processedVideo` - Cloudinary URL
- `status` - Analysis status
- `processingTime` - Processing time
- `uploadedAt` - Upload timestamp
- `completedAt` - Completion timestamp
- `errorMessage` - Error message
- `createdAt` - Creation timestamp
- `updatedAt` - Update timestamp

---

## Controllers

### User Controller

**File:** `Backend(Express)/src/Controllers/user.controller.js`

**Methods:**
- `registerUser` - Register new user
- `loginUser` - Login user
- `logoutUser` - Logout user
- `getUser` - Get current user

---

### Exam Controller

**File:** `Backend(Express)/src/Controllers/exam.controller.js`

**Methods:**
- `createExam` - Create new exam
- `getExams` - List exams with pagination
- `getExamById` - Get exam by ID
- `updateExam` - Update exam
- `deleteExam` - Delete exam
- `cancelExam` - Cancel exam

---

### Exam Session Controller

**File:** `Backend(Express)/src/Controllers/examSession.controller.js`

**Methods:**
- `createExamSession` - Create session
- `getExamSessions` - List sessions
- `getExamSessionById` - Get session by ID
- `getInvigilatorSessions` - Get invigilator's sessions
- `updateExamSession` - Update session
- `deleteExamSession` - Delete session

---

### Video Analysis Controller

**File:** `Backend(Express)/src/Controllers/videoAnalysis.controller.js`

**Methods:**
- `createVideoAnalysis` - Create video analysis record
- `getVideoAnalysisBySession` - Get analysis by session
- `getVideoAnalysesByInvigilator` - Get invigilator's analyses
- `updateVideoAnalysis` - Update analysis
- `deleteVideoAnalysis` - Delete analysis

---

## Routes

### User Routes

**File:** `Backend(Express)/src/Routes/user.route.js`

**Endpoints:**
- `POST /api/users/register` - Register user
- `POST /api/users/login` - Login user
- `POST /api/users/logout` - Logout user
- `GET /api/users/` - Get current user

---

### Exam Routes

**File:** `Backend(Express)/src/Routes/exam.route.js`

**Endpoints:**
- `POST /api/exams/create` - Create exam
- `GET /api/exams` - List exams
- `GET /api/exams/:id` - Get exam by ID
- `PUT /api/exams/update/:id` - Update exam
- `DELETE /api/exams/delete/:id` - Delete exam

---

### Exam Session Routes

**File:** `Backend(Express)/src/Routes/examSession.route.js`

**Endpoints:**
- `POST /api/examSessions/create` - Create session
- `GET /api/examSessions/` - List sessions
- `GET /api/examSessions/:id` - Get session by ID
- `GET /api/examSessions/invigilator/:id` - Get invigilator's sessions
- `PUT /api/examSessions/update/:id` - Update session
- `DELETE /api/examSessions/delete/:id` - Delete session

---

### Video Analysis Routes

**File:** `Backend(Express)/src/Routes/videoAnalysis.route.js`

**Endpoints:**
- `POST /api/videoAnalysis` - Create video analysis
- `GET /api/videoAnalysis/session/:sessionId` - Get by session
- `GET /api/videoAnalysis/invigilator` - Get invigilator's analyses
- `PUT /api/videoAnalysis/:id` - Update analysis
- `DELETE /api/videoAnalysis/:id` - Delete analysis

---

## Services

### Cloudinary Service

**File:** `Backend(Express)/src/Services/cloudinary.service.js`

**Purpose:** Handles Cloudinary operations

**Methods:**
- `uploadImage(file)` - Upload image to Cloudinary
- `deleteImage(publicId)` - Delete image from Cloudinary

---

## Middleware

### Auth Middleware

**File:** `Backend(Express)/src/Middleware/auth.middleware.js`

**Middleware:**
- `verifyJWT` - Verify JWT token

---

### Index Middleware

**File:** `Backend(Express)/src/Middleware/index.middleware.js`

**Middleware:**
- Error handler
- 404 handler

---

## Validation

### Exam Validation

**File:** `Backend(Express)/src/Validation/validateExam.middleware.js`

**Purpose:** Validates exam creation/update requests

**Schema:** Joi validation schema

---

## Configuration

### Environment Variables

**File:** `Backend(Express)/.env`

```env
PORT=8080
MONGODB_URI=mongodb://localhost:27017/neuroproctor
ACCESS_TOKEN_SECRET=your-secret-key
REFRESH_TOKEN_SECRET=your-refresh-secret
ACCESS_TOKEN_EXPIRY=15m
REFRESH_TOKEN_EXPIRY=7d
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

### Cookie Options

**File:** `Backend(Express)/src/Options/cookie.options.js`

```javascript
export const cookieOptions = {
    httpOnly: true,
    secure: false, // Set to true in production with HTTPS
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
};
```

---

## Error Handling

**Custom Error Class:** `ApiError`

**File:** `Backend(Express)/src/Utils/index.utils.js`

**Usage:**
```javascript
throw new ApiError(401, "Unauthorized");
throw new ApiError(404, "Resource not found");
```

**Response Format:**
```json
{
  "success": false,
  "message": "Error message",
  "errors": []
}
```

---

## Development

### Start Development Server

```bash
cd "Backend(Express)"
npm run dev
```

**URL:** http://localhost:8080

### Start Production Server

```bash
npm start
```

---

## Dependencies

**File:** `Backend(Express)/package.json`

**Key Dependencies:**
- `express` - Web framework
- `mongoose` - MongoDB ODM
- `jsonwebtoken` - JWT authentication
- `bcrypt` - Password hashing
- `multer` - File uploads
- `cloudinary` - Cloud storage
- `joi` - Validation
- `cookie-parser` - Cookie parsing
- `cors` - CORS support

---

## Related Documentation

- [00 - Project Home](00%20-%20Project%20Home.md) - Project overview
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System architecture
- [Frontend/Frontend Overview](Frontend/Frontend%20Overview.md) - Frontend documentation
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services documentation
- [08 - API Reference](08%20-%20API%20Reference.md) - API endpoints
- [09 - Database Reference](09%20-%20Database%20Reference.md) - Database models

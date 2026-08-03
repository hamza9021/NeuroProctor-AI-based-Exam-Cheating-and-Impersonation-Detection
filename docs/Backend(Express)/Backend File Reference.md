---
title: Backend File Reference
project: NeuroProctor
type: reference
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - file-reference
last_reviewed: 2026-08-03
---

# Backend File Reference

This document provides detailed information about every relevant Backend (Express) source file.

## Entry Points

### `src/index.js`

**Purpose:** Server entry point, starts Express server and connects to MongoDB

**Used by:** Node.js runtime

**Depends on:**
- Express app
- MongoDB connection

**Key Symbols:**
- `connectDB()` - Database connection function
- `app.listen()` - Start server

**Runtime Role:** Bootstraps the Express server

**Status:** Implemented

**Notes:** Connects to MongoDB before starting server

---

### `src/app.js`

**Purpose:** Express application configuration and middleware setup

**Used by:** index.js

**Depends on:**
- Express
- CORS
- cookie-parser
- Routes

**Key Symbols:**
- `app` - Express application instance

**Runtime Role:** Configures middleware and mounts routes

**Status:** Implemented

**Notes:** Sets up CORS, cookie parsing, JSON parsing, and static file serving

---

## Configuration

### `src/Config/db.js`

**Purpose:** MongoDB connection configuration

**Used by:** index.js

**Depends on:**
- Mongoose
- Environment variables

**Key Symbols:**
- `connectDB()` - Database connection function

**Runtime Role:** Establishes MongoDB connection

**Status:** Implemented

**Notes:** Exits process on connection failure

---

## Middleware

### `src/Middleware/auth.middleware.js`

**Purpose:** JWT verification middleware

**Used by:** All protected routes

**Depends on:**
- JWT utilities
- User model

**Key Symbols:**
- `verifyJWT` - JWT verification function

**Runtime Role:** Verifies JWT tokens from HttpOnly cookies

**Status:** Implemented

**Notes:** Attaches decoded user to req.user

---

### `src/Middleware/index.middleware.js`

**Purpose:** Global error handler and 404 handler

**Used by:** app.js

**Depends on:**
- ApiError
- ApiResponse

**Key Symbols:**
- Error handler middleware
- 404 handler

**Runtime Role:** Catches and formats all errors

**Status:** Implemented

---

### `src/Middleware/multer.middleware.js`

**Purpose:** Multer configuration for file uploads

**Used by:** User routes

**Depends on:**
- Multer

**Key Symbols:**
- `upload` - Multer instance

**Runtime Role:** Handles multipart/form-data file uploads

**Status:** Implemented

**Notes:** Configured for profile image uploads

---

### `src/Middleware/validateExam.middleware.js`

**Purpose:** Exam request validation using Joi

**Used by:** Exam routes

**Depends on:**
- Joi
- Exam validation schema

**Key Symbols:**
- `validateExam` - Validation middleware

**Runtime Role:** Validates exam creation/update requests

**Status:** Implemented

---

### `src/Middleware/validateUser.middleware.js`

**Purpose:** User request validation using Joi

**Used by:** User routes

**Depends on:**
- Joi
- User validation schemas

**Key Symbols:**
- `validateRegister` - Registration validation
- `validateLogin` - Login validation

**Runtime Role:** Validates user registration/login requests

**Status:** Implemented

---

## Models

### `src/Models/user.models.js`

**Purpose:** User schema with authentication methods

**Used by:** User controller

**Depends on:**
- Mongoose
- bcrypt
- jsonwebtoken

**Key Symbols:**
- `User` - Mongoose model
- `isPasswordMatch()` - Password verification
- `generateAccessToken()` - Access token generation
- `generateRefreshToken()` - Refresh token generation

**Runtime Role:** Stores user data and provides auth methods

**Status:** Implemented

**Notes:** Password hashed using bcrypt (10 salt rounds)

---

### `src/Models/exam.models.js`

**Purpose:** Exam schema for exam management

**Used by:** Exam controller

**Depends on:**
- Mongoose

**Key Symbols:**
- `Exam` - Mongoose model

**Runtime Role:** Stores exam information

**Status:** Implemented

---

### `src/Models/examSession.models.js`

**Purpose:** Exam session schema for session management

**Used by:** Exam session controller

**Depends on:**
- Mongoose

**Key Symbols:**
- `ExamSession` - Mongoose model

**Runtime Role:** Stores exam session instances

**Status:** Implemented

---

### `src/Models/videoAnalysis.models.js`

**Purpose:** Video analysis schema for processed videos

**Used by:** Video analysis controller

**Depends on:**
- Mongoose

**Key Symbols:**
- `VideoAnalysis` - Mongoose model

**Runtime Role:** Stores video processing results

**Status:** Implemented

---

## Controllers

### `src/Controllers/user.controller.js`

**Purpose:** User authentication and management

**Used by:** User routes

**Depends on:**
- User model
- Cloudinary service
- JWT utilities

**Key Symbols:**
- `registerUser()` - Register user
- `loginUser()` - Login user
- `logoutUser()` - Logout user
- `getUser()` - Get current user

**Runtime Role:** Handles user authentication operations

**Status:** Implemented

**Notes:** Uploads profile image to Cloudinary

---

### `src/Controllers/exam.controller.js`

**Purpose:** Exam CRUD operations

**Used by:** Exam routes

**Depends on:**
- Exam model

**Key Symbols:**
- `createExam()` - Create exam
- `getExams()` - List exams
- `getExamById()` - Get exam by ID
- `updateExam()` - Update exam
- `deleteExam()` - Delete exam
- `cancelExam()` - Cancel exam

**Runtime Role:** Handles exam management

**Status:** Implemented

**Notes:** Includes role checks for authorization

---

### `src/Controllers/examSession.controller.js`

**Purpose:** Exam session CRUD operations

**Used by:** Exam session routes

**Depends on:**
- ExamSession model

**Key Symbols:**
- `createExamSession()` - Create session
- `getExamSessions()` - List sessions
- `getExamSessionById()` - Get session by ID
- `getInvigilatorSessions()` - Get invigilator's sessions
- `updateExamSession()` - Update session
- `deleteExamSession()` - Delete session

**Runtime Role:** Handles session management

**Status:** Implemented

---

### `src/Controllers/videoAnalysis.controller.js`

**Purpose:** Video analysis CRUD operations

**Used by:** Video analysis routes

**Depends on:**
- VideoAnalysis model

**Key Symbols:**
- `createVideoAnalysis()` - Create analysis
- `getVideoAnalysisBySession()` - Get by session
- `getVideoAnalysesByInvigilator()` - Get invigilator's analyses
- `updateVideoAnalysis()` - Update analysis
- `deleteVideoAnalysis()` - Delete analysis

**Runtime Role:** Handles video analysis management

**Status:** Implemented

**Notes:** Called by AI Services after video processing

---

### `src/Controllers/admin.controller.js`

**Purpose:** Admin-specific operations

**Used by:** Admin routes

**Depends on:**
- User model

**Key Symbols:**
- Admin user management functions

**Runtime Role:** Handles admin operations

**Status:** Implemented

---

## Routes

### `src/Routes/index.route.js`

**Purpose:** Route aggregator

**Used by:** app.js

**Depends on:** All route files

**Key Symbols:** Route exports

**Runtime Role:** Centralizes all route definitions

**Status:** Implemented

---

### `src/Routes/user.route.js`

**Purpose:** User authentication routes

**Used by:** index.route.js

**Depends on:**
- User controller
- Auth middleware
- Multer middleware
- Validation middleware

**Key Symbols:**
- User route definitions

**Runtime Role:** Defines user API endpoints

**Status:** Implemented

---

### `src/Routes/exam.route.js`

**Purpose:** Exam management routes

**Used by:** index.route.js

**Depends on:**
- Exam controller
- Auth middleware
- Validation middleware

**Key Symbols:**
- Exam route definitions

**Runtime Role:** Defines exam API endpoints

**Status:** Implemented

---

### `src/Routes/examSession.route.js`

**Purpose:** Exam session management routes

**Used by:** index.route.js

**Depends on:**
- Exam session controller
- Auth middleware
- Validation middleware

**Key Symbols:**
- Exam session route definitions

**Runtime Role:** Defines session API endpoints

**Status:** Implemented

---

### `src/Routes/videoAnalysis.route.js`

**Purpose:** Video analysis routes

**Used by:** index.route.js

**Depends on:**
- Video analysis controller
- Auth middleware

**Key Symbols:**
- Video analysis route definitions

**Runtime Role:** Defines video analysis API endpoints

**Status:** Implemented

---

### `src/Routes/admin.route.js`

**Purpose:** Admin-specific routes

**Used by:** index.route.js

**Depends on:**
- Admin controller
- Auth middleware

**Key Symbols:**
- Admin route definitions

**Runtime Role:** Defines admin API endpoints

**Status:** Implemented

---

## Services

### `src/Services/cloudinary.service.js`

**Purpose:** Cloudinary integration

**Used by:** User controller

**Depends on:**
- cloudinary npm package

**Key Symbols:**
- `uploadImage()` - Upload image
- `deleteImage()` - Delete image

**Runtime Role:** Handles Cloudinary operations

**Status:** Implemented

**Notes:** Used for profile image storage

---

## Utilities

### `src/Utils/index.utils.js`

**Purpose:** Utility functions aggregator

**Used by:** Controllers

**Depends on:** All utility files

**Key Symbols:** Utility exports

**Runtime Role:** Centralizes utility functions

**Status:** Implemented

---

### `src/Utils/apiError.utils.js`

**Purpose:** Custom error class

**Used by:** Controllers

**Depends on:** None

**Key Symbols:**
- `ApiError` - Custom error class

**Runtime Role:** Provides standardized error handling

**Status:** Implemented

---

### `src/Utils/apiResponse.utils.js`

**Purpose:** Standardized API response format

**Used by:** Controllers

**Depends on:** None

**Key Symbols:**
- `ApiResponse` - Response class

**Runtime Role:** Provides consistent response format

**Status:** Implemented

---

### `src/Utils/asyncWrap.utils.js`

**Purpose:** Async error wrapper

**Used by:** Controllers

**Depends on:** None

**Key Symbols:**
- `asyncWrap()` - Error wrapper function

**Runtime Role:** Wraps async functions for error handling

**Status:** Implemented

---

### `src/Utils/generateAccessAndRefreshToken.utils.js`

**Purpose:** Token generation utilities

**Used by:** User model

**Depends on:**
- jsonwebtoken

**Key Symbols:**
- `generateAccessToken()` - Generate access token
- `generateRefreshToken()` - Generate refresh token

**Runtime Role:** Generates JWT tokens

**Status:** Implemented

---

## Options

### `src/Options/cookie.options.js`

**Purpose:** Cookie configuration

**Used by:** User controller

**Depends on:** None

**Key Symbols:**
- `cookieOptions` - Cookie configuration object

**Runtime Role:** Provides cookie settings

**Status:** Implemented

---

### `src/Options/cors.options.js`

**Purpose:** CORS configuration

**Used by:** app.js

**Depends on:** None

**Key Symbols:**
- `corsOptions` - CORS configuration object

**Runtime Role:** Provides CORS settings

**Status:** Implemented

---

## Validation

### `src/Validation/exam.validation.js`

**Purpose:** Exam validation schemas

**Used by:** validateExam middleware

**Depends on:**
- Joi

**Key Symbols:**
- Exam validation schemas

**Runtime Role:** Defines exam request validation rules

**Status:** Implemented

---

### `src/Validation/user.validation.js`

**Purpose:** User validation schemas

**Used by:** validateUser middleware

**Depends on:**
- Joi

**Key Symbols:**
- User validation schemas

**Runtime Role:** Defines user request validation rules

**Status:** Implemented

---

## Configuration

### `package.json`

**Purpose:** Project dependencies and scripts

**Used by:** npm/yarn

**Depends on:** None

**Key Symbols:** Dependencies, scripts

**Runtime Role:** Defines project configuration

**Status:** Implemented

---

### `.env`

**Purpose:** Environment variables

**Used by:** Application

**Depends on:** None

**Key Symbols:** Environment variables

**Runtime Role:** Provides configuration

**Status:** Implemented

**Notes:** Not in source control (gitignored)

---

## Related Documentation

- [Backend/Backend Architecture](Backend/Backend%20Architecture.md) - Backend architecture
- [Backend/Routes and Controllers](Backend/Routes%20and%20Controllers.md) - Routes and controllers
- [Backend/Services and Repositories](Backend/Services%20and%20Repositories.md) - Services
- [Backend/Models and Schemas](Backend/Models%20and%20Schemas.md) - Models

---
title: Backend Architecture
project: NeuroProctor
type: architecture
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - architecture
last_reviewed: 2026-08-03
---

# Backend Architecture

## Technology Stack

- **Framework:** Express 5
- **Runtime:** Node.js
- **Language:** JavaScript
- **Database:** MongoDB with Mongoose
- **Authentication:** JWT (access + refresh tokens)
- **File Upload:** Multer
- **Cloud Storage:** Cloudinary
- **Validation:** Joi
- **Cookie Parsing:** cookie-parser
- **CORS:** cors

## Architecture Overview

```mermaid
graph TB
    subgraph "Backend (Express)"
        App[Express App]
        Router[API Router]
        Middleware[Middleware Layer]
        Controllers[Controllers]
        Services[Services]
        Models[Mongoose Models]
        MongoDB[(MongoDB)]
        Cloudinary1[Cloudinary]
    end
    
    subgraph "External"
        Frontend[Frontend]
        AI Services[AI Services]
    end
    
    Frontend -->|REST + JWT Cookies| App
    App --> Router
    Router --> Middleware
    Middleware --> Controllers
    Controllers --> Services
    Services --> Models
    Services --> Cloudinary1
    Models --> MongoDB
    Controllers -->|REST| AI Services
    
    style Backend fill:#fff4e1
```

## Layer Architecture

### Application Layer

**File:** `Backend(Express)/src/app.js`

**Purpose:** Express application configuration

**Responsibilities:**
- Middleware setup (CORS, cookie-parser, JSON parser)
- Static file serving
- Route mounting
- Global error handling

---

### Routing Layer

**Location:** `Backend(Express)/src/Routes/`

**Files:**
- `index.route.js` - Route aggregator
- `user.route.js` - User routes
- `exam.route.js` - Exam routes
- `examSession.route.js` - Exam session routes
- `videoAnalysis.route.js` - Video analysis routes
- `admin.route.js` - Admin routes

**Responsibilities:**
- Define API endpoints
- Apply middleware
- Map to controllers

---

### Middleware Layer

**Location:** `Backend(Express)/src/Middleware/`

**Files:**
- `auth.middleware.js` - JWT verification
- `index.middleware.js` - Error handling

**Responsibilities:**
- Request validation
- Authentication
- Authorization
- Error handling

---

### Controller Layer

**Location:** `Backend(Express)/src/Controllers/`

**Files:**
- `user.controller.js` - User operations
- `exam.controller.js` - Exam operations
- `examSession.controller.js` - Exam session operations
- `videoAnalysis.controller.js` - Video analysis operations

**Responsibilities:**
- Request handling
- Business logic orchestration
- Response formatting
- Error handling

---

### Service Layer

**Location:** `Backend(Express)/src/Services/`

**Files:**
- `cloudinary.service.js` - Cloudinary operations

**Responsibilities:**
- External service integration
- Business logic
- Data transformation

---

### Model Layer

**Location:** `Backend(Express)/src/Models/`

**Files:**
- `user.models.js` - User schema
- `exam.models.js` - Exam schema
- `examSession.models.js` - Exam session schema
- `videoAnalysis.models.js` - Video analysis schema

**Responsibilities:**
- Data schema definition
- Validation
- Instance methods
- Static methods

---

### Database Layer

**File:** `Backend(Express)/src/Config/db.js`

**Purpose:** MongoDB connection

**Responsibilities:**
- Database connection
- Connection error handling

---

## Request Flow

### Typical Request Flow

```
Frontend Request
→ Express App (app.js)
→ Route (Routes/*.route.js)
→ Middleware (Middleware/auth.middleware.js)
→ Controller (Controllers/*.controller.js)
→ Service (Services/*.js)
→ Model (Models/*.js)
→ MongoDB
→ Response
```

### Authentication Flow

```
Frontend Request with HttpOnly Cookie
→ Express App
→ Route
→ verifyJWT Middleware
→ Extract token from cookie
→ Verify token signature
→ Decode payload
→ Attach user to req.user
→ Controller
→ Response
```

---

## Middleware Stack

### Global Middleware

1. **CORS** - Cross-origin resource sharing
2. **cookie-parser** - Parse cookies
3. **express.json()** - Parse JSON bodies
4. **express.static()** - Serve static files

### Route-Specific Middleware

1. **verifyJWT** - Verify JWT token
2. **multer** - Handle file uploads
3. **Validation middleware** - Validate request data

---

## Security Architecture

### Authentication

**Mechanism:** JWT (JSON Web Tokens)

**Token Types:**
- Access Token (15 min expiry)
- Refresh Token (7 day expiry)

**Storage:** HttpOnly cookies

**Verification:** `verifyJWT` middleware

---

### Authorization

**Mechanism:** Role-based access control

**Roles:**
- `admin` - Full system access
- `invigilator` - Exam and session management

**Implementation:** Role checks in controllers

---

### Password Security

**Hashing:** bcrypt (10 salt rounds)

**Storage:** Hashed password in database

**Verification:** bcrypt.compare()

---

### CORS Configuration

**Origin:** Configured via environment variable

**Credentials:** Enabled (for HttpOnly cookies)

**Methods:** GET, POST, PUT, DELETE

---

## Data Architecture

### Database

**Type:** MongoDB

**ODM:** Mongoose

**Connection String:** `mongodb://localhost:27017/neuroproctor`

**Collections:**
- users
- exams
- examSessions
- videoAnalysis

---

### Cloud Storage

**Provider:** Cloudinary

**Usage:**
- Profile images
- Original videos
- Processed videos

**Folders:**
- `neuroproctor/students` - Student images
- `videos/original` - Original videos
- `videos/processed` - Processed videos

---

## Error Handling

### Global Error Handler

**File:** `Backend(Express)/src/Middleware/index.middleware.js`

**Purpose:** Catch and format all errors

**Response Format:**
```json
{
  "success": false,
  "message": "Error message",
  "errors": []
}
```

### Custom Error Class

**File:** `Backend(Express)/src/Utils/index.utils.js`

**Class:** `ApiError`

**Usage:**
```javascript
throw new ApiError(401, "Unauthorized");
```

---

## Related Documentation

- [Backend/Backend Overview](Backend/Backend%20Overview.md) - Backend overview
- [Backend/Routes and Controllers](Backend/Routes%20and%20Controllers.md) - Routes and controllers
- [Backend/Services and Repositories](Backend/Services%20and%20Repositories.md) - Services
- [Backend/Models and Schemas](Backend/Models%20and%20Schemas.md) - Models
- [Backend/Authentication and Authorization](Backend/Authentication%20and%20Authorization.md) - Authentication
- [Backend/Backend File Reference](Backend/Backend%20File%20Reference.md) - File reference

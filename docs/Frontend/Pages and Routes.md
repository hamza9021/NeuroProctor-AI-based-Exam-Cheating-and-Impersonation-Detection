---
title: Pages and Routes
project: NeuroProctor
type: reference
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - pages
  - routes
last_reviewed: 2026-08-03
---

# Pages and Routes

This document details all pages, routes, and their purposes in the Frontend application.

## Route Configuration

**File:** `Frontend/src/App.jsx`

## Public Routes

### `/` - Homepage

**Component:** `Frontend/src/Pages/Homepage.jsx`

**Role:** Public

**Purpose:** Landing page with project overview

**Components Used:**
- Navbar
- Hero section
- Features section

**API Requests:** None

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Homepage.jsx`

---

### `/login` - Login

**Component:** `Frontend/src/Pages/Auth/Login.jsx`

**Role:** Public

**Purpose:** User authentication

**Components Used:**
- Login form
- Role selector

**API Requests:**
- `POST /api/users/login` - Login user

**State:**
- Email, password, role form state
- Loading state
- Error state

**Loading Behavior:** Shows loading spinner during API call

**Error Handling:** Displays error message on login failure

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Auth/Login.jsx`
- `Frontend/src/apis/Users/user.apis.js`

---

### `/register` - Register

**Component:** `Frontend/src/Pages/Auth/Register.jsx`

**Role:** Public

**Purpose:** User registration

**Components Used:**
- Registration form
- Profile image upload

**API Requests:**
- `POST /api/users/register` - Register user

**State:**
- Form state (fullName, email, password, phoneNumber, role)
- Profile image file state
- Loading state
- Error state

**Loading Behavior:** Shows loading spinner during API call

**Error Handling:** Displays error message on registration failure

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Auth/Register.jsx`
- `Frontend/src/apis/Users/user.apis.js`

---

### `/error` - Error Page

**Component:** `Frontend/src/Pages/Error/ErrorPage.jsx`

**Role:** Public

**Purpose:** Generic error page

**Components Used:**
- Error message display
- Back to home button

**API Requests:** None

**State:** None

**Loading Behavior:** None

**Error Handling:** N/A (is error handler)

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Error/ErrorPage.jsx`
- `Frontend/src/Pages/Error/ErrorPage.css`

---

### `/unauthorized` - Unauthorized

**Component:** `Frontend/src/Pages/Error/Unauthorized.jsx`

**Role:** Public

**Purpose:** Unauthorized access page

**Components Used:**
- Unauthorized message
- Back to login button

**API Requests:** None

**State:** None

**Loading Behavior:** None

**Error Handling:** N/A (is error handler)

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Error/Unauthorized.jsx`

---

## Protected Routes

### `/admin/dashboard` - Admin Dashboard

**Component:** `Frontend/src/Pages/Dashboard/AdminDashboard.jsx`

**Role:** Admin

**Purpose:** Admin dashboard with user management overview

**Components Used:**
- AdminsList
- InvigilatorsList
- Quick stats

**API Requests:**
- `GET /api/users/` - Get users (filtered by role)

**State:**
- Users list state
- Loading state
- Error state

**Loading Behavior:** Shows loading spinner during API calls

**Error Handling:** Displays error message on API failure

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Dashboard/AdminDashboard.jsx`
- `Frontend/src/components/Admin/AdminsList.jsx`
- `Frontend/src/components/Admin/InvigilatorsList.jsx`

---

### `/invigilator/dashboard` - Invigilator Dashboard

**Component:** `Frontend/src/Pages/Dashboard/InvigilatorDashboard.jsx`

**Role:** Invigilator

**Purpose:** Invigilator dashboard with exam overview

**Components Used:**
- ExamsList
- Quick actions

**API Requests:**
- `GET /api/exams` - Get exams

**State:**
- Exams list state
- Loading state
- Error state

**Loading Behavior:** Shows loading spinner during API calls

**Error Handling:** Displays error message on API failure

**Socket.IO Usage:** None

**Important Source Files:**
- `Frontend/src/Pages/Dashboard/InvigilatorDashboard.jsx`
- `Frontend/src/components/Exams/ExamsList.jsx`

---

### `/invigilator/sessions` - Invigilator Sessions

**Component:** `Frontend/src/Pages/Dashboard/InvigilatorSessions.jsx`

**Role:** Invigilator

**Purpose:** Session management and video upload

**Components Used:**
- ExamSessionsList
- VideoUpload
- Progress viewer

**API Requests:**
- `GET /api/examSessions/invigilator/:id` - Get sessions
- `GET /api/videoAnalysis/session/:sessionId` - Get video analysis
- `POST /api/v1/video/process` - Upload video

**State:**
- Sessions list state
- Selected session state
- Video upload progress state
- Processing progress state
- Loading state
- Error state

**Loading Behavior:** Shows loading spinner during API calls

**Error Handling:** Displays error message on API failure

**Socket.IO Usage:**
- Connects to AI Services Socket.IO
- Listens for: `pipeline_info`, `pipeline_error`, `stage_started`, `stage_completed`, `pipeline_completed`

**Important Source Files:**
- `Frontend/src/Pages/Dashboard/InvigilatorSessions.jsx`
- `Frontend/src/components/ExamSessions/ExamSessionsList.jsx`
- `Frontend/src/components/VideoUpload/VideoUpload.jsx`

---

## Component Routes

### Admin User Management

**Route:** `/admin/users` (component-based navigation)

**Components:**
- `AdminsList` - List of admin users
- `InvigilatorsList` - List of invigilators
- `AdminDetail` - Admin user details
- `InvigilatorDetail` - Invigilator details

**API Requests:**
- `GET /api/users/` - Get users
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

**Important Source Files:**
- `Frontend/src/components/Admin/AdminsList.jsx`
- `Frontend/src/components/Admin/InvigilatorsList.jsx`
- `Frontend/src/components/Admin/AdminDetail.jsx`
- `Frontend/src/components/Admin/InvigilatorDetail.jsx`

---

### Exam Management

**Route:** `/admin/exams` (component-based navigation)

**Components:**
- `AdminExams` - List of exams
- `AdminExamDetail` - Exam details
- `Exam` - Exam creation/edit form

**API Requests:**
- `GET /api/exams` - Get exams
- `GET /api/exams/:id` - Get exam by ID
- `POST /api/exams/create` - Create exam
- `PUT /api/exams/update/:id` - Update exam
- `DELETE /api/exams/delete/:id` - Delete exam

**Important Source Files:**
- `Frontend/src/components/Admin/AdminExams.jsx`
- `Frontend/src/components/Admin/AdminExamDetail.jsx`
- `Frontend/src/components/Exams/Exam.jsx`

---

### Exam Session Management

**Route:** `/admin/examSessions` (component-based navigation)

**Components:**
- `ExamSessionsList` - List of sessions
- `ExamSessionDetail` - Session details
- `ExamSessionFormModal` - Session creation/edit form

**API Requests:**
- `GET /api/examSessions/` - Get sessions
- `GET /api/examSessions/:id` - Get session by ID
- `POST /api/examSessions/create` - Create session
- `PUT /api/examSessions/update/:id` - Update session
- `DELETE /api/examSessions/delete/:id` - Delete session

**Important Source Files:**
- `Frontend/src/components/ExamSessions/ExamSessionsList.jsx`
- `Frontend/src/components/ExamSessions/ExamSessionDetail.jsx`
- `Frontend/src/components/ExamSessions/ExamSessionFormModal.jsx`

---

### Student Management

**Route:** `/invigilator/students` (component-based navigation)

**Components:**
- `StudentsList` - List of students
- `StudentDetail` - Student details with face enrollment
- `Student` - Student creation form

**API Requests:**
- `GET /api/v1/students` - Get students
- `GET /api/v1/students/:id` - Get student by ID
- `POST /api/v1/students` - Create student
- `PUT /api/v1/students/:id/face` - Update face pose
- `DELETE /api/v1/students/:id` - Delete student

**Important Source Files:**
- `Frontend/src/components/Students/StudentsList.jsx`
- `Frontend/src/components/Students/StudentDetail.jsx`
- `Frontend/src/components/Students/Student.jsx`

---

## Related Documentation

- [Frontend/Frontend Architecture](Frontend/Frontend%20Architecture.md) - Frontend architecture
- [Frontend/Components](Frontend/Components.md) - Component details
- [Frontend/State and API Integration](Frontend/State%20and%20API%20Integration.md) - State management
- [Frontend/Frontend File Reference](Frontend/Frontend%20File%20Reference.md) - File reference

---
title: Frontend File Reference
project: NeuroProctor
type: reference
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - file-reference
last_reviewed: 2026-08-03
---

# Frontend File Reference

This document provides detailed information about every relevant Frontend source file.

## Entry Points

### `src/main.jsx`

**Purpose:** Application entry point, initializes React app with providers

**Used by:** Vite build system

**Depends on:**
- React
- ReactDOM
- TanStack Query
- AuthContext
- App component

**Key Symbols:**
- `QueryClient` - TanStack Query client
- `QueryClientProvider` - Query provider
- `AuthProvider` - Auth context provider
- `App` - Main app component

**Runtime Role:** Bootstraps the React application with global providers

**Status:** Implemented

**Notes:** Sets up TanStack Query with default options (no refetch on window focus, retry once)

---

### `src/App.jsx`

**Purpose:** Main routing configuration and route guards

**Used by:** main.jsx

**Depends on:**
- React Router
- AuthContext
- ProtectedRoute components
- Page components

**Key Symbols:**
- `BrowserRouter` - Router component
- `Routes` - Route container
- `Route` - Individual route
- `ProtectedRoute` - Auth guard
- `AdminProtectedRoute` - Admin guard
- `InvigilatorProtectedRoute` - Invigilator guard

**Runtime Role:** Defines all application routes and their protection levels

**Status:** Implemented

**Notes:** Contains all route definitions with role-based access control

---

## Context

### `src/contexts/AuthContext.jsx`

**Purpose:** Authentication state management and methods

**Used by:** App.jsx, all protected components

**Depends on:**
- React
- User API module

**Key Symbols:**
- `AuthProvider` - Context provider
- `useAuth` - Custom hook
- `login()` - Login method
- `register()` - Register method
- `logout()` - Logout method
- `checkAuth()` - Auth check method

**Runtime Role:** Manages user authentication state across the application

**Status:** Implemented

**Notes:** Stores JWT tokens in HttpOnly cookies (managed by backend)

---

## Pages

### `src/Pages/Homepage.jsx`

**Purpose:** Landing page with project overview

**Used by:** App.jsx (route `/`)

**Depends on:**
- React
- Layout components

**Key Symbols:**
- `Homepage` component

**Runtime Role:** Displays landing page content

**Status:** Implemented

---

### `src/Pages/Auth/Login.jsx`

**Purpose:** User login page

**Used by:** App.jsx (route `/login`)

**Depends on:**
- React
- React Hook Form
- AuthContext
- User API module

**Key Symbols:**
- `Login` component
- `handleSubmit()` - Form submission handler

**Runtime Role:** Provides login form and authentication

**Status:** Implemented

---

### `src/Pages/Auth/Register.jsx`

**Purpose:** User registration page

**Used by:** App.jsx (route `/register`)

**Depends on:**
- React
- React Hook Form
- AuthContext
- User API module

**Key Symbols:**
- `Register` component
- `handleSubmit()` - Form submission handler

**Runtime Role:** Provides registration form with profile image upload

**Status:** Implemented

---

### `src/Pages/Dashboard/AdminDashboard.jsx`

**Purpose:** Admin dashboard with user management

**Used by:** App.jsx (route `/admin/dashboard`)

**Depends on:**
- React
- Admin components
- User API module
- TanStack Query

**Key Symbols:**
- `AdminDashboard` component

**Runtime Role:** Container for admin user management interface

**Status:** Implemented

---

### `src/Pages/Dashboard/InvigilatorDashboard.jsx`

**Purpose:** Invigilator dashboard with exam overview

**Used by:** App.jsx (route `/invigilator/dashboard`)

**Depends on:**
- React
- Exam components
- Exam API module
- TanStack Query

**Key Symbols:**
- `InvigilatorDashboard` component

**Runtime Role:** Container for invigilator exam management interface

**Status:** Implemented

---

### `src/Pages/Dashboard/InvigilatorSessions.jsx`

**Purpose:** Session management and video upload

**Used by:** App.jsx (route `/invigilator/sessions`)

**Depends on:**
- React
- ExamSession components
- VideoUpload component
- ExamSession API module
- VideoAnalysis API module
- Socket.IO Client
- TanStack Query

**Key Symbols:**
- `InvigilatorSessions` component

**Runtime Role:** Container for session management and video processing interface

**Status:** Implemented

**Notes:** Integrates Socket.IO for real-time video processing progress

---

### `src/Pages/Error/ErrorPage.jsx`

**Purpose:** Generic error page

**Used by:** App.jsx (route `/error`)

**Depends on:**
- React
- ErrorPage.css

**Key Symbols:**
- `ErrorPage` component

**Runtime Role:** Displays error message and navigation options

**Status:** Implemented

---

### `src/Pages/Error/ErrorPage.css`

**Purpose:** Styling for error page

**Used by:** ErrorPage.jsx

**Depends on:** None

**Key Symbols:** CSS styles

**Runtime Role:** Provides error page styling

**Status:** Implemented

---

### `src/Pages/Error/Unauthorized.jsx`

**Purpose:** Unauthorized access page

**Used by:** App.jsx (route `/unauthorized`)

**Depends on:**
- React

**Key Symbols:**
- `Unauthorized` component

**Runtime Role:** Displays unauthorized access message

**Status:** Implemented

---

### `src/Pages/index.js`

**Purpose:** Page component exports

**Used by:** App.jsx

**Depends on:** All page components

**Key Symbols:** Page component exports

**Runtime Role:** Central export file for page components

**Status:** Implemented

---

## API Clients

### `src/AxiosInstance/axios.express.js`

**Purpose:** Axios instance for Backend (Express) API

**Used by:** API modules (Users, Exams, ExamSessions, VideoAnalysis, Admin)

**Depends on:**
- axios

**Key Symbols:**
- `axiosExpress` - Configured axios instance

**Runtime Role:** Provides HTTP client for Express backend with cookie support

**Status:** Implemented

**Notes:** Includes response interceptor for error handling

---

### `src/AxiosInstance/axios.python.js`

**Purpose:** Axios instance for AI Services API

**Used by:** Student API module

**Depends on:**
- axios

**Key Symbols:**
- `axiosPython` - Configured axios instance

**Runtime Role:** Provides HTTP client for AI Services with cookie support

**Status:** Implemented

---

## API Modules

### `src/apis/Users/user.apis.js`

**Purpose:** User-related API calls

**Used by:** AuthContext, Login, Register

**Depends on:**
- axiosExpress

**Key Symbols:**
- `registerUser()` - Register user
- `loginUser()` - Login user
- `logoutUser()` - Logout user
- `getCurrentUser()` - Get current user

**Runtime Role:** Handles user authentication API calls

**Status:** Implemented

---

### `src/apis/Exams/exams.apis.js`

**Purpose:** Exam-related API calls

**Used by:** Exam components

**Depends on:**
- axiosExpress

**Key Symbols:**
- `getExams()` - Get exams list
- `getExamById()` - Get exam by ID
- `createExam()` - Create exam
- `updateExam()` - Update exam
- `deleteExam()` - Delete exam

**Runtime Role:** Handles exam CRUD API calls

**Status:** Implemented

---

### `src/apis/ExamSessions/examSessions.apis.js`

**Purpose:** Exam session-related API calls

**Used by:** ExamSession components

**Depends on:**
- axiosExpress

**Key Symbols:**
- `getExamSessions()` - Get sessions list
- `getExamSessionById()` - Get session by ID
- `createExamSession()` - Create session
- `updateExamSession()` - Update session
- `deleteExamSession()` - Delete session

**Runtime Role:** Handles exam session CRUD API calls

**Status:** Implemented

---

### `src/apis/Students/student.apis.js`

**Purpose:** Student-related API calls

**Used by:** Student components

**Depends on:**
- axiosPython

**Key Symbols:**
- `getStudents()` - Get students list
- `getStudentById()` - Get student by ID
- `createStudent()` - Create student
- `updateStudentFace()` - Update face pose
- `deleteStudent()` - Delete student

**Runtime Role:** Handles student CRUD API calls to AI Services

**Status:** Implemented

---

### `src/apis/VideoAnalysis/videoAnalysis.apis.js`

**Purpose:** Video analysis-related API calls

**Used by:** VideoUpload component

**Depends on:**
- axiosExpress

**Key Symbols:**
- `getVideoAnalysisBySession()` - Get analysis by session
- `getVideoAnalysesByInvigilator()` - Get invigilator's analyses
- `updateVideoAnalysis()` - Update analysis
- `deleteVideoAnalysis()` - Delete analysis

**Runtime Role:** Handles video analysis API calls

**Status:** Implemented

---

### `src/apis/Admin/admin.apis.js`

**Purpose:** Admin user management API calls

**Used by:** Admin components

**Depends on:**
- axiosExpress

**Key Symbols:**
- `getUsers()` - Get users
- `getUserById()` - Get user by ID
- `updateUser()` - Update user
- `deleteUser()` - Delete user
- `verifyUser()` - Verify user

**Runtime Role:** Handles admin user management API calls

**Status:** Implemented

---

## Components

### `src/components/ProtectedRoute.jsx`

**Purpose:** Route guard for authenticated users

**Used by:** App.jsx

**Depends on:**
- React Router
- AuthContext

**Key Symbols:**
- `ProtectedRoute` component

**Runtime Role:** Redirects unauthenticated users to login

**Status:** Implemented

---

### `src/components/AdminProtectedRoute.jsx`

**Purpose:** Route guard for admin users

**Used by:** App.jsx

**Depends on:**
- React Router
- AuthContext

**Key Symbols:**
- `AdminProtectedRoute` component

**Runtime Role:** Redirects non-admin users to unauthorized page

**Status:** Implemented

---

### `src/components/InvigilatorProtectedRoute.jsx`

**Purpose:** Route guard for invigilator users

**Used by:** App.jsx

**Depends on:**
- React Router
- AuthContext

**Key Symbols:**
- `InvigilatorProtectedRoute` component

**Runtime Role:** Redirects non-invigilator users to unauthorized page

**Status:** Implemented

---

### `src/components/Admin/Admin.jsx`

**Purpose:** Admin user management container

**Used by:** AdminDashboard

**Depends on:**
- AdminsList
- InvigilatorsList

**Key Symbols:**
- `Admin` component

**Runtime Role:** Container for admin user management

**Status:** Implemented

---

### `src/components/Admin/AdminDetail.jsx`

**Purpose:** Admin user detail view

**Used by:** AdminsList

**Depends on:**
- User API module

**Key Symbols:**
- `AdminDetail` component

**Runtime Role:** Displays admin details and edit form

**Status:** Implemented

---

### `src/components/Admin/AdminExamDetail.jsx`

**Purpose:** Exam detail view for admin

**Used by:** AdminExams

**Depends on:**
- Exam API module

**Key Symbols:**
- `AdminExamDetail` component

**Runtime Role:** Displays exam details with admin options

**Status:** Implemented

---

### `src/components/Admin/AdminExams.jsx`

**Purpose:** Exam list for admin

**Used by:** Admin

**Depends on:**
- Exam API module
- TanStack Query

**Key Symbols:**
- `AdminExams` component

**Runtime Role:** Displays exam list with admin management

**Status:** Implemented

---

### `src/components/Admin/AdminsList.jsx`

**Purpose:** List of admin users

**Used by:** Admin

**Depends on:**
- User API module
- TanStack Query

**Key Symbols:**
- `AdminsList` component

**Runtime Role:** Displays admin users with management options

**Status:** Implemented

---

### `src/components/Admin/InvigilatorDetail.jsx`

**Purpose:** Invigilator detail view

**Used by:** InvigilatorsList

**Depends on:**
- User API module

**Key Symbols:**
- `InvigilatorDetail` component

**Runtime Role:** Displays invigilator details and edit form

**Status:** Implemented

---

### `src/components/Admin/InvigilatorsList.jsx`

**Purpose:** List of invigilator users

**Used by:** Admin

**Depends on:**
- User API module
- TanStack Query

**Key Symbols:**
- `InvigilatorsList` component

**Runtime Role:** Displays invigilators with management options

**Status:** Implemented

---

### `src/components/ExamSessions/ExamSessionDetail.jsx`

**Purpose:** Exam session detail view

**Used by:** ExamSessionsList

**Depends on:**
- ExamSession API module

**Key Symbols:**
- `ExamSessionDetail` component

**Runtime Role:** Displays session details and management options

**Status:** Implemented

---

### `src/components/ExamSessions/ExamSessionFormModal.jsx`

**Purpose:** Modal for creating/editing exam sessions

**Used by:** ExamSessionsList

**Depends on:**
- ExamSession API module

**Key Symbols:**
- `ExamSessionFormModal` component

**Runtime Role:** Provides form for session creation/editing

**Status:** Implemented

---

### `src/components/ExamSessions/ExamSessionsList.jsx`

**Purpose:** List of exam sessions

**Used by:** AdminDashboard, InvigilatorDashboard

**Depends on:**
- ExamSession API module
- TanStack Query

**Key Symbols:**
- `ExamSessionsList` component

**Runtime Role:** Displays session list with management options

**Status:** Implemented

---

### `src/components/Exams/Exam.jsx`

**Purpose:** Exam creation/editing form

**Used by:** ExamsList

**Depends on:**
- Exam API module
- React Hook Form

**Key Symbols:**
- `Exam` component

**Runtime Role:** Provides exam creation/editing form

**Status:** Implemented

---

### `src/components/Exams/ExamDetail.jsx`

**Purpose:** Exam detail view

**Used by:** ExamsList

**Depends on:**
- Exam API module

**Key Symbols:**
- `ExamDetail` component

**Runtime Role:** Displays exam details and edit options

**Status:** Implemented

---

### `src/components/Exams/ExamsList.jsx`

**Purpose:** List of exams

**Used by:** InvigilatorDashboard

**Depends on:**
- Exam API module
- TanStack Query

**Key Symbols:**
- `ExamsList` component

**Runtime Role:** Displays exam list with management options

**Status:** Implemented

---

### `src/components/Students/Student.jsx`

**Purpose:** Student creation form with face enrollment

**Used by:** StudentsList

**Depends on:**
- Student API module
- React Hook Form

**Key Symbols:**
- `Student` component

**Runtime Role:** Provides student creation form with face upload

**Status:** Implemented

---

### `src/components/Students/StudentDetail.jsx`

**Purpose:** Student detail view with multi-pose enrollment

**Used by:** StudentsList

**Depends on:**
- Student API module

**Key Symbols:**
- `StudentDetail` component

**Runtime Role:** Displays student details and pose enrollment interface

**Status:** Implemented

---

### `src/components/Students/StudentsList.jsx`

**Purpose:** List of students

**Used by:** InvigilatorDashboard

**Depends on:**
- Student API module
- TanStack Query

**Key Symbols:**
- `StudentsList` component

**Runtime Role:** Displays student list with management options

**Status:** Implemented

---

### `src/components/VideoUpload/VideoUpload.jsx`

**Purpose:** Video upload interface with progress tracking

**Used by:** InvigilatorSessions

**Depends on:**
- VideoAnalysis API module
- Socket.IO Client

**Key Symbols:**
- `VideoUpload` component

**Runtime Role:** Provides video upload with real-time progress via Socket.IO

**Status:** Implemented

**Notes:** Connects to AI Services Socket.IO for progress updates

---

## Assets

### `src/Assets/Logo.png`

**Purpose:** Application logo

**Used by:** Various components

**Depends on:** None

**Key Symbols:** Image file

**Runtime Role:** Displayed in UI elements

**Status:** Implemented

---

### `src/Assets/Logo2.png`

**Purpose:** Alternative application logo

**Used by:** Various components

**Depends on:** None

**Key Symbols:** Image file

**Runtime Role:** Displayed in UI elements

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

### `vite.config.js`

**Purpose:** Vite build configuration

**Used by:** Vite

**Depends on:** None

**Key Symbols:** Vite configuration

**Runtime Role:** Configures build tool

**Status:** Implemented

---

### `tailwind.config.js`

**Purpose:** TailwindCSS configuration

**Used by:** TailwindCSS

**Depends on:** None

**Key Symbols:** Tailwind configuration

**Runtime Role:** Configures CSS framework

**Status:** Implemented

---

### `index.html`

**Purpose:** HTML entry point

**Used by:** Vite

**Depends on:** None

**Key Symbols:** HTML structure

**Runtime Role:** Mount point for React app

**Status:** Implemented

---

## Related Documentation

- [Frontend/Frontend Architecture](Frontend/Frontend%20Architecture.md) - Frontend architecture
- [Frontend/Pages and Routes](Frontend/Pages%20and%20Routes.md) - Pages and routes
- [Frontend/Components](Frontend/Components.md) - Component details
- [Frontend/State and API Integration](Frontend/State%20and%20API%20Integration.md) - State management

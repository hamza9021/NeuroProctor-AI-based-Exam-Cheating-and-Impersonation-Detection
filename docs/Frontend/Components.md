---
title: Components
project: NeuroProctor
type: reference
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - components
last_reviewed: 2026-08-03
---

# Components

This document details all React components in the Frontend application.

## Layout Components

### Navbar

**File:** `Frontend/src/components/Layout/Navbar.jsx`

**Purpose:** Navigation bar with logo and menu

**Used by:** All pages

**Depends on:**
- React Router (useNavigate)
- AuthContext (user state)

**Key Symbols:**
- `Navbar` component

**Runtime Role:** Provides navigation links and user menu

**Status:** Implemented

---

### Sidebar

**File:** `Frontend/src/components/Layout/Sidebar.jsx`

**Purpose:** Sidebar navigation for dashboards

**Used by:** Dashboard pages

**Depends on:**
- React Router (useNavigate)

**Key Symbols:**
- `Sidebar` component

**Runtime Role:** Provides sidebar navigation menu

**Status:** Implemented

---

## Route Guard Components

### ProtectedRoute

**File:** `Frontend/src/components/ProtectedRoute.jsx`

**Purpose:** Protects routes requiring authentication

**Used by:** App.jsx

**Depends on:**
- React Router (Navigate, useLocation)
- AuthContext (user state)

**Key Symbols:**
- `ProtectedRoute` component

**Runtime Role:** Redirects unauthenticated users to login

**Status:** Implemented

---

### AdminProtectedRoute

**File:** `Frontend/src/components/AdminProtectedRoute.jsx`

**Purpose:** Protects routes requiring admin role

**Used by:** App.jsx

**Depends on:**
- React Router (Navigate)
- AuthContext (user state)

**Key Symbols:**
- `AdminProtectedRoute` component

**Runtime Role:** Redirects non-admin users to unauthorized page

**Status:** Implemented

---

### InvigilatorProtectedRoute

**File:** `Frontend/src/components/InvigilatorProtectedRoute.jsx`

**Purpose:** Protects routes requiring invigilator role

**Used by:** App.jsx

**Depends on:**
- React Router (Navigate)
- AuthContext (user state)

**Key Symbols:**
- `InvigilatorProtectedRoute` component

**Runtime Role:** Redirects non-invigilator users to unauthorized page

**Status:** Implemented

---

## Admin Components

### Admin

**File:** `Frontend/src/components/Admin/Admin.jsx`

**Purpose:** Main admin component for user management

**Used by:** AdminDashboard

**Depends on:**
- AdminsList
- InvigilatorsList

**Key Symbols:**
- `Admin` component

**Runtime Role:** Container for admin user management

**Status:** Implemented

---

### AdminDetail

**File:** `Frontend/src/components/Admin/AdminDetail.jsx`

**Purpose:** Display and edit admin user details

**Used by:** AdminsList

**Depends on:**
- User API module

**Key Symbols:**
- `AdminDetail` component

**Runtime Role:** Shows admin details and edit form

**Status:** Implemented

---

### AdminExamDetail

**File:** `Frontend/src/components/Admin/AdminExamDetail.jsx`

**Purpose:** Display exam details for admin

**Used by:** AdminExams

**Depends on:**
- Exam API module

**Key Symbols:**
- `AdminExamDetail` component

**Runtime Role:** Shows exam details and edit options

**Status:** Implemented

---

### AdminExams

**File:** `Frontend/src/components/Admin/AdminExams.jsx`

**Purpose:** List and manage exams

**Used by:** AdminDashboard

**Depends on:**
- Exam API module
- TanStack Query

**Key Symbols:**
- `AdminExams` component

**Runtime Role:** Displays exam list with CRUD operations

**Status:** Implemented

---

### AdminsList

**File:** `Frontend/src/components/Admin/AdminsList.jsx`

**Purpose:** List all admin users

**Used by:** Admin

**Depends on:**
- User API module
- TanStack Query

**Key Symbols:**
- `AdminsList` component

**Runtime Role:** Displays admin users with management options

**Status:** Implemented

---

### InvigilatorDetail

**File:** `Frontend/src/components/Admin/InvigilatorDetail.jsx`

**Purpose:** Display and edit invigilator details

**Used by:** InvigilatorsList

**Depends on:**
- User API module

**Key Symbols:**
- `InvigilatorDetail` component

**Runtime Role:** Shows invigilator details and edit form

**Status:** Implemented

---

### InvigilatorsList

**File:** `Frontend/src/components/Admin/InvigilatorsList.jsx`

**Purpose:** List all invigilator users

**Used by:** Admin

**Depends on:**
- User API module
- TanStack Query

**Key Symbols:**
- `InvigilatorsList` component

**Runtime Role:** Displays invigilators with management options

**Status:** Implemented

---

## Exam Session Components

### ExamSessionDetail

**File:** `Frontend/src/components/ExamSessions/ExamSessionDetail.jsx`

**Purpose:** Display exam session details

**Used by:** ExamSessionsList

**Depends on:**
- ExamSession API module

**Key Symbols:**
- `ExamSessionDetail` component

**Runtime Role:** Shows session details and management options

**Status:** Implemented

---

### ExamSessionFormModal

**File:** `Frontend/src/components/ExamSessions/ExamSessionFormModal.jsx`

**Purpose:** Modal form for creating/editing exam sessions

**Used by:** ExamSessionsList

**Depends on:**
- ExamSession API module

**Key Symbols:**
- `ExamSessionFormModal` component

**Runtime Role:** Provides form for session creation/editing

**Status:** Implemented

---

### ExamSessionsList

**File:** `Frontend/src/components/ExamSessions/ExamSessionsList.jsx`

**Purpose:** List all exam sessions

**Used by:** AdminDashboard, InvigilatorDashboard

**Depends on:**
- ExamSession API module
- TanStack Query

**Key Symbols:**
- `ExamSessionsList` component

**Runtime Role:** Displays session list with management options

**Status:** Implemented

---

## Exam Components

### Exam

**File:** `Frontend/src/components/Exams/Exam.jsx`

**Purpose:** Form for creating/editing exams

**Used by:** ExamsList

**Depends on:**
- Exam API module
- React Hook Form

**Key Symbols:**
- `Exam` component

**Runtime Role:** Provides exam creation/editing form

**Status:** Implemented

---

### ExamDetail

**File:** `Frontend/src/components/Exams/ExamDetail.jsx`

**Purpose:** Display exam details

**Used by:** ExamsList

**Depends on:**
- Exam API module

**Key Symbols:**
- `ExamDetail` component

**Runtime Role:** Shows exam details and edit options

**Status:** Implemented

---

### ExamsList

**File:** `Frontend/src/components/Exams/ExamsList.jsx`

**Purpose:** List all exams

**Used by:** InvigilatorDashboard

**Depends on:**
- Exam API module
- TanStack Query

**Key Symbols:**
- `ExamsList` component

**Runtime Role:** Displays exam list with management options

**Status:** Implemented

---

## Student Components

### Student

**File:** `Frontend/src/components/Students/Student.jsx`

**Purpose:** Form for creating students with face enrollment

**Used by:** StudentsList

**Depends on:**
- Student API module
- React Hook Form

**Key Symbols:**
- `Student` component

**Runtime Role:** Provides student creation form with face upload

**Status:** Implemented

---

### StudentDetail

**File:** `Frontend/src/components/Students/StudentDetail.jsx`

**Purpose:** Display student details with multi-pose face enrollment

**Used by:** StudentsList

**Depends on:**
- Student API module

**Key Symbols:**
- `StudentDetail` component

**Runtime Role:** Shows student details and pose enrollment interface

**Status:** Implemented

---

### StudentsList

**File:** `Frontend/src/components/Students/StudentsList.jsx`

**Purpose:** List all students

**Used by:** InvigilatorDashboard

**Depends on:**
- Student API module
- TanStack Query

**Key Symbols:**
- `StudentsList` component

**Runtime Role:** Displays student list with management options

**Status:** Implemented

---

## Video Upload Components

### VideoUpload

**File:** `Frontend/src/components/VideoUpload/VideoUpload.jsx`

**Purpose:** Upload video for processing

**Used by:** InvigilatorSessions

**Depends on:**
- VideoAnalysis API module
- Socket.IO Client

**Key Symbols:**
- `VideoUpload` component

**Runtime Role:** Provides video upload interface with real-time progress

**Status:** Implemented

---

## UI Components

### Button

**File:** `Frontend/src/components/ui/Button.jsx`

**Purpose:** Reusable button component

**Used by:** Multiple components

**Depends on:** None

**Key Symbols:**
- `Button` component

**Runtime Role:** Provides styled button with variants

**Status:** Implemented

---

### Input

**File:** `Frontend/src/components/ui/Input.jsx`

**Purpose:** Reusable input component

**Used by:** Multiple components

**Depends on:** None

**Key Symbols:**
- `Input` component

**Runtime Role:** Provides styled input with validation

**Status:** Implemented

---

### Modal

**File:** `Frontend/src/components/ui/Modal.jsx`

**Purpose:** Reusable modal component

**Used by:** Multiple components

**Depends on:** None

**Key Symbols:**
- `Modal` component

**Runtime Role:** Provides modal dialog with backdrop

**Status:** Implemented

---

## Related Documentation

- [Frontend/Frontend Architecture](Frontend/Frontend%20Architecture.md) - Frontend architecture
- [Frontend/Pages and Routes](Frontend/Pages%20and%20Routes.md) - Pages and routes
- [Frontend/State and API Integration](Frontend/State%20and%20API%20Integration.md) - State management
- [Frontend/Frontend File Reference](Frontend/Frontend%20File%20Reference.md) - File reference

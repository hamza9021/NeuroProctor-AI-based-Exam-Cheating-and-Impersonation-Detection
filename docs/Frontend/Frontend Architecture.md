---
title: Frontend Architecture
project: NeuroProctor
type: architecture
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - architecture
last_reviewed: 2026-08-03
---

# Frontend Architecture

## Technology Stack

- **Framework:** React 19
- **Build Tool:** Vite 6
- **Language:** JavaScript (JSX)
- **Routing:** React Router 7
- **State Management:** React Context + TanStack Query
- **HTTP Client:** Axios
- **Real-Time:** Socket.IO Client
- **Styling:** TailwindCSS
- **Forms:** React Hook Form
- **Icons:** Lucide React

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[UI Components]
        Router[React Router]
        AuthContext[Auth Context]
        QueryClient[TanStack Query]
        Axios[Axios Client]
        Socket[Socket.IO Client]
    end
    
    UI --> Router
    UI --> AuthContext
    UI --> QueryClient
    QueryClient --> Axios
    UI --> Socket
    
    Router -->|Protected Routes| AuthContext
    Axios -->|JWT Cookies| Backend
    Socket -->|Socket.IO| AI Services
    
    style Frontend fill:#e1f5ff
```

## Component Architecture

### Page Components

**Location:** `Frontend/src/Pages/`

| Component | Route | Role | Purpose |
|-----------|-------|------|---------|
| `Homepage.jsx` | `/` | Public | Landing page |
| `Auth/Login.jsx` | `/login` | Public | User login |
| `Auth/Register.jsx` | `/register` | Public | User registration |
| `Dashboard/AdminDashboard.jsx` | `/admin/dashboard` | Admin | Admin dashboard |
| `Dashboard/InvigilatorDashboard.jsx` | `/invigilator/dashboard` | Invigilator | Invigilator dashboard |
| `Dashboard/InvigilatorSessions.jsx` | `/invigilator/sessions` | Invigilator | Session management |
| `Error/ErrorPage.jsx` | `/error` | Public | Error page |
| `Error/Unauthorized.jsx` | `/unauthorized` | Public | Unauthorized access |

### Feature Components

**Location:** `Frontend/src/components/`

| Directory | Components | Purpose |
|-----------|------------|---------|
| `Admin/` | Admin, AdminDetail, AdminsList, InvigilatorsList, InvigilatorDetail | User management |
| `ExamSessions/` | ExamSessionDetail, ExamSessionFormModal, ExamSessionsList | Session management |
| `Exams/` | Exam, ExamDetail, ExamsList | Exam management |
| `Layout/` | Navbar, Sidebar | Layout components |
| `Students/` | Student, StudentDetail, StudentsList | Student management |
| `VideoUpload/` | VideoUpload | Video upload interface |
| `ui/` | Button, Input, Modal | Reusable UI components |
| `AdminProtectedRoute.jsx` | - | Admin route guard |
| `InvigilatorProtectedRoute.jsx` | - | Invigilator route guard |
| `ProtectedRoute.jsx` | - | General route guard |

## State Management

### Authentication State

**File:** `Frontend/src/contexts/AuthContext.jsx`

**State:**
- `user` - Current user object
- `loading` - Loading state
- `isAuthenticated` - Auth status

**Methods:**
- `login(email, password, role)` - Login user
- `register(userData)` - Register user
- `logout()` - Logout user
- `checkAuth()` - Check authentication status

**Storage:** HttpOnly cookies for JWT tokens

### Server State

**File:** `Frontend/src/main.jsx`

**Provider:** TanStack Query (React Query)

**Purpose:** Caching and synchronization of server data

**Usage:**
```javascript
const { data, isLoading, error } = useQuery({
  queryKey: ['exams'],
  queryFn: () => getExams(),
});
```

## API Integration

### Axios Configuration

**Location:** `Frontend/src/AxiosInstance/`

**Files:**
- `axios.express.js` - Backend (Express) client
- `axios.python.js` - AI Services client

**Configuration:**
- Base URL from environment variables
- HttpOnly cookie support
- Request/response interceptors
- Error handling

### API Modules

**Location:** `Frontend/src/apis/`

| Module | Purpose |
|--------|---------|
| `Admin/admin.apis.js` | Admin operations |
| `ExamSessions/examSessions.apis.js` | Session operations |
| `Exams/exams.apis.js` | Exam operations |
| `Students/student.apis.js` | Student operations |
| `Users/user.apis.js` | User operations |
| `VideoAnalysis/videoAnalysis.apis.js` | Video analysis operations |

## Routing

**File:** `Frontend/src/App.jsx`

**Route Structure:**
- Public routes: `/`, `/login`, `/register`, `/error`, `/unauthorized`
- Protected routes: `/admin/*`, `/invigilator/*`
- Role-based routes: Admin-only, Invigilator-only

**Route Guards:**
- `ProtectedRoute` - Requires authentication
- `AdminProtectedRoute` - Requires admin role
- `InvigilatorProtectedRoute` - Requires invigilator role

## Real-Time Communication

**Socket.IO Integration**

**Usage:** Video processing progress updates

**Events Listened:**
- `pipeline_info` - General pipeline information
- `pipeline_error` - Pipeline errors
- `stage_started` - Stage started
- `stage_completed` - Stage completed
- `pipeline_completed` - Pipeline completed

**Implementation:**
```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000', {
  withCredentials: true,
  transports: ['websocket']
});
```

## Data Flow

### Authentication Flow

```
User → Login Form → AuthContext.login() → Axios POST /api/users/login
→ Backend (JWT verification) → Set HttpOnly cookies → Update AuthContext
```

### Data Fetching Flow

```
Component → useQuery() → API Module → Axios → Backend/AI Services
→ Response → TanStack Query Cache → Component Render
```

### Real-Time Flow

```
AI Services → Socket.IO Event → Frontend Socket.IO Client → Component State Update
```

## Styling

**Framework:** TailwindCSS

**Configuration:** `Frontend/tailwind.config.js`

**Usage:** Utility classes in JSX

**Theme:** Default Tailwind theme with custom colors if configured

## Related Documentation

- [Frontend/Frontend Overview](Frontend/Frontend%20Overview.md) - Frontend overview
- [Frontend/Pages and Routes](Frontend/Pages%20and%20Routes.md) - Page details
- [Frontend/Components](Frontend/Components.md) - Component details
- [Frontend/State and API Integration](Frontend/State%20and%20API%20Integration.md) - State management details
- [Frontend/Frontend File Reference](Frontend/Frontend%20File%20Reference.md) - File reference

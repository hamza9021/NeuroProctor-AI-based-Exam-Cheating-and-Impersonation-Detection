---
title: Frontend Overview
project: NeuroProctor
type: service
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - react
last_reviewed: 2026-08-03
---

# Frontend Overview

## Technology Stack

- **Framework:** React 19
- **Build Tool:** Vite
- **Routing:** React Router 7
- **State Management:** React Context + TanStack Query
- **HTTP Client:** Axios
- **Real-Time:** Socket.IO Client
- **Styling:** TailwindCSS
- **Forms:** React Hook Form
- **Language:** JavaScript (JSX)

## Entry Point

**File:** `Frontend/src/main.jsx`

**Description:** Initializes React app with QueryClient and AuthContext providers

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
```

## Main App Component

**File:** `Frontend/src/App.jsx`

**Description:** Defines routing structure and protected routes

**Routes:**
- `/` - Homepage
- `/login` - Login page
- `/register` - Register page
- `/admin/dashboard` - Admin dashboard (protected)
- `/invigilator/dashboard` - Invigilator dashboard (protected)
- `/invigilator/sessions` - Invigilator sessions (protected)
- `/admin/users` - User management (admin protected)
- `/admin/exams` - Exam management (admin protected)
- `/admin/exams/:id` - Exam details (admin protected)
- `/admin/examSessions` - Session management (admin protected)
- `/invigilator/exams` - Exam list (invigilator protected)
- `/invigilator/students` - Student management (invigilator protected)
- `/unauthorized` - Unauthorized access page
- `/error` - Error page

## Directory Structure

```
src/
├── App.jsx                      # Main routing
├── main.jsx                     # Entry point
├── index.css                    # Global styles
├── Assets/                      # Static assets
├── AxiosInstance/               # Axios configuration
├── Pages/                       # Page components
│   ├── Auth/                    # Authentication pages
│   ├── Dashboard/               # Dashboard pages
│   ├── Error/                   # Error pages
│   └── Homepage.jsx             # Homepage
├── components/                  # Reusable components
│   ├── Admin/                   # Admin components
│   ├── ExamSessions/            # Session components
│   ├── Exams/                   # Exam components
│   ├── Layout/                  # Layout components
│   ├── Students/                # Student components
│   ├── VideoUpload/             # Video upload components
│   ├── ui/                      # UI components
│   ├── AdminProtectedRoute.jsx  # Admin route guard
│   ├── InvigilatorProtectedRoute.jsx
│   └── ProtectedRoute.jsx       # Route guard
├── contexts/                    # React contexts
│   └── AuthContext.jsx          # Authentication context
├── apis/                        # API client modules
│   ├── Admin/
│   ├── ExamSessions/
│   ├── Exams/
│   ├── Health/
│   ├── Students/
│   ├── Users/
│   └── VideoAnalysis/
└── utils/                       # Utility functions
```

## Key Components

### AuthContext

**File:** `Frontend/src/contexts/AuthContext.jsx`

**Purpose:** Manages authentication state and provides auth methods

**State:**
- `user` - Current user object
- `loading` - Loading state
- `isAuthenticated` - Auth status

**Methods:**
- `login(email, password, role)` - Login user
- `register(userData)` - Register user
- `logout()` - Logout user
- `checkAuth()` - Check authentication status

---

### Protected Routes

**Files:**
- `Frontend/src/components/ProtectedRoute.jsx`
- `Frontend/src/components/AdminProtectedRoute.jsx`
- `Frontend/src/components/InvigilatorProtectedRoute.jsx`

**Purpose:** Route guards for role-based access control

---

### API Clients

**Directory:** `Frontend/src/apis/`

**Purpose:** Centralized API client modules per domain

**Modules:**
- `Admin/index.js` - Admin operations
- `ExamSessions/index.js` - Exam session operations
- `Exams/index.js` - Exam operations
- `Students/index.js` - Student operations
- `Users/index.js` - User operations
- `VideoAnalysis/index.js` - Video analysis operations

**Example:**
```javascript
import axiosInstance from '../AxiosInstance';

export const createExam = async (examData) => {
  const response = await axiosInstance.post('/api/exams/create', examData);
  return response.data;
};
```

---

## Key Pages

### Authentication Pages

**Login:** `Frontend/src/Pages/Auth/Login.jsx`
- Email/password form
- Role selection
- Calls `/api/users/login`

**Register:** `Frontend/src/Pages/Auth/Register.jsx`
- User registration form
- Profile image upload
- Calls `/api/users/register`

---

### Dashboard Pages

**Admin Dashboard:** `Frontend/src/Pages/Dashboard/AdminDashboard.jsx`
- User management
- Exam overview
- Session overview

**Invigilator Dashboard:** `Frontend/src/Pages/Dashboard/InvigilatorDashboard.jsx`
- Exam list
- Session list
- Quick actions

**Invigilator Sessions:** `Frontend/src/Pages/Dashboard/InvigilatorSessions.jsx`
- Session details
- Video upload
- Processing progress
- Download links

---

### Management Pages

**Exams:** `Frontend/src/components/Exams/`
- Exam list
- Exam creation
- Exam details
- Exam updates

**Exam Sessions:** `Frontend/src/components/ExamSessions/`
- Session list
- Session creation
- Session details

**Students:** `Frontend/src/components/Students/`
- Student list
- Student enrollment
- Face registration
- Multi-pose enrollment

**Video Upload:** `Frontend/src/components/VideoUpload/`
- Video upload form
- Progress tracking
- Socket.IO integration

---

## Socket.IO Integration

**Usage:** Real-time progress updates during video processing

**Implementation:**
```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000', {
  withCredentials: true,
  transports: ['websocket']
});

socket.on('pipeline_info', (data) => {
  console.log(data);
});

socket.on('stage_completed', (data) => {
  updateStage(data.stage);
});
```

**Events Listened:**
- `pipeline_info` - General pipeline information
- `pipeline_error` - Pipeline errors
- `stage_started` - Stage started
- `stage_completed` - Stage completed
- `pipeline_completed` - Pipeline completed

---

## State Management

### React Context
- **AuthContext** - Authentication state
- Custom contexts can be added as needed

### TanStack Query
- Used for server state management
- Caching and invalidation
- Loading and error states

**Example:**
```javascript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading, error } = useQuery({
  queryKey: ['exams'],
  queryFn: () => getExams(),
});
```

---

## Styling

**Framework:** TailwindCSS

**Configuration:** `Frontend/tailwind.config.js`

**Usage:** Utility classes in JSX

**Example:**
```javascript
<div className="bg-blue-500 text-white p-4 rounded">
  Button
</div>
```

---

## Configuration

### Environment Variables

**File:** `Frontend/.env`

```env
VITE_API_URL=http://localhost:8080
VITE_AI_API_URL=http://localhost:8000
```

### Axios Configuration

**File:** `Frontend/src/AxiosInstance/index.js`

**Features:**
- Base URL from environment
- Cookie support (withCredentials)
- Request/response interceptors
- Error handling

---

## Dependencies

**File:** `Frontend/package.json`

**Key Dependencies:**
- `react` - UI framework
- `react-router-dom` - Routing
- `@tanstack/react-query` - Server state
- `axios` - HTTP client
- `socket.io-client` - Real-time
- `tailwindcss` - Styling
- `react-hook-form` - Forms
- `lucide-react` - Icons

---

## Development

### Start Development Server

```bash
cd Frontend
npm run dev
```

**URL:** http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

---

## Related Documentation

- [00 - Project Home](00%20-%20Project%20Home.md) - Project overview
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System architecture
- [Backend/Backend Overview](Backend/Backend%20Overview.md) - Backend documentation
- [AI Services/AI Services Overview](AI%20Services/AI%20Services%20Overview.md) - AI Services documentation

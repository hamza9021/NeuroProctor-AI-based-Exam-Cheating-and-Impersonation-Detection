---
title: State and API Integration
project: NeuroProctor
type: reference
service: frontend
status: active
tags:
  - neuroproctor
  - frontend
  - state
  - api
last_reviewed: 2026-08-03
---

# State and API Integration

This document details state management and API integration in the Frontend application.

## State Management

### Authentication State

**File:** `Frontend/src/contexts/AuthContext.jsx`

**Provider:** `AuthProvider`

**State:**
```javascript
{
  user: {
    _id: string,
    email: string,
    fullName: string,
    role: 'admin' | 'invigilator',
    profileImage: string
  } | null,
  loading: boolean,
  isAuthenticated: boolean
}
```

**Methods:**
- `login(email, password, role)` - Login user
- `register(userData)` - Register user
- `logout()` - Logout user
- `checkAuth()` - Check authentication status

**Storage:** HttpOnly cookies (managed by backend)

**Usage:**
```javascript
const { user, login, logout, isAuthenticated } = useAuth();
```

---

### Server State (TanStack Query)

**File:** `Frontend/src/main.jsx`

**Provider:** `QueryClientProvider`

**Configuration:**
```javascript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

**Usage Pattern:**
```javascript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Query
const { data, isLoading, error } = useQuery({
  queryKey: ['exams'],
  queryFn: () => getExams(),
});

// Mutation
const mutation = useMutation({
  mutationFn: (examData) => createExam(examData),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['exams'] });
  },
});
```

**Cache Keys:**
- `['exams']` - Exam list
- `['examSessions']` - Session list
- `['students']` - Student list
- `['users']` - User list
- `['videoAnalysis']` - Video analysis data

---

## API Integration

### Axios Configuration

#### Express Backend Client

**File:** `Frontend/src/AxiosInstance/axios.express.js`

**Configuration:**
```javascript
import axios from 'axios';

const axiosExpress = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
axiosExpress.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export default axiosExpress;
```

**Base URL:** `VITE_API_URL` environment variable

**Cookie Support:** Enabled (HttpOnly cookies)

---

#### AI Services Client

**File:** `Frontend/src/AxiosInstance/axios.python.js`

**Configuration:**
```javascript
import axios from 'axios';

const axiosPython = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosPython;
```

**Base URL:** `VITE_AI_API_URL` environment variable

**Cookie Support:** Enabled (HttpOnly cookies)

---

### API Modules

#### User API

**File:** `Frontend/src/apis/Users/user.apis.js`

**Functions:**
- `registerUser(userData)` - Register new user
- `loginUser(credentials)` - Login user
- `logoutUser()` - Logout user
- `getCurrentUser()` - Get current user

**Endpoints:**
- `POST /api/users/register`
- `POST /api/users/login`
- `POST /api/users/logout`
- `GET /api/users/`

---

#### Exam API

**File:** `Frontend/src/apis/Exams/exams.apis.js`

**Functions:**
- `getExams(params)` - Get exams list
- `getExamById(id)` - Get exam by ID
- `createExam(examData)` - Create exam
- `updateExam(id, examData)` - Update exam
- `deleteExam(id)` - Delete exam

**Endpoints:**
- `GET /api/exams`
- `GET /api/exams/:id`
- `POST /api/exams/create`
- `PUT /api/exams/update/:id`
- `DELETE /api/exams/delete/:id`

---

#### Exam Session API

**File:** `Frontend/src/apis/ExamSessions/examSessions.apis.js`

**Functions:**
- `getExamSessions(params)` - Get sessions list
- `getExamSessionById(id)` - Get session by ID
- `createExamSession(sessionData)` - Create session
- `updateExamSession(id, sessionData)` - Update session
- `deleteExamSession(id)` - Delete session

**Endpoints:**
- `GET /api/examSessions/`
- `GET /api/examSessions/:id`
- `POST /api/examSessions/create`
- `PUT /api/examSessions/update/:id`
- `DELETE /api/examSessions/delete/:id`

---

#### Student API

**File:** `Frontend/src/apis/Students/student.apis.js`

**Functions:**
- `getStudents(params)` - Get students list
- `getStudentById(id)` - Get student by ID
- `createStudent(studentData)` - Create student with face
- `updateStudentFace(id, poseData)` - Update face pose
- `deleteStudent(id)` - Delete student

**Endpoints:**
- `GET /api/v1/students`
- `GET /api/v1/students/:id`
- `POST /api/v1/students`
- `PUT /api/v1/students/:id/face`
- `DELETE /api/v1/students/:id`

---

#### Video Analysis API

**File:** `Frontend/src/apis/VideoAnalysis/videoAnalysis.apis.js`

**Functions:**
- `getVideoAnalysisBySession(sessionId)` - Get analysis by session
- `getVideoAnalysesByInvigilator()` - Get invigilator's analyses
- `updateVideoAnalysis(id, data)` - Update analysis
- `deleteVideoAnalysis(id)` - Delete analysis

**Endpoints:**
- `GET /api/videoAnalysis/session/:sessionId`
- `GET /api/videoAnalysis/invigilator`
- `PUT /api/videoAnalysis/:id`
- `DELETE /api/videoAnalysis/:id`

---

#### Admin API

**File:** `Frontend/src/apis/Admin/admin.apis.js`

**Functions:**
- `getUsers(params)` - Get users
- `getUserById(id)` - Get user by ID
- `updateUser(id, userData)` - Update user
- `deleteUser(id)` - Delete user
- `verifyUser(id)` - Verify user

**Endpoints:**
- `GET /api/users/`
- `GET /api/users/:id`
- `PUT /api/users/:id`
- `DELETE /api/users/:id`

---

## Socket.IO Integration

### Configuration

**Usage:** Video processing progress updates

**Connection:**
```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000', {
  withCredentials: true,
  transports: ['websocket'],
});
```

### Events

#### Events Listened

- `pipeline_info` - General pipeline information
- `pipeline_error` - Pipeline errors
- `stage_started` - Stage started
- `stage_completed` - Stage completed
- `pipeline_completed` - Pipeline completed

#### Event Data Structure

**pipeline_info:**
```javascript
{
  message: string,
  data: {
    frame_number?: number,
    total_frames?: number,
    progress?: number,
    stage?: string
  }
}
```

**stage_started / stage_completed:**
```javascript
{
  message: string,
  data: {
    stage: string
  }
}
```

**pipeline_completed:**
```javascript
{
  message: string,
  data: {
    videoAnalysis: object,
    processingTime: number
  }
}
```

### Implementation Example

```javascript
useEffect(() => {
  const socket = io('http://localhost:8000', {
    withCredentials: true,
    transports: ['websocket'],
  });

  socket.on('pipeline_info', (data) => {
    console.log(data);
  });

  socket.on('stage_completed', (data) => {
    updateStage(data.stage);
  });

  socket.on('pipeline_completed', (data) => {
    setProcessingComplete(true);
    setVideoAnalysis(data.videoAnalysis);
  });

  return () => {
    socket.disconnect();
  };
}, []);
```

---

## Error Handling

### API Errors

**Global Interceptor:** Handles 401 unauthorized responses

**Component-Level:** Try-catch in async functions

**Display:** Error messages shown in UI

### Socket.IO Errors

**Connection Errors:** Logged to console

**Event Errors:** Handled via `pipeline_error` event

---

## Related Documentation

- [Frontend/Frontend Architecture](Frontend/Frontend%20Architecture.md) - Frontend architecture
- [Frontend/Pages and Routes](Frontend/Pages%20and%20Routes.md) - Pages and routes
- [Frontend/Components](Frontend/Components.md) - Component details
- [Frontend/Frontend File Reference](Frontend/Frontend%20File%20Reference.md) - File reference

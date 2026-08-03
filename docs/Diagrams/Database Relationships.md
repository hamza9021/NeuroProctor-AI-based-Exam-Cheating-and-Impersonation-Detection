---
title: Database Relationships
project: NeuroProctor
type: diagram
status: active
tags:
  - neuroproctor
  - diagram
  - database
last_reviewed: 2026-08-03
---

# Database Relationships Diagram

## Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Exam : creates
    User ||--o{ ExamSession : invigilates
    Exam ||--o{ ExamSession : has
    ExamSession ||--o| VideoAnalysis : has
    User ||--o{ VideoAnalysis : processes
    
    User {
        ObjectId _id PK
        string fullName
        string email UK
        string password
        string phoneNumber
        string role
        string profileImage
        boolean isVerified
        boolean isActive
        string refreshToken
        date createdAt
        date updatedAt
    }
    
    Exam {
        ObjectId _id PK
        string title
        string description
        string courseName
        string courseCode
        number duration
        date startTime
        date endTime
        string status
        ObjectId createdBy FK
        date createdAt
        date updatedAt
    }
    
    ExamSession {
        ObjectId _id PK
        ObjectId examId FK
        ObjectId invigilatorId FK
        string sessionCode UK
        string mode
        string status
        boolean verified
        date startedAt
        date endedAt
        date createdAt
        date updatedAt
    }
    
    VideoAnalysis {
        ObjectId _id PK
        ObjectId sessionId FK
        ObjectId examId FK
        ObjectId invigilatorId FK
        string originalVideo
        string processedVideo
        string status
        number processingTime
        date uploadedAt
        date completedAt
        string errorMessage
        date createdAt
        date updatedAt
    }
    
    Student {
        ObjectId _id PK
        string full_name
        string registration_number UK
        string email
        string department
        number semester
        string profile_image
        string cloudinary_public_id
        array face_embeddings
        boolean is_face_registered
        boolean is_active
        date created_at
        date updated_at
    }
```

## Relationship Descriptions

### User → Exam
- **Type:** One-to-Many
- **Description:** One user (admin/invigilator) can create many exams
- **Foreign Key:** `Exam.createdBy` → `User._id`

### User → ExamSession
- **Type:** One-to-Many
- **Description:** One user (invigilator) can be assigned to many exam sessions
- **Foreign Key:** `ExamSession.invigilatorId` → `User._id`

### Exam → ExamSession
- **Type:** One-to-Many
- **Description:** One exam can have many exam sessions
- **Foreign Key:** `ExamSession.examId` → `Exam._id`

### ExamSession → VideoAnalysis
- **Type:** One-to-One
- **Description:** One exam session has one video analysis record
- **Foreign Key:** `VideoAnalysis.sessionId` → `ExamSession._id`

### User → VideoAnalysis
- **Type:** One-to-Many
- **Description:** One user (invigilator) can process many video analyses
- **Foreign Key:** `VideoAnalysis.invigilatorId` → `User._id`

### Student
- **Type:** Independent
- **Description:** Student collection has no direct relationships to other collections
- **Usage:** Used for face enrollment and matching in AI pipeline

## Related Documentation

- [09 - Database Reference](09%20-%20Database%20Reference.md) - Detailed database schema
- [02 - System Architecture](02%20-%20System%20Architecture.md) - System design

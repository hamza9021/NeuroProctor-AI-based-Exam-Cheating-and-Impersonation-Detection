---
title: Services and Repositories
project: NeuroProctor
type: reference
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - services
last_reviewed: 2026-08-03
---

# Services and Repositories

This document details all services and repositories in the Backend (Express) application.

## Services

### Cloudinary Service

**File:** `Backend(Express)/src/Services/cloudinary.service.js`

**Purpose:** Handle Cloudinary operations for image and video upload/deletion

**Used by:**
- User controller (profile image upload)
- Video controller (video upload - if implemented)

**Depends on:**
- cloudinary npm package
- Environment variables (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)

**Key Symbols:**
- `uploadImage(file)` - Upload image to Cloudinary
- `deleteImage(publicId)` - Delete image from Cloudinary

**Runtime Role:** Provides abstraction layer for Cloudinary API

**Status:** Implemented

**Notes:**
- Configured with folder structure for organization
- Returns public URL and public ID for uploaded files
- Used for profile image storage

---

## Repositories

The Backend (Express) application uses Mongoose models directly as repositories. There is no separate repository layer. Database operations are performed directly in controllers using Mongoose model methods.

### Model as Repository Pattern

**Pattern:** Mongoose models act as repositories

**Usage:**
- Controllers use Mongoose model methods directly
- No separate repository layer
- Business logic in controllers

**Examples:**
```javascript
// Create
const user = await User.create(userData);

// Find
const user = await User.findOne({ email });

// Update
const user = await User.findByIdAndUpdate(id, updateData, { new: true });

// Delete
await User.findByIdAndDelete(id);
```

---

## Related Documentation

- [Backend/Backend Architecture](Backend/Backend%20Architecture.md) - Backend architecture
- [Backend/Routes and Controllers](Backend/Routes%20and%20Controllers.md) - Routes and controllers
- [Backend/Models and Schemas](Backend/Models%20and%20Schemas.md) - Models
- [Backend/Backend File Reference](Backend/Backend%20File%20Reference.md) - File reference

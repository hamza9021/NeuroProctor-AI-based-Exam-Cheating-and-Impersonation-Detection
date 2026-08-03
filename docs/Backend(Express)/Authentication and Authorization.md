---
title: Authentication and Authorization
project: NeuroProctor
type: reference
service: backend
status: active
tags:
  - neuroproctor
  - backend
  - authentication
  - authorization
last_reviewed: 2026-08-03
---

# Authentication and Authorization

This document details authentication and authorization in the Backend (Express) application.

## Authentication

### JWT Token System

**Token Types:**
- **Access Token:** Short-lived (15 minutes)
- **Refresh Token:** Long-lived (7 days)

**Token Payload:**
```javascript
{
  "_id": "user_id",
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "invigilator"
}
```

### Token Generation

**File:** `Backend(Express)/src/Utils/index.utils.js`

**Functions:**
- `generateAccessToken(user)` - Generate access token
- `generateRefreshToken(user)` - Generate refresh token

**Access Token Configuration:**
```javascript
{
  expiresIn: process.env.ACCESS_TOKEN_EXPIRY || '15m',
  secret: process.env.ACCESS_TOKEN_SECRET
}
```

**Refresh Token Configuration:**
```javascript
{
  expiresIn: process.env.REFRESH_TOKEN_EXPIRY || '7d',
  secret: process.env.REFRESH_TOKEN_SECRET
}
```

---

### Token Verification Middleware

**File:** `Backend(Express)/src/Middleware/auth.middleware.js`

**Function:** `verifyJWT`

**Process:**
1. Extract access token from HttpOnly cookie
2. Verify token signature using `ACCESS_TOKEN_SECRET`
3. Decode token payload
4. Attach user to `req.user`
5. Call next middleware or controller

**Usage:**
```javascript
router.get('/protected', verifyJWT, controller);
```

**Error Handling:**
- 401 - Invalid or missing token
- 403 - Token expired

---

### Password Security

**Hashing:** bcrypt with 10 salt rounds

**File:** `Backend(Express)/src/Models/user.models.js`

**Method:** `isPasswordMatch(password)`

**Process:**
```javascript
const isMatch = await bcrypt.compare(enteredPassword, this.password);
```

**Storage:** Hashed password only (never plain text)

---

### Cookie Configuration

**File:** `Backend(Express)/src/Options/cookie.options.js`

**Configuration:**
```javascript
{
  httpOnly: true,      // Prevents JavaScript access
  secure: false,       // Set to true in production with HTTPS
  sameSite: 'lax',     // CSRF protection
  maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
}
```

---

## Authorization

### Role-Based Access Control

**Roles:**
- `admin` - Full system access
- `invigilator` - Exam and session management

### Role Checks

**Implementation:** Role checks in controllers

**Example:**
```javascript
if (req.user.role !== 'admin') {
  throw new ApiError(403, "Forbidden: Admin access required");
}
```

**Protected Operations:**
- User management (admin only)
- Exam creation (admin only)
- Exam session creation (invigilator only)
- Video analysis (invigilator only)

---

### Resource Ownership

**Pattern:** Verify resource ownership before modification

**Example:**
```javascript
const exam = await Exam.findById(id);
if (exam.createdBy.toString() !== req.user._id.toString()) {
  throw new ApiError(403, "Forbidden: Not the creator");
}
```

**Applied to:**
- Exam updates/deletion (creator check)
- Exam session updates/deletion (invigilator check)
- Video analysis updates/deletion (invigilator check)

---

## Authentication Flow

### Login Flow

```
Frontend POST /api/users/login
→ Backend validates credentials
→ Backend verifies role match
→ Backend generates access token
→ Backend generates refresh token
→ Backend sets HttpOnly cookies
→ Backend returns user data
→ Frontend stores user in AuthContext
```

### Protected Request Flow

```
Frontend request with HttpOnly cookie
→ Backend verifyJWT middleware
→ Extract token from cookie
→ Verify token signature
→ Decode payload
→ Attach user to req.user
→ Controller executes
→ Response returned
```

---

## Security Considerations

### Current Implementation Status

**Implemented:**
- ✅ JWT token generation and verification
- ✅ HttpOnly cookies for token storage
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ Resource ownership checks

**Missing:**
- ❌ Refresh token rotation
- ❌ Token blacklist for logout
- ❌ Account lockout after failed attempts
- ❌ Password complexity requirements
- ❌ 2FA for admin operations
- ❌ Request signing for critical operations

### Known Security Issues

1. **Refresh Token Not Used:** Refresh tokens are generated but not used for automatic token renewal. Users must re-login after access token expires (15 minutes).

2. **No Token Blacklist:** Logout does not invalidate access tokens. Tokens remain valid until expiry.

3. **No Account Lockout:** No protection against brute force attacks on login.

4. **CORS Configuration:** `secure: false` in cookie options (should be `true` in production with HTTPS).

---

## Related Documentation

- [Backend/Backend Architecture](Backend/Backend%20Architecture.md) - Backend architecture
- [Backend/Routes and Controllers](Backend/Routes%20and%20Controllers.md) - Routes and controllers
- [11 - Security and Authentication](11%20-%20Security%20and%20Authentication.md) - Security details
- [Workflows/User Authentication Workflow](Workflows/User%20Authentication%20Workflow.md) - Authentication workflow

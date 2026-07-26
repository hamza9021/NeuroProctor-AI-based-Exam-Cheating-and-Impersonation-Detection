"""
Security constants and configuration.

Centralises JWT algorithm selection and security-related constants
so they are never duplicated or hard-coded across the codebase.

All values are derived from the application settings so that a single
change in .env propagates everywhere automatically.
"""
from app.config.settings import settings

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

# Signing algorithm. Must match what the Express backend uses.
# jsonwebtoken (Node.js) defaults to HS256 when no algorithm is specified.
JWT_ALGORITHM: str = settings.JWT_ALGORITHM

# The HttpOnly cookie name set by the Express backend's login response.
# FastAPI reads this cookie on every protected request.
JWT_COOKIE_NAME: str = "accessToken"

# ---------------------------------------------------------------------------
# Role-Based Access Control
# ---------------------------------------------------------------------------

# The complete list of roles that exist in the Express user model.
ALL_ROLES: list[str] = ["admin", "invigilator"]

# Roles permitted to call the Student CRUD / face registration endpoints.
STUDENT_API_ROLES: list[str] = ["admin", "invigilator"]

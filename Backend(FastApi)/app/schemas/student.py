"""
Pydantic v2 request and response schemas for the Student API.

These schemas define the *public contract* of the REST API.
They are intentionally kept separate from app/models/student.py (which
mirrors the MongoDB document shape) to enforce separation of concerns:

  - models/student.py  → what is stored in MongoDB
  - schemas/student.py → what is accepted / returned over HTTP

Key differences:
  - Raw 512-dim embedding vectors are never exposed in list responses
    (too large and unnecessary for most consumers).
  - FaceEmbeddingResponse adds a computed `is_registered` boolean.
  - StudentResponse uses str for `id` (already serialised from ObjectId).
  - TokenPayload represents the decoded JWT payload used by auth dependencies.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# =============================================================================
# Auth schemas
# =============================================================================

class TokenPayload(BaseModel):
    """
    Decoded JWT payload after Express token verification.

    Field mapping from Express → Python:
        _id      → user_id   (MongoDB ObjectId as str)
        fullName → full_name (snake_case)
        email    → email
        role     → role
    """

    user_id: str = Field(..., description="MongoDB ObjectId of the authenticated user.")
    email: str = Field(..., description="User email address.")
    full_name: str = Field(default="", description="User full name.")
    role: str = Field(..., description="User role: 'admin' or 'invigilator'.")


# =============================================================================
# Student request schemas
# =============================================================================

class StudentCreateRequest(BaseModel):
    """
    Validated fields for the student registration endpoint.

    Note: profile_image is handled separately as a FastAPI UploadFile parameter
    and is therefore NOT included in this schema.
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Student's full name (2–100 characters).",
    )
    registration_number: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique university registration / roll number.",
    )
    email: EmailStr = Field(
        ...,
        description="Student's institutional email address.",
    )
    department: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Academic department name.",
    )
    semester: int = Field(
        ...,
        ge=1,
        le=8,
        description="Current semester (1–8).",
    )

    @field_validator("registration_number")
    @classmethod
    def strip_registration_number(cls, v: str) -> str:
        """Remove leading/trailing whitespace from the registration number."""
        return v.strip()

    @field_validator("full_name", "department")
    @classmethod
    def strip_text_fields(cls, v: str) -> str:
        """Remove leading/trailing whitespace from text fields."""
        return v.strip()

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        """Normalise email to lowercase for consistent storage and lookups."""
        return v.lower().strip()


# =============================================================================
# Student response schemas
# =============================================================================

class FaceEmbeddingResponse(BaseModel):
    """
    Public representation of a single face embedding.

    The raw 512-dimensional vector is deliberately excluded from API responses
    to keep payloads small and prevent accidental leakage.  The boolean
    `is_registered` flag tells consumers whether a real embedding exists.
    """

    pose: str = Field(..., description="Head pose: front | left | right | up | down.")
    quality_score: float = Field(..., description="Detection confidence (0.0–1.0).")
    captured_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp of capture. None for unregistered poses.",
    )
    is_registered: bool = Field(
        ...,
        description="True if a 512-dim embedding has been captured for this pose.",
    )


class StudentResponse(BaseModel):
    """
    Standard student response returned by all student endpoints.

    Embedding vectors are omitted.  Use the admin embedding inspection
    endpoint (if implemented) to retrieve raw vectors.
    """

    id: str = Field(..., description="MongoDB document ID (hex string).")
    full_name: str
    registration_number: str
    email: str
    department: str
    semester: int
    profile_image: str = Field(..., description="Cloudinary HTTPS URL.")
    is_face_registered: bool
    is_active: bool
    face_embeddings: list[FaceEmbeddingResponse]
    created_at: datetime
    updated_at: datetime

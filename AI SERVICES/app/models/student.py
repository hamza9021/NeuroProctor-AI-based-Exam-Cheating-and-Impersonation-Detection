"""
MongoDB document models for the Student collection.

These Pydantic v2 models mirror the *exact* shape of documents stored
in the 'students' MongoDB collection.  They are used exclusively by
the repository layer for reading raw documents and by the service layer
when building new documents to insert.

For API request/response contracts, see app/schemas/student.py.

Student document shape:
    {
        "_id":                 ObjectId,
        "full_name":           str,
        "registration_number": str,
        "email":               str,
        "department":          str,
        "semester":            int  (1–8),
        "profile_image":       str  (Cloudinary HTTPS URL),
        "cloudinary_public_id": str (used for deletion),
        "face_embeddings": [
            {
                "pose":          str   ("front" | "left" | "right" | "up" | "down"),
                "embedding":     list[float]  (512 values, or [] if not yet captured),
                "quality_score": float (0.0–1.0),
                "captured_at":   datetime | None
            },
            ...
        ],
        "is_face_registered": bool,
        "is_active":          bool,
        "created_at":         datetime,
        "updated_at":         datetime
    }
"""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.utils.objectid import PyObjectId

# ---------------------------------------------------------------------------
# Valid head poses — order matters (front is always registered first)
# ---------------------------------------------------------------------------
VALID_POSES: list[str] = ["front", "left", "right", "up", "down"]


# =============================================================================
# FaceEmbedding — subdocument model
# =============================================================================

class FaceEmbedding(BaseModel):
    """
    A single face embedding associated with a specific head pose.

    When a student is first registered with only a front-facing image,
    the service creates four additional placeholder embeddings (left, right,
    up, down) with empty embedding vectors and quality_score = 0.0.
    These placeholders are replaced via the face-update endpoint when the
    remaining poses are captured.
    """

    pose: str = Field(
        ...,
        description="Head orientation: 'front' | 'left' | 'right' | 'up' | 'down'.",
    )
    embedding: list[float] = Field(
        default_factory=list,
        description=(
            "512-dimensional ArcFace embedding vector. "
            "Empty list ([]) indicates this pose has not yet been captured."
        ),
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="InsightFace detection confidence score (0.0 = placeholder, 1.0 = perfect).",
    )
    captured_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when this embedding was generated. None for placeholders.",
    )

    @property
    def is_registered(self) -> bool:
        """True if a real 512-dimensional embedding vector has been stored."""
        return len(self.embedding) == 512

    model_config = {"populate_by_name": True}


# =============================================================================
# StudentDocument — full collection document model
# =============================================================================

class StudentDocument(BaseModel):
    """
    Complete student MongoDB document model.

    The `id` field uses alias `_id` so that raw MongoDB documents (which
    use `_id`) can be parsed directly without field remapping.

    PyObjectId serialises the ObjectId as a plain string in JSON output,
    making it frontend-friendly while keeping the BSON type in the DB.
    """

    id: Optional[PyObjectId] = Field(
        default=None,
        alias="_id",
        description="MongoDB document ID (ObjectId serialised as string).",
    )
    full_name: str = Field(..., description="Student's full name.")
    registration_number: str = Field(
        ...,
        description="Unique university registration / roll number.",
    )
    email: str = Field(..., description="Student's institutional email address.")
    department: str = Field(..., description="Academic department name.")
    semester: int = Field(..., ge=1, le=8, description="Current semester (1–8).")

    # Cloudinary
    profile_image: str = Field(
        ...,
        description="Cloudinary HTTPS URL of the student's profile photo.",
    )
    cloudinary_public_id: str = Field(
        default="",
        description="Cloudinary public_id used for image deletion.",
    )

    # Face embeddings — up to 5 (one per pose)
    face_embeddings: list[FaceEmbedding] = Field(
        default_factory=list,
        description="Pose-indexed face embedding subdocuments.",
    )

    # Status flags
    is_face_registered: bool = Field(
        default=False,
        description="True when at least the front-pose embedding has been captured.",
    )
    is_active: bool = Field(
        default=True,
        description="Soft-delete flag. False means the student is logically deleted.",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Document creation timestamp (UTC).",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last document modification timestamp (UTC).",
    )

    model_config = {
        "populate_by_name": True,       # Accept both field name and alias
        "arbitrary_types_allowed": True, # Required for PyObjectId (bson.ObjectId)
        "json_encoders": {PyObjectId: str},
    }

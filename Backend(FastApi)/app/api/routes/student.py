"""
Student API routes — all protected by JWT + role authorisation.

Every endpoint requires the 'accessToken' HttpOnly cookie issued by the
Express backend.  Only users with the 'admin' or 'invigilator' role may
call any endpoint in this router.

Routes:
    POST   /api/v1/students                    — Register new student + face
    GET    /api/v1/students                    — List students (paginated)
    GET    /api/v1/students/{student_id}       — Get student by ID
    PUT    /api/v1/students/{student_id}/face  — Update face pose embedding
    DELETE /api/v1/students/{student_id}       — Delete student

Auth errors:
    401 — Cookie missing / JWT expired / JWT invalid
    403 — Role not in ["admin", "invigilator"]

All responses follow the standard envelope:
    Success: { "success": true,  "message": "...", "data": {...} }
    Error:   { "success": false, "message": "...", "errors": [...] }
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.dependencies import require_roles
from app.core.responses import paginated_response, success_response
from app.schemas.student import StudentCreateRequest, TokenPayload
from app.services.student_service import student_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

# ---------------------------------------------------------------------------
# Reusable role guard — imported once, applied to every route via Depends()
# ---------------------------------------------------------------------------
_protected = require_roles(["admin", "invigilator"])


# =============================================================================
# POST /students — Register new student with face embedding
# =============================================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student with face embedding",
    description="""
Register a new student and generate their face embedding using InsightFace (GPU).

**Upload format:** `multipart/form-data`

**Processing pipeline:**
1. Validate image (JPEG/PNG, max 5 MB, exactly 1 face).
2. Check for duplicate registration number / email.
3. Upload profile image to Cloudinary.
4. Generate 512-dim ArcFace front embedding via InsightFace.
5. Create 4 empty placeholder slots for remaining poses (left/right/up/down).
6. Insert student document in MongoDB.
7. Return 201 with student data.

**Note on pose placeholders:**  
The remaining 4 poses are stored as empty placeholder embeddings in the  
document from day one.  Use `PUT /students/{id}/face` to fill them in  
as additional pose photos are captured.
    """,
)
async def create_student(
    # ── Form fields ────────────────────────────────────────────────────────
    full_name: str = Form(
        ...,
        description="Student's full name (2–100 characters).",
        min_length=2,
        max_length=100,
    ),
    registration_number: str = Form(
        ...,
        description="Unique university registration / roll number (e.g. SP23-BCS-183).",
        min_length=3,
        max_length=30,
    ),
    email: str = Form(
        ...,
        description="Student's institutional email address.",
    ),
    department: str = Form(
        ...,
        description="Academic department (e.g. Computer Science).",
        min_length=2,
        max_length=100,
    ),
    semester: int = Form(
        ...,
        description="Current semester number (1–8).",
        ge=1,
        le=8,
    ),
    profile_image: UploadFile = File(
        ...,
        description="Student face photo. Accepted: JPEG, PNG. Max size: 5 MB. "
                    "Must contain exactly one face.",
    ),
    # ── Auth dependency ────────────────────────────────────────────────────
    current_user: TokenPayload = Depends(_protected),
):
    """Register a new student and generate their front-pose face embedding."""
    # Build a validated request object from the form fields
    request = StudentCreateRequest(
        full_name=full_name,
        registration_number=registration_number,
        email=email,
        department=department,
        semester=semester,
    )

    student = await student_service.create_student(request, profile_image)

    logger.info(
        "Student registered — id: %s | by: %s (%s)",
        student.id,
        current_user.email,
        current_user.role,
    )

    return success_response(
        data=student.model_dump(mode="json"),
        message="Student registered successfully.",
        status_code=status.HTTP_201_CREATED,
    )


# =============================================================================
# GET /students — Paginated student list
# =============================================================================

@router.get(
    "",
    summary="List all students (paginated, searchable, sortable)",
    description="""
Returns a paginated list of active students.

**Search** performs case-insensitive regex matching across:
- full_name
- email
- registration_number
- department

**Embedding vectors are NOT included** in list responses (use GET /students/{id} for details).
    """,
)
async def list_students(
    page: int = Query(
        default=1, ge=1,
        description="Page number (1-indexed).",
    ),
    limit: int = Query(
        default=10, ge=1, le=100,
        description="Number of students per page (1–100).",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search query matched against name, email, reg. number, department.",
    ),
    sort_by: str = Query(
        default="created_at",
        description="Field to sort results by.",
    ),
    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort direction: 'asc' (oldest first) or 'desc' (newest first).",
    ),
    current_user: TokenPayload = Depends(_protected),
):
    """Return a paginated, searchable list of active students."""
    students, total = await student_service.get_all_students(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return paginated_response(
        data=[s.model_dump(mode="json") for s in students],
        total=total,
        page=page,
        limit=limit,
        message="Students retrieved successfully.",
    )


# =============================================================================
# GET /students/{student_id} — Get single student
# =============================================================================

@router.get(
    "/{student_id}",
    summary="Get student by ID",
    description="Retrieve complete details for a single active student by MongoDB ObjectId.",
)
async def get_student(
    student_id: str,
    current_user: TokenPayload = Depends(_protected),
):
    """Retrieve a single student's full details."""
    student = await student_service.get_student(student_id)

    return success_response(
        data=student.model_dump(mode="json"),
        message="Student retrieved successfully.",
    )


# =============================================================================
# PUT /students/{student_id}/face — Update face embedding for a pose
# =============================================================================

@router.put(
    "/{student_id}/face",
    summary="Update face embedding for a specific pose",
    description="""
Replace the face embedding for one specific head pose.

**Valid poses:** `front` | `left` | `right` | `up` | `down`

**Use cases:**
- Complete face registration by capturing the 4 remaining poses after initial enrollment.
- Re-register a pose with a better quality image (e.g., better lighting).

The update is atomic — only the specified pose embedding is replaced.
All other pose embeddings remain unchanged.

After all 5 poses are captured, `is_face_registered` is automatically set to `true`.
    """,
)
async def update_student_face(
    student_id: str,
    pose: str = Form(
        ...,
        description="Head pose to update. One of: front | left | right | up | down",
    ),
    image: UploadFile = File(
        ...,
        description="Face photo for this pose. JPEG/PNG, max 5 MB, exactly 1 face.",
    ),
    current_user: TokenPayload = Depends(_protected),
):
    """Replace the face embedding for a given head pose."""
    student = await student_service.update_student_face(student_id, pose, image)

    logger.info(
        "Face embedding updated — student: %s | pose: %s | by: %s (%s)",
        student_id,
        pose,
        current_user.email,
        current_user.role,
    )

    return success_response(
        data=student.model_dump(mode="json"),
        message=f"Face embedding for pose '{pose}' updated successfully.",
    )


# =============================================================================
# DELETE /students/{student_id} — Delete student
# =============================================================================

@router.delete(
    "/{student_id}",
    summary="Delete a student",
    description="""
Permanently delete a student from the system.

**Actions performed:**
1. Verify the student exists.
2. Delete the profile image from Cloudinary.
3. Hard-delete the MongoDB document.

**Warning:** This is a permanent hard-delete. The student record cannot be recovered.
For soft-delete behaviour, use the `is_active` flag pattern (not yet a separate endpoint).
    """,
)
async def delete_student(
    student_id: str,
    current_user: TokenPayload = Depends(_protected),
):
    """Permanently delete a student and their Cloudinary image."""
    await student_service.delete_student(student_id)

    logger.info(
        "Student deleted — id: %s | by: %s (%s)",
        student_id,
        current_user.email,
        current_user.role,
    )

    return success_response(
        data={"deleted_id": student_id},
        message="Student deleted successfully.",
    )

"""
Student service — business logic orchestrator.

This is the heart of the AI pipeline.  It coordinates:
  1. Image validation (type, size)
  2. Duplicate checking (registration number, email)
  3. Cloudinary image upload
  4. InsightFace face embedding generation (GPU-accelerated)
  5. MongoDB persistence via StudentRepository

The service layer enforces all business rules and is the only place where
multiple services are called together.  Route handlers are thin — they
delegate everything here.

Error handling contract:
  All methods raise typed AppException subclasses (from app/core/exceptions.py).
  These propagate up to the global exception handlers in main.py which convert
  them into the standard JSON error envelope automatically.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile

from app.config.settings import settings
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ServiceException,
    ValidationException,
)
from app.models.student import FaceEmbedding, VALID_POSES
from app.repositories.student_repository import StudentRepository
from app.schemas.student import (
    FaceEmbeddingResponse,
    StudentCreateRequest,
    StudentResponse,
)
from app.services.cloudinary_service import cloudinary_service
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class StudentService:
    """
    High-level student management service.

    Orchestrates the full student lifecycle:
      - Registration (image upload + face embedding + DB insert)
      - Face embedding updates (per pose)
      - Retrieval (single + paginated list)
      - Deletion (Cloudinary cleanup + MongoDB delete)
    """

    def __init__(self) -> None:
        self._repo = StudentRepository()

    # =========================================================================
    # Private helpers
    # =========================================================================

    async def _validate_image(self, file: UploadFile) -> bytes:
        """
        Read and validate an uploaded image file.

        Checks:
          - Content-Type is in ALLOWED_IMAGE_TYPES (jpeg/jpg/png).
          - File size does not exceed MAX_IMAGE_SIZE_MB.

        Args:
            file: FastAPI UploadFile object from a multipart/form-data request.

        Returns:
            Raw file bytes if all checks pass.

        Raises:
            ValidationException: On MIME type or size violation.
        """
        content_type = (file.content_type or "").lower().strip()

        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise ValidationException(
                f"Unsupported image format '{content_type}'. "
                f"Accepted formats: JPEG, JPG, PNG.",
            )

        file_bytes = await file.read()
        max_bytes = settings.MAX_IMAGE_SIZE_MB * 1_024 * 1_024

        if len(file_bytes) > max_bytes:
            size_mb = len(file_bytes) / 1_048_576
            raise ValidationException(
                f"Image size ({size_mb:.2f} MB) exceeds the maximum "
                f"allowed size of {settings.MAX_IMAGE_SIZE_MB} MB.",
            )

        return file_bytes

    @staticmethod
    def _doc_to_response(doc: dict) -> StudentResponse:
        """
        Convert a raw MongoDB document dict to a StudentResponse schema.

        Handles:
          - _id ObjectId → str conversion
          - face_embeddings sub-documents → FaceEmbeddingResponse list
          - Computed is_registered flag per pose

        Args:
            doc: Raw dict returned by Motor (includes _id as ObjectId).

        Returns:
            Typed StudentResponse instance ready for JSON serialisation.
        """
        embeddings = [
            FaceEmbeddingResponse(
                pose=e.get("pose", ""),
                quality_score=float(e.get("quality_score", 0.0)),
                captured_at=e.get("captured_at"),
                is_registered=len(e.get("embedding", [])) == settings.EMBEDDING_DIMENSION,
            )
            for e in doc.get("face_embeddings", [])
        ]

        # Maintain canonical pose order for consistent API responses
        pose_order = {p: i for i, p in enumerate(VALID_POSES)}
        embeddings.sort(key=lambda e: pose_order.get(e.pose, 99))

        return StudentResponse(
            id=str(doc["_id"]),
            full_name=doc["full_name"],
            registration_number=doc["registration_number"],
            email=doc["email"],
            department=doc["department"],
            semester=doc["semester"],
            profile_image=doc["profile_image"],
            is_face_registered=doc.get("is_face_registered", False),
            is_active=doc.get("is_active", True),
            face_embeddings=embeddings,
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    # =========================================================================
    # Create student
    # =========================================================================

    async def create_student(
        self,
        request: StudentCreateRequest,
        profile_image: UploadFile,
    ) -> StudentResponse:
        """
        Full student registration pipeline.

        Steps:
          1. Validate image (type + size check — cheap operation first).
          2. Check for duplicate registration_number and email in MongoDB.
          3. Upload the profile image to Cloudinary.
          4. Generate the front-pose face embedding via InsightFace (GPU).
          5. Build empty placeholder embeddings for the 4 remaining poses.
          6. Build and insert the student document in MongoDB.
          7. Return the serialised StudentResponse.

        Cloudinary rollback:
          If embedding extraction fails AFTER the image was uploaded to
          Cloudinary, the service deletes the Cloudinary image before
          re-raising the exception.  This prevents orphaned uploads.

        Args:
            request:       Validated StudentCreateRequest with form data.
            profile_image: Uploaded face image UploadFile.

        Returns:
            StudentResponse for the newly created student.

        Raises:
            ValidationException:  Image type/size/face detection error.
            ConflictException:    Duplicate registration number or email.
            ServiceException:     Cloudinary or InsightFace failure.
        """
        # ── Step 1: Validate image ────────────────────────────────────────────
        image_bytes = await self._validate_image(profile_image)

        # ── Step 2: Duplicate check ───────────────────────────────────────────
        # Perform DB checks before touching external services (Cloudinary/GPU)
        # to fail fast and avoid wasted cloud API calls.
        existing_reg = await self._repo.find_by_registration_number(
            request.registration_number
        )
        if existing_reg:
            raise ConflictException(
                f"A student with registration number "
                f"'{request.registration_number}' already exists."
            )

        existing_email = await self._repo.find_by_email(request.email)
        if existing_email:
            raise ConflictException(
                f"A student with email '{request.email}' already exists."
            )

        # ── Step 3: Upload to Cloudinary ──────────────────────────────────────
        # Create a URL-safe public_id from the registration number
        reg_slug = (
            request.registration_number
            .replace("/", "-")
            .replace(" ", "_")
            .lower()
        )
        cloudinary_result = await cloudinary_service.upload_image(
            file_bytes=image_bytes,
            subfolder="profiles",
            public_id=f"neuroproctor/students/profiles/{reg_slug}",
        )
        cloudinary_url: str = cloudinary_result["url"]
        cloudinary_public_id: str = cloudinary_result["public_id"]

        logger.info(
            "Cloudinary upload done — student: %s | url: %s",
            request.registration_number,
            cloudinary_url,
        )

        # ── Step 4: Generate front embedding ──────────────────────────────────
        # If this fails, roll back the Cloudinary upload to prevent orphaned images.
        try:
            front_embedding: FaceEmbedding = await embedding_service.generate_embedding(
                image_bytes=image_bytes,
                pose="front",
            )
        except (ValidationException, ServiceException):
            # Rollback Cloudinary upload on embedding failure
            logger.warning(
                "Embedding failed — rolling back Cloudinary upload for '%s'",
                cloudinary_public_id,
            )
            await cloudinary_service.delete_image(cloudinary_public_id)
            raise  # Re-raise the original exception

        logger.info(
            "Front embedding generated — quality: %.4f",
            front_embedding.quality_score,
        )

        # ── Step 5: Build placeholder embeddings ──────────────────────────────
        placeholder_embeddings: list[FaceEmbedding] = (
            embedding_service.build_placeholder_embeddings(
                registered_poses=["front"]
            )
        )

        # Final ordered embedding list: [front, left(empty), right(empty), up(empty), down(empty)]
        all_embeddings: list[FaceEmbedding] = [front_embedding] + placeholder_embeddings

        # ── Step 6: Build and insert MongoDB document ─────────────────────────
        now = datetime.now(timezone.utc)
        student_doc: dict = {
            "full_name": request.full_name,
            "registration_number": request.registration_number,
            "email": request.email,  # Already lowercase-normalised by validator
            "department": request.department,
            "semester": request.semester,
            "profile_image": cloudinary_url,
            "cloudinary_public_id": cloudinary_public_id,
            "face_embeddings": [e.model_dump() for e in all_embeddings],
            "is_face_registered": True,   # Front pose captured
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        inserted_id: str = await self._repo.insert_one(student_doc)
        logger.info(
            "Student inserted — id: %s | reg: %s",
            inserted_id,
            request.registration_number,
        )

        # ── Step 7: Fetch created document and return response ─────────────────
        created_doc = await self._repo.find_by_id(inserted_id)
        if not created_doc:
            raise ServiceException(
                "Student was successfully created but could not be retrieved. "
                "Please check the database."
            )

        return self._doc_to_response(created_doc)

    # =========================================================================
    # Get single student
    # =========================================================================

    async def get_student(self, student_id: str) -> StudentResponse:
        """
        Retrieve a single active student by their MongoDB ObjectId string.

        Args:
            student_id: 24-character hex string ObjectId.

        Returns:
            StudentResponse for the found student.

        Raises:
            NotFoundException: Student not found or soft-deleted.
        """
        doc = await self._repo.find_active_by_id(student_id)
        if not doc:
            raise NotFoundException(
                f"Student with ID '{student_id}' was not found."
            )
        return self._doc_to_response(doc)

    # =========================================================================
    # Get all students (paginated)
    # =========================================================================

    async def get_all_students(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[StudentResponse], int]:
        """
        Retrieve a paginated, searchable, sortable list of active students.

        Args:
            page:       1-indexed page number (minimum 1).
            limit:      Students per page (maximum 100, enforced here).
            search:     Optional search string matched across name, email,
                        registration number, and department.
            sort_by:    Field name to sort results by.
            sort_order: 'asc' or 'desc'.

        Returns:
            Tuple of (list_of_StudentResponse, total_matching_count).
        """
        # Enforce sensible upper bound to prevent memory exhaustion
        limit = min(max(limit, 1), 100)

        documents, total = await self._repo.get_paginated(
            page=page,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        students = [self._doc_to_response(doc) for doc in documents]
        return students, total

    # =========================================================================
    # Update face embedding for a pose
    # =========================================================================

    async def update_student_face(
        self,
        student_id: str,
        pose: str,
        image: UploadFile,
    ) -> StudentResponse:
        """
        Replace the face embedding for a specific head pose.

        Used to:
          - Complete initial registration by capturing the 4 remaining poses
            (left, right, up, down) after the front pose is done.
          - Re-register a pose with a better quality image.

        The MongoDB update is atomic — if the update fails, the student
        document is left in its prior state (no partial writes).

        Args:
            student_id: 24-character hex ObjectId string.
            pose:       Head pose name (must be in VALID_POSES).
            image:      Uploaded face image for this pose.

        Returns:
            Updated StudentResponse with the new embedding reflected.

        Raises:
            ValidationException: Invalid pose, bad image, or face detection error.
            NotFoundException:   Student not found.
            ServiceException:    Embedding or database failure.
        """
        # Validate pose before any I/O
        if pose not in VALID_POSES:
            raise ValidationException(
                f"Invalid pose '{pose}'. "
                f"Accepted values are: {VALID_POSES}."
            )

        # Verify student exists
        doc = await self._repo.find_active_by_id(student_id)
        if not doc:
            raise NotFoundException(
                f"Student with ID '{student_id}' was not found."
            )

        # Validate and read image
        image_bytes = await self._validate_image(image)

        # Generate embedding for the specified pose
        new_embedding: FaceEmbedding = await embedding_service.generate_embedding(
            image_bytes=image_bytes,
            pose=pose,
        )

        # Atomically replace embedding in MongoDB
        success = await self._repo.add_or_replace_embedding(
            student_id, new_embedding
        )
        if not success:
            raise ServiceException(
                f"Failed to update the '{pose}' embedding in the database."
            )

        # After update, check if all 5 poses now have real embeddings.
        # If so, mark is_face_registered = True.
        updated_doc = await self._repo.find_active_by_id(student_id)
        if updated_doc:
            all_registered = all(
                len(e.get("embedding", [])) == settings.EMBEDDING_DIMENSION
                for e in updated_doc.get("face_embeddings", [])
                if e.get("pose") in VALID_POSES
            )
            registered_poses = [
                e.get("pose")
                for e in updated_doc.get("face_embeddings", [])
                if len(e.get("embedding", [])) == settings.EMBEDDING_DIMENSION
            ]
            if len(registered_poses) == len(VALID_POSES):
                await self._repo.set_face_registered_status(student_id, True)
                logger.info(
                    "All 5 poses registered for student %s — "
                    "is_face_registered set to True.",
                    student_id,
                )

        logger.info(
            "Face embedding updated — student: %s | pose: %s | quality: %.4f",
            student_id,
            pose,
            new_embedding.quality_score,
        )

        # Return the final refreshed document
        final_doc = await self._repo.find_active_by_id(student_id)
        if not final_doc:
            raise ServiceException(
                "Student could not be retrieved after face update."
            )
        return self._doc_to_response(final_doc)

    # =========================================================================
    # Delete student
    # =========================================================================

    async def delete_student(self, student_id: str) -> bool:
        """
        Permanently delete a student and their Cloudinary profile image.

        Steps:
          1. Verify the student exists.
          2. Attempt to delete the Cloudinary image (non-fatal on failure).
          3. Hard-delete the MongoDB document.

        Note: Cloudinary deletion failure is logged as a warning but does NOT
        prevent the MongoDB deletion.  This ensures no student record is left
        dangling just because of a transient Cloudinary error.

        Args:
            student_id: 24-character hex ObjectId string.

        Returns:
            True on successful deletion.

        Raises:
            NotFoundException: Student does not exist or is already deleted.
            ServiceException:  MongoDB deletion failed.
        """
        # Verify student exists first
        doc = await self._repo.find_active_by_id(student_id)
        if not doc:
            raise NotFoundException(
                f"Student with ID '{student_id}' was not found."
            )

        # Attempt Cloudinary image removal (best-effort)
        cloudinary_public_id: str = doc.get("cloudinary_public_id", "")
        if cloudinary_public_id:
            try:
                deleted_from_cloud = await cloudinary_service.delete_image(
                    cloudinary_public_id
                )
                if not deleted_from_cloud:
                    logger.warning(
                        "Cloudinary image not found for student %s "
                        "(public_id: '%s') — proceeding with DB deletion.",
                        student_id,
                        cloudinary_public_id,
                    )
            except ServiceException as exc:
                # Non-fatal — log and continue
                logger.warning(
                    "Cloudinary deletion failed for student %s: %s — "
                    "proceeding with DB deletion.",
                    student_id,
                    exc.message,
                )
        else:
            logger.warning(
                "No cloudinary_public_id stored for student %s — "
                "skipping Cloudinary deletion.",
                student_id,
            )

        # Hard-delete from MongoDB
        deleted = await self._repo.delete_by_id(student_id)
        if not deleted:
            raise ServiceException(
                f"Failed to delete student '{student_id}' from the database."
            )

        logger.info("Student hard-deleted — id: %s", student_id)
        return True


# =============================================================================
# Module-level singleton
# =============================================================================
student_service = StudentService()

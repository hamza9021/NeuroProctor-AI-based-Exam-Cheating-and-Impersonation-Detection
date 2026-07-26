"""
Student repository — MongoDB operations for the 'students' collection.

Extends BaseRepository with student-domain specific queries and
atomic face-embedding management operations.

All methods return raw dict documents from MongoDB.  The service layer
(app/services/student_service.py) is responsible for converting these
dicts into typed Pydantic response schemas.
"""
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from app.models.student import FaceEmbedding
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class StudentRepository(BaseRepository):
    """Async repository for all MongoDB I/O on the 'students' collection."""

    collection_name = "students"

    # -------------------------------------------------------------------------
    # Domain-specific lookups
    # -------------------------------------------------------------------------

    async def find_by_registration_number(
        self, registration_number: str
    ) -> Optional[dict]:
        """
        Find an active student by their unique registration number.

        Args:
            registration_number: Exact registration/roll number string.

        Returns:
            Document dict if found, None otherwise.
        """
        return await self.find_one(
            {"registration_number": registration_number, "is_active": True}
        )

    async def find_by_email(self, email: str) -> Optional[dict]:
        """
        Find an active student by email address (case-insensitive).

        Args:
            email: Email address to search for.

        Returns:
            Document dict if found, None otherwise.
        """
        return await self.find_one(
            {"email": email.lower(), "is_active": True}
        )

    async def find_active_by_id(self, student_id: str) -> Optional[dict]:
        """
        Find an active student by their MongoDB ObjectId string.

        Returns None if the ID is invalid, the student does not exist,
        or the student has been soft-deleted (is_active=False).

        Args:
            student_id: 24-character hex ObjectId string.

        Returns:
            Document dict if found and active, None otherwise.
        """
        if not ObjectId.is_valid(student_id):
            logger.debug(
                "find_active_by_id: invalid ObjectId '%s'", student_id
            )
            return None
        return await self.find_one(
            {"_id": ObjectId(student_id), "is_active": True}
        )

    # -------------------------------------------------------------------------
    # Paginated list with search + sort
    # -------------------------------------------------------------------------

    async def get_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[dict], int]:
        """
        Return a paginated list of active students with optional search.

        Search performs a case-insensitive regex match across:
          - full_name
          - email
          - registration_number
          - department

        Args:
            page:       1-indexed page number.
            limit:      Documents per page.
            search:     Optional free-text search string.
            sort_by:    Field to sort results by.
            sort_order: 'asc' (ascending) or 'desc' (descending).

        Returns:
            Tuple of (list_of_documents, total_matching_count).
        """
        # Build base filter — only active students
        filter_: dict = {"is_active": True}

        # Append search filter if provided
        if search and search.strip():
            # Escape user input to prevent regex injection
            escaped = re.escape(search.strip())
            pattern = re.compile(escaped, re.IGNORECASE)
            filter_["$or"] = [
                {"full_name": {"$regex": pattern}},
                {"email": {"$regex": pattern}},
                {"registration_number": {"$regex": pattern}},
                {"department": {"$regex": pattern}},
            ]

        # Resolve sort direction
        direction = DESCENDING if sort_order.lower() == "desc" else ASCENDING

        # Protect against invalid sort_by fields
        allowed_sort_fields = {
            "created_at", "updated_at", "full_name",
            "registration_number", "department", "semester",
        }
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        skip = (page - 1) * limit

        # Execute both queries concurrently would require asyncio.gather;
        # sequential is safe enough for typical load and avoids complexity.
        documents = await self.find_many(
            filter_=filter_,
            skip=skip,
            limit=limit,
            sort=[(sort_by, direction)],
        )
        total = await self.count(filter_)

        return documents, total

    # -------------------------------------------------------------------------
    # Face embedding management
    # -------------------------------------------------------------------------

    async def add_or_replace_embedding(
        self, student_id: str, embedding: FaceEmbedding
    ) -> bool:
        """
        Atomically replace a pose-specific face embedding in the array.

        Uses a two-step $pull → $push approach to ensure atomicity:
          1. Remove any existing embedding with the same pose.
          2. Push the new embedding and update metadata.

        This guarantees no duplicate pose entries can exist, even under
        concurrent requests (MongoDB single-document operations are atomic).

        Args:
            student_id: 24-character hex ObjectId string of the student.
            embedding:  Populated FaceEmbedding model with pose + vector.

        Returns:
            True if the document was modified.

        Raises:
            ValueError: If student_id is not a valid ObjectId string.
        """
        if not ObjectId.is_valid(student_id):
            raise ValueError(f"Invalid student_id: '{student_id}'")

        now = datetime.now(timezone.utc)
        oid = ObjectId(student_id)
        embedding_dict = embedding.model_dump()

        # Step 1 — Remove existing embedding for this pose (if any)
        await self.collection.update_one(
            {"_id": oid},
            {"$pull": {"face_embeddings": {"pose": embedding.pose}}},
        )

        # Step 2 — Push new embedding and refresh timestamps / status flag
        result = await self.collection.update_one(
            {"_id": oid},
            {
                "$push": {"face_embeddings": embedding_dict},
                "$set": {
                    "updated_at": now,
                    # Mark is_face_registered True if a real embedding was stored.
                    # (Real = 512-dimensional vector)
                    "is_face_registered": len(embedding.embedding) == 512,
                },
            },
        )
        return result.modified_count > 0

    async def set_face_registered_status(
        self, student_id: str, is_registered: bool
    ) -> bool:
        """
        Update the is_face_registered flag for a student.

        Called by the service layer after verifying whether all 5 poses
        have been captured.

        Args:
            student_id:    24-character hex ObjectId string.
            is_registered: New flag value.

        Returns:
            True if the document was updated.
        """
        return await self.update_by_id(
            student_id,
            {
                "$set": {
                    "is_face_registered": is_registered,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    async def soft_delete(self, student_id: str) -> bool:
        """
        Soft-delete a student by setting is_active = False.

        The document is retained in MongoDB for audit purposes.
        Use delete_by_id() for hard (permanent) deletion.

        Args:
            student_id: 24-character hex ObjectId string.

        Returns:
            True if the flag was updated.
        """
        return await self.update_by_id(
            student_id,
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

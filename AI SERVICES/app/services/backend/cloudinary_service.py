"""
Cloudinary service — async image upload and deletion.

Design decisions:
  1. ASYNC WRAPPERS — The Cloudinary Python SDK is synchronous.  All SDK
     calls are wrapped in asyncio.get_event_loop().run_in_executor(None, ...)
     so they run in a thread-pool and never block the async event loop.

  2. NO PER-CALL CONFIGURATION — The SDK is configured once at startup via
     app/config/cloudinary_config.py.  Every call here inherits that config.

  3. PUBLIC ID STRATEGY — Images are stored under a structured path:
       neuroproctor/students/profiles/{registration_slug}
     This makes Cloudinary's media library organised and allows targeted
     folder-level operations in the future.

  4. SECURE=True — All returned URLs use HTTPS (configured globally).

  5. QUALITY AUTO — Cloudinary's auto-quality transcoding reduces storage
     costs while maintaining visual fidelity.

Public API:
    cloudinary_service.upload_image(file_bytes, subfolder, public_id) → dict
    cloudinary_service.delete_image(public_id) → bool
    CloudinaryService.extract_public_id(url) → str  (static)
"""
import asyncio
import logging
import uuid
from typing import Optional

import cloudinary
import cloudinary.uploader

from app.config.settings import settings
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)


class CloudinaryService:
    """
    Async-compatible wrapper around the Cloudinary Python SDK.

    Use the module-level `cloudinary_service` singleton.
    """

    def __init__(self) -> None:
        # Base folder for all student images
        self._base_folder: str = settings.CLOUDINARY_STUDENT_FOLDER

    # =========================================================================
    # Upload
    # =========================================================================

    async def upload_image(
        self,
        file_bytes: bytes,
        subfolder: str = "",
        public_id: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Upload raw image bytes to Cloudinary.

        Args:
            file_bytes: Raw bytes of the JPEG/PNG image.
            subfolder:  Optional subfolder appended to the base folder path.
                        Example: "profiles" → "neuroproctor/students/profiles"
            public_id:  Optional Cloudinary public_id.  If None, a UUID-based
                        ID is generated automatically.

        Returns:
            Dict with:
                'url'       : Cloudinary HTTPS URL of the uploaded image.
                'public_id' : Cloudinary public_id for future operations.

        Raises:
            ServiceException: If the Cloudinary API call fails for any reason.
        """
        # Build the full folder path
        folder = (
            f"{self._base_folder}/{subfolder}".rstrip("/")
            if subfolder
            else self._base_folder
        )

        # Generate a public_id if not provided
        if not public_id:
            public_id = f"{folder}/{uuid.uuid4().hex}"

        logger.info(
            "Uploading image to Cloudinary — folder: '%s', public_id: '%s'",
            folder,
            public_id,
        )

        loop = asyncio.get_event_loop()
        try:
            result: dict = await loop.run_in_executor(
                None,
                lambda: cloudinary.uploader.upload(
                    file_bytes,
                    public_id=public_id,
                    resource_type="image",
                    overwrite=True,         # Replace if same public_id exists
                    quality="auto:best",    # Intelligent quality compression
                    fetch_format="auto",    # Serve WebP to supporting browsers
                ),
            )
        except Exception as exc:
            logger.exception("Cloudinary upload failed: %s", exc)
            raise ServiceException(
                "Failed to upload the profile image to Cloudinary. "
                "Please try again.",
                errors=[str(exc)],
            ) from exc

        secure_url: str = result["secure_url"]
        returned_public_id: str = result["public_id"]

        logger.info(
            "Cloudinary upload successful — public_id: '%s', url: '%s'",
            returned_public_id,
            secure_url,
        )
        return {
            "url": secure_url,
            "public_id": returned_public_id,
        }

    # =========================================================================
    # Delete
    # =========================================================================

    async def delete_image(self, public_id: str) -> bool:
        """
        Delete a Cloudinary image by its public_id.

        Args:
            public_id: The Cloudinary public_id of the image to remove.
                       This is the value stored in student.cloudinary_public_id.

        Returns:
            True  — image was deleted successfully.
            False — image was not found (already deleted or wrong public_id).

        Raises:
            ServiceException: On unexpected Cloudinary API errors.
        """
        if not public_id or not public_id.strip():
            logger.warning(
                "delete_image called with empty public_id — nothing to delete."
            )
            return False

        logger.info("Deleting Cloudinary image — public_id: '%s'", public_id)

        loop = asyncio.get_event_loop()
        try:
            result: dict = await loop.run_in_executor(
                None,
                lambda: cloudinary.uploader.destroy(
                    public_id, resource_type="image"
                ),
            )
        except Exception as exc:
            logger.exception(
                "Cloudinary delete failed for public_id '%s': %s", public_id, exc
            )
            raise ServiceException(
                "Failed to remove the profile image from Cloudinary.",
                errors=[str(exc)],
            ) from exc

        outcome = result.get("result", "")
        if outcome == "ok":
            logger.info(
                "Cloudinary image deleted — public_id: '%s'", public_id
            )
            return True

        logger.warning(
            "Cloudinary delete returned unexpected result for '%s': %s",
            public_id,
            result,
        )
        return False

    # =========================================================================
    # Static utilities
    # =========================================================================

    @staticmethod
    def extract_public_id(cloudinary_url: str) -> str:
        """
        Extract the Cloudinary public_id from a full secure URL.

        Example:
            Input  : https://res.cloudinary.com/demo/image/upload/v1234/folder/img.jpg
            Output : folder/img

        Note:
            - The version segment (v<digits>/) is stripped.
            - The file extension is stripped.

        Args:
            cloudinary_url: Full Cloudinary HTTPS image URL.

        Returns:
            The public_id string (without extension).
            Falls back to returning the original URL if parsing fails.
        """
        try:
            # Everything after '/upload/' is the versioned path
            _, path = cloudinary_url.split("/upload/", 1)
            parts = path.split("/")

            # Drop the version segment (e.g. 'v1627384920')
            if parts and parts[0].startswith("v") and parts[0][1:].isdigit():
                parts = parts[1:]

            # Remove file extension from the last path segment
            if parts:
                base, _, _ = parts[-1].rpartition(".")
                parts[-1] = base if base else parts[-1]

            return "/".join(parts)
        except (ValueError, IndexError, AttributeError):
            logger.warning(
                "extract_public_id: could not parse URL '%s'", cloudinary_url
            )
            return cloudinary_url


# =============================================================================
# Module-level singleton
# =============================================================================
cloudinary_service = CloudinaryService()

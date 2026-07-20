"""
Cloudinary SDK initialisation.

The Cloudinary SDK uses a global configuration object.  This module
configures it once at application startup using credentials from the
application settings.

After init_cloudinary() is called, all cloudinary.uploader and
cloudinary.api calls throughout the application will automatically
use these credentials — no per-call configuration is required.
"""
import logging

import cloudinary

from app.config.settings import settings

logger = logging.getLogger(__name__)


def init_cloudinary() -> None:
    """
    Configure the Cloudinary Python SDK with application credentials.

    Called once inside the FastAPI lifespan startup block.
    Safe to call multiple times (subsequent calls simply overwrite the config).

    The `secure=True` flag ensures all generated asset URLs use HTTPS,
    which is required when storing URLs in MongoDB for frontend consumption.
    """
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,   # Always return https:// URLs
    )
    logger.info(
        "Cloudinary SDK configured — cloud_name: '%s'",
        settings.CLOUDINARY_CLOUD_NAME,
    )

"""
Root endpoint.

Provides basic service information at the root URL.
"""
from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter()


@router.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        JSON response with basic service information
    """
    return {
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/api/docs",
        "health_url": "/api/v1/health",
    }

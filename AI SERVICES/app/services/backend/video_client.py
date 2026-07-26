"""
Video analysis client for communicating with the Express backend.

This module provides a client for interacting with video analysis endpoints
in the main Express backend API.
"""
import logging
from typing import Optional

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class VideoAnalysisClient:
    """
    Client for video analysis backend operations.

    This client handles communication with the Express backend's video analysis
    service for creating and retrieving video analysis records.
    """

    def __init__(self, base_url: str = None, timeout: int = 30):
        """
        Initialize the video analysis client.

        Args:
            base_url: Base URL of the Express backend API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.EXPRESS_BACKEND_URL
        self.timeout = timeout
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize the client."""
        self.is_initialized = True
        logger.info("Video analysis client initialized with base URL: %s", self.base_url)

    async def create_video_analysis(
        self,
        session_id: str,
        exam_id: str,
        invigilator_id: str,
        original_video: str,
        processed_video: str,
        processing_time: float,
        access_token: str,
    ) -> Optional[dict]:
        """
        Create a video analysis record via Express backend.

        Args:
            session_id: Exam session ID
            exam_id: Exam ID
            invigilator_id: Invigilator user ID
            original_video: Cloudinary URL for original video
            processed_video: Cloudinary URL for processed video
            processing_time: Processing time in seconds
            access_token: JWT access token for authentication

        Returns:
            Created video analysis data or None if failed
        """
        if not self.is_initialized:
            logger.warning("Video analysis client not initialized")
            return None

        url = f"{self.base_url}/api/v1/videoAnalysis"
        headers = {
            "Content-Type": "application/json",
        }
        
        # Only add cookie if token is present
        if access_token:
            headers["Cookie"] = f"accessToken={access_token}"
            logger.info("Sending request with access token (length: %d)", len(access_token))
        else:
            logger.warning("No access token provided for Express backend request")

        payload = {
            "sessionId": session_id,
            "examId": exam_id,
            "invigilatorId": invigilator_id,
            "originalVideo": original_video,
            "processedVideo": processed_video,
            "processingTime": processing_time,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info("Video analysis created successfully: %s", data.get("data", {}).get("_id"))
                return data.get("data")

        except httpx.HTTPError as e:
            logger.error("Failed to create video analysis: %s", str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error creating video analysis: %s", str(e))
            return None

    async def get_video_analysis_by_session(
        self,
        session_id: str,
        access_token: str,
    ) -> Optional[dict]:
        """
        Get video analysis by session ID.

        Args:
            session_id: Exam session ID
            access_token: JWT access token for authentication

        Returns:
            Video analysis data or None if not found
        """
        if not self.is_initialized:
            logger.warning("Video analysis client not initialized")
            return None

        url = f"{self.base_url}/api/v1/videoAnalysis/session/{session_id}"
        headers = {
            "Cookie": f"accessToken={access_token}",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("data")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info("Video analysis not found for session: %s", session_id)
                return None
            logger.error("Failed to get video analysis: %s", str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error getting video analysis: %s", str(e))
            return None

    def is_client_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self.is_initialized


# Module-level singleton
video_analysis_client = VideoAnalysisClient()

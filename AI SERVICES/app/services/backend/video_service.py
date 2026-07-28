"""
Video service — business logic orchestrator for video processing.

This service coordinates:
  1. Video validation (type, size)
  2. Temporary file storage
  3. AI pipeline processing (cheating detection)
  4. Cloudinary video upload (original and processed)
  5. MongoDB persistence via Express backend API
  6. Temporary file cleanup

Error handling contract:
  All methods raise typed AppException subclasses (from app/core/exceptions.py).
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config.settings import settings
from app.core.exceptions import (
    NotFoundException,
    ServiceException,
    ValidationException,
)
from app.services.backend.cloudinary_service import cloudinary_service
from app.services.backend.video_client import video_analysis_client
from app.services.ai.detectors.yolo.config import YOLOConfig
from app.services.ai.processors.video_processor import VideoProcessor
from app.services.ai.monitoring import PipelineLogger

logger = logging.getLogger(__name__)


class VideoService:
    """
    High-level video processing service.

    Orchestrates the full video processing lifecycle:
      - Video validation and temporary storage
      - AI pipeline processing
      - Cloudinary upload (original + processed)
      - VideoAnalysis record creation via Express backend
      - Temporary file cleanup
    """

    def __init__(self) -> None:
        self._temp_dir = Path(settings.TEMP_DIR)
        self._annotated_dir = Path(settings.ANNOTATED_VIDEOS_DIR)

    # =========================================================================
    # Public API
    # =========================================================================

    async def process_video(
        self,
        video_file: UploadFile,
        session_id: str,
        exam_id: str,
        invigilator_id: str,
        access_token: str,
        event_emitter: Optional["EventEmitter"] = None,
    ) -> dict:
        """
        Process a video file for cheating detection.

        Args:
            video_file: Uploaded video file
            session_id: Exam session ID
            exam_id: Exam ID
            invigilator_id: Invigilator user ID
            access_token: JWT access token for authentication
            event_emitter: Optional event emitter for real-time updates

        Returns:
            dict: VideoAnalysis record with Cloudinary URLs

        Raises:
            ValidationException: On video format or size violation
            ServiceException: On processing or upload failure
        """
        # Validate video
        video_bytes = await self._validate_video(video_file)
        if event_emitter:
            await event_emitter.emit_info("Video validated successfully")

        # Save temporarily
        temp_path = await self._save_temp_video(video_bytes, video_file.filename)
        if event_emitter:
            await event_emitter.emit_info("Temporary file created")

        try:
            # Process through AI pipeline
            if event_emitter:
                await event_emitter.emit_stage_started("AI Pipeline")
            processed_path = await self._process_with_ai_pipeline(temp_path, event_emitter)
            if event_emitter:
                await event_emitter.emit_stage_completed("AI Pipeline")

            # Upload to Cloudinary
            if event_emitter:
                await event_emitter.emit_info("Uploading original video to Cloudinary")
            original_url = await self._upload_to_cloudinary(
                temp_path,
                folder="videos/original",
                public_id=f"session_{session_id}_original",
            )
            if event_emitter:
                await event_emitter.emit_info("Original video uploaded")

            if event_emitter:
                await event_emitter.emit_info("Uploading processed video to Cloudinary")
            processed_url = await self._upload_to_cloudinary(
                processed_path,
                folder="videos/processed",
                public_id=f"session_{session_id}_processed",
            )
            if event_emitter:
                await event_emitter.emit_info("Processed video uploaded")

            # Create VideoAnalysis record via Express backend
            if event_emitter:
                await event_emitter.emit_info("Creating VideoAnalysis record")
            video_analysis = await self._create_video_analysis(
                session_id=session_id,
                exam_id=exam_id,
                invigilator_id=invigilator_id,
                original_video=original_url,
                processed_video=processed_url,
                access_token=access_token,
            )

            return video_analysis

        finally:
            # Cleanup temporary files
            await self._cleanup_temp_files(temp_path, processed_path if 'processed_path' in locals() else None)

    # =========================================================================
    # Private helpers
    # =========================================================================

    async def _validate_video(self, file: UploadFile) -> bytes:
        """
        Read and validate an uploaded video file.

        Checks:
          - Content-Type is in ALLOWED_VIDEO_TYPES (mp4, avi, mov)
          - File size does not exceed MAX_VIDEO_SIZE_MB

        Args:
            file: FastAPI UploadFile object

        Returns:
            Raw file bytes if all checks pass

        Raises:
            ValidationException: On MIME type or size violation
        """
        content_type = (file.content_type or "").lower().strip()

        allowed_types = [
            "video/mp4",
            "video/avi",
            "video/quicktime",
            "video/x-msvideo",
        ]

        if content_type not in allowed_types:
            raise ValidationException(
                f"Unsupported video format '{content_type}'. "
                f"Accepted formats: MP4, AVI, MOV.",
            )

        file_bytes = await file.read()
        max_bytes = 500 * 1_024 * 1_024  # 500 MB max

        if len(file_bytes) > max_bytes:
            size_mb = len(file_bytes) / 1_048_576
            raise ValidationException(
                f"Video size ({size_mb:.2f} MB) exceeds the maximum "
                f"allowed size of 500 MB.",
            )

        return file_bytes

    async def _save_temp_video(self, file_bytes: bytes, filename: Optional[str]) -> Path:
        """
        Save video bytes to a temporary file.

        Args:
            file_bytes: Raw video bytes
            filename: Original filename (for extension)

        Returns:
            Path to temporary file
        """
        # Generate unique filename
        ext = Path(filename).suffix if filename else ".mp4"
        temp_filename = f"{uuid.uuid4().hex}{ext}"
        temp_path = self._temp_dir / temp_filename

        # Write file
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, temp_path.write_bytes, file_bytes)

        logger.info("Saved temporary video to: %s", temp_path)
        return temp_path

    async def _process_with_ai_pipeline(
        self,
        video_path: Path,
        event_emitter: Optional["EventEmitter"] = None,
    ) -> Path:
        """
        Process video through the AI cheating detection pipeline.

        This runs YOLO object detection on each frame and generates
        an annotated video with bounding boxes.

        Args:
            video_path: Path to input video
            event_emitter: Optional event emitter for real-time updates

        Returns:
            Path to processed (annotated) video
        """
        logger.info("Processing video through AI pipeline: %s", video_path)
        if event_emitter:
            await event_emitter.emit_info("Processing video through AI pipeline")

        # Initialize YOLO configuration from environment variables
        yolo_config = YOLOConfig(
            model_path=settings.YOLO_MODEL,
            confidence=settings.YOLO_CONFIDENCE,
            iou=settings.YOLO_IOU,
            image_size=settings.YOLO_IMAGE_SIZE,
            device=settings.YOLO_DEVICE,
        )

        # Initialize DeepSORT configuration
        from app.services.ai.trackers.deepsort.config import DeepSORTConfig
        deepsort_config = DeepSORTConfig(
            device=settings.YOLO_DEVICE,
        )

        # Initialize Pose configuration
        from app.services.ai.analyzers.pose.config import YoloPoseConfig
        pose_config = YoloPoseConfig(
            device=settings.YOLO_DEVICE,
        )

        # Initialize pipeline logger
        pipeline_logger = PipelineLogger(session_id="video-processing")

        # Create video processor with YOLO, DeepSORT, and Pose configs
        processor = VideoProcessor(yolo_config, deepsort_config, pose_config, pipeline_logger)

        # Generate output path
        output_path = self._annotated_dir / f"processed_{video_path.name}"

        # Process video (async call)
        stats = await processor.process_video(video_path, output_path)

        logger.info(f"AI pipeline completed. Output: {output_path}")
        logger.info(f"Detection statistics: {stats}")

        if event_emitter:
            await event_emitter.emit_info(f"AI pipeline completed. Detected: {stats['detections']}")

        return output_path

    async def _upload_to_cloudinary(
        self,
        file_path: Path,
        folder: str,
        public_id: str,
    ) -> str:
        """
        Upload a video file to Cloudinary.

        Args:
            file_path: Path to video file
            folder: Cloudinary folder
            public_id: Cloudinary public ID

        Returns:
            Cloudinary URL

        Raises:
            ServiceException: If upload fails
        """
        logger.info(
            "Uploading video to Cloudinary - folder: %s, public_id: %s",
            folder,
            public_id,
        )

        # Read file bytes
        loop = asyncio.get_event_loop()
        file_bytes = await loop.run_in_executor(None, file_path.read_bytes)

        # Upload using cloudinary service
        # Note: We need to add video upload support to cloudinary_service
        # For now, we'll use a direct call
        try:
            result = await self._upload_video_to_cloudinary(
                file_bytes,
                folder=folder,
                public_id=public_id,
            )
            return result["url"]
        except Exception as e:
            logger.error("Cloudinary upload failed: %s", str(e))
            raise ServiceException(f"Failed to upload video to Cloudinary: {str(e)}")

    async def _upload_video_to_cloudinary(
        self,
        file_bytes: bytes,
        folder: str,
        public_id: str,
    ) -> dict:
        """
        Upload video bytes to Cloudinary (async wrapper).

        Args:
            file_bytes: Raw video bytes
            folder: Cloudinary folder
            public_id: Cloudinary public ID

        Returns:
            Dict with 'url' and 'public_id'
        """
        import cloudinary.uploader

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: cloudinary.uploader.upload(
                file_bytes,
                resource_type="video",
                folder=folder,
                public_id=public_id,
                overwrite=True,
            ),
        )

        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
        }

    async def _create_video_analysis(
        self,
        session_id: str,
        exam_id: str,
        invigilator_id: str,
        original_video: str,
        processed_video: str,
        access_token: str,
    ) -> dict:
        """
        Create VideoAnalysis record via Express backend API.

        Args:
            session_id: Exam session ID
            exam_id: Exam ID
            invigilator_id: Invigilator user ID
            original_video: Cloudinary URL for original video
            processed_video: Cloudinary URL for processed video
            access_token: JWT access token for authentication

        Returns:
            Created VideoAnalysis record

        Raises:
            ServiceException: If API call fails
        """
        logger.info("Creating VideoAnalysis record for session: %s", session_id)

        processing_time = 0  # This would be calculated from actual processing time

        video_analysis = await video_analysis_client.create_video_analysis(
            session_id=session_id,
            exam_id=exam_id,
            invigilator_id=invigilator_id,
            original_video=original_video,
            processed_video=processed_video,
            processing_time=processing_time,
            access_token=access_token,
        )

        if not video_analysis:
            raise ServiceException("Failed to create VideoAnalysis record in backend")

        return video_analysis

    async def _cleanup_temp_files(
        self,
        *paths: Optional[Path],
    ) -> None:
        """
        Delete temporary files.

        Args:
            *paths: Paths to delete
        """
        for path in paths:
            if path and path.exists():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, path.unlink)
                logger.info("Deleted temporary file: %s", path)


# Module-level singleton
video_service = VideoService()

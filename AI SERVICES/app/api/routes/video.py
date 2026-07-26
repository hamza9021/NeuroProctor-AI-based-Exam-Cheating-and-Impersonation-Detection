"""
Video API routes — AI-powered video processing for exam sessions.

Every endpoint requires the 'accessToken' HttpOnly cookie issued by the
Express backend. Only users with the 'invigilator' role may call these endpoints.

Routes:
    POST /api/v1/video/process — Upload and process video for cheating detection

Auth errors:
    401 — Cookie missing / JWT expired / JWT invalid
    403 — Role not in ["invigilator"]

All responses follow the standard envelope:
    Success: { "success": true,  "message": "...", "data": {...} }
    Error:   { "success": false, "message": "...", "errors": [...] }
"""
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status

from app.api.dependencies import require_roles
from app.core.responses import success_response
from app.schemas.video import VideoProcessRequest, TokenPayload
from app.services.ai.monitoring import EventEmitter, PipelineLogger
from app.services.backend.video_service import video_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/video",
    tags=["Video Processing"],
)

# ---------------------------------------------------------------------------
# Reusable role guard — only invigilators can process videos
# ---------------------------------------------------------------------------
_protected = require_roles(["invigilator"])


# =============================================================================
# POST /video/process — Upload and process video for cheating detection
# =============================================================================

@router.post(
    "/process",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Process video for cheating detection",
    description="""
    Upload a video file for AI-powered cheating detection.
    
    The video will be:
    1. Validated for format and size
    2. Processed through the AI pipeline
    3. Uploaded to Cloudinary (original and processed versions)
    4. A VideoAnalysis record will be created/updated
    
    Returns Cloudinary URLs for both original and processed videos.
    """,
)
async def process_video(
    request: Request,
    video: UploadFile = File(..., description="Video file to process (MP4, AVI, MOV)"),
    sessionId: str = Form(..., description="Exam session ID"),
    examId: str = Form(..., description="Exam ID"),
    token_payload: TokenPayload = Depends(_protected),
) -> dict:
    """
    Process a video file for cheating detection.
    
    Args:
        request: FastAPI request object (for cookie extraction)
        video: Uploaded video file
        sessionId: Exam session ID
        examId: Exam ID
        token_payload: JWT token payload (injected by dependency)
    
    Returns:
        dict: Success response with video analysis data including Cloudinary URLs
    """
    # Extract access token from cookies
    access_token = request.cookies.get("accessToken")
    
    # Initialize logger and emitter for this session
    pipeline_logger = PipelineLogger(session_id=sessionId)
    event_emitter = EventEmitter(pipeline_logger)
    
    logger.info(
        "Video processing request - Session: %s, Exam: %s, User: %s, Token present: %s",
        sessionId,
        examId,
        token_payload.user_id,
        bool(access_token),
    )
    
    # Emit video received event
    logger.info("Emitting video_received event for session: %s", sessionId)
    await event_emitter.emit_info("Video received", {"session_id": sessionId, "exam_id": examId})
    
    start_time = time.time()
    
    try:
        # Emit video validated event
        await event_emitter.emit_info("Video validated")
        
        # Process video through AI pipeline
        result = await video_service.process_video(
            video_file=video,
            session_id=sessionId,
            exam_id=examId,
            invigilator_id=token_payload.user_id,
            access_token=access_token,
            event_emitter=event_emitter,
        )
        
        processing_time = time.time() - start_time
        logger.info(
            "Video processed successfully - Session: %s, Time: %.2fs",
            sessionId,
            processing_time,
        )
        
        # Emit processing completed event
        await event_emitter.emit_info("Processing completed", {"processing_time": processing_time})
        
        return success_response(
            message="Video processed successfully",
            data={
                "videoAnalysis": result,
                "processingTime": processing_time,
            },
        )
        
    except Exception as e:
        logger.error(
            "Video processing failed - Session: %s, Error: %s",
            sessionId,
            str(e),
            exc_info=True,
        )
        # Emit pipeline failed event
        await event_emitter.emit_error(f"Processing failed: {str(e)}")
        raise

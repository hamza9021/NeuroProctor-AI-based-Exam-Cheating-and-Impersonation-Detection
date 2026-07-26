"""
Video processing schemas for FastAPI.
"""
from pydantic import BaseModel


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    user_id: str
    role: str
    exp: int


class VideoProcessRequest(BaseModel):
    """Request schema for video processing."""
    sessionId: str
    examId: str


class VideoAnalysisResponse(BaseModel):
    """Response schema for video analysis."""
    _id: str
    sessionId: str
    examId: str
    invigilatorId: str
    originalVideo: str
    processedVideo: str
    status: str
    processingTime: float
    uploadedAt: str
    completedAt: str

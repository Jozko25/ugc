"""Data models for UGC video generation system."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    """Video generation job status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ScriptMetadata(BaseModel):
    """Metadata for generated UGC script."""
    duration: int = Field(..., description="Target video duration in seconds")
    tone: str = Field(..., description="Tone of the video (e.g., calm, energetic, empathetic)")
    hashtags: List[str] = Field(..., description="Suggested hashtags for social media")
    target_audience: str = Field(..., description="Primary target audience")


class GeneratedScript(BaseModel):
    """Generated UGC script output."""
    script: str = Field(..., description="Natural UGC-style script")
    sora_prompt: str = Field(..., description="Sora 2 video generation prompt")
    metadata: ScriptMetadata


class VideoGenerationRequest(BaseModel):
    """Request for video generation."""
    topic: str = Field(..., description="Topic for the UGC video")
    duration: Optional[int] = Field(default=None, description="Video duration in seconds")


class VideoResult(BaseModel):
    """Final video generation result."""
    job_id: str
    topic: str
    script: str
    sora_prompt: str
    video_url: str
    metadata: ScriptMetadata
    status: VideoStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class VideoJobStatus(BaseModel):
    """Status of a video generation job."""
    job_id: str
    status: VideoStatus
    video_url: Optional[str] = None
    progress: Optional[int] = Field(default=None, description="Progress percentage (0-100)")
    error: Optional[str] = None


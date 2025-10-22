"""Video generation service using OpenAI Sora 2 API."""

import logging
import time
from typing import Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .models import VideoStatus, VideoJobStatus

logger = logging.getLogger(__name__)


class VideoService:
    """Service for generating videos using Sora 2 API."""
    
    def __init__(self):
        """Initialize OpenAI client for Sora 2."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model_video
        logger.info(f"Initialized video service with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_video(self, prompt: str, duration: int, size: str = None) -> str:
        """
        Initiate video generation with Sora 2.
        
        Args:
            prompt: Detailed video generation prompt
            duration: Video duration in seconds (must be a string in API call)
            size: Video resolution (e.g., "1280x720", "1920x1080")
            
        Returns:
            Job ID for tracking the video generation
        """
        if size is None:
            size = settings.default_video_size
            
        logger.info(f"Initiating video generation: duration={duration}s, size={size}")
        logger.debug(f"Sora prompt: {prompt[:200]}...")
        
        try:
            # Official Sora 2 API call
            response = self.client.videos.create(
                model=self.model,
                prompt=prompt,
                seconds=str(duration),  # API expects string
                size=size
            )
            
            job_id = response.id
            logger.info(f"Video generation job created: {job_id}, status: {response.status}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to initiate video generation: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    def check_video_status(self, job_id: str) -> VideoJobStatus:
        """
        Check the status of a video generation job.
        
        Args:
            job_id: The video generation job ID
            
        Returns:
            VideoJobStatus object with current status
        """
        try:
            # Official API: openai.videos.retrieve(video_id)
            response = self.client.videos.retrieve(job_id)
            
            # Map API status to our enum
            status_mapping = {
                "queued": VideoStatus.QUEUED,
                "in_progress": VideoStatus.IN_PROGRESS,
                "completed": VideoStatus.COMPLETED,
                "failed": VideoStatus.FAILED
            }
            
            status = status_mapping.get(response.status.lower(), VideoStatus.QUEUED)
            
            # For completed videos, we'll need to download content separately
            # The API doesn't return a direct URL, you must call downloadContent()
            video_url = None
            if status == VideoStatus.COMPLETED:
                video_url = f"completed:{job_id}"  # Marker that we need to download
            
            job_status = VideoJobStatus(
                job_id=job_id,
                status=status,
                video_url=video_url,
                progress=getattr(response, 'progress', None),
                error=getattr(response, 'error', None) if hasattr(response, 'error') else None
            )
            
            logger.debug(f"Job {job_id} status: {status}, progress: {job_status.progress}%")
            
            return job_status
            
        except Exception as e:
            logger.error(f"Failed to check video status for job {job_id}: {e}")
            raise
    
    def poll_video_status(self, job_id: str) -> VideoJobStatus:
        """
        Poll video generation status until completion or failure.
        
        Args:
            job_id: The video generation job ID
            
        Returns:
            Final VideoJobStatus
            
        Raises:
            TimeoutError: If max poll attempts exceeded
            RuntimeError: If video generation failed
        """
        logger.info(f"Starting to poll job {job_id}")
        
        attempts = 0
        max_attempts = settings.max_poll_attempts
        poll_interval = settings.poll_interval_seconds
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                status = self.check_video_status(job_id)
                
                if status.status == VideoStatus.COMPLETED:
                    logger.info(f"Video generation completed for job {job_id}")
                    return status
                
                elif status.status == VideoStatus.FAILED:
                    error_msg = status.error or "Unknown error"
                    logger.error(f"Video generation failed for job {job_id}: {error_msg}")
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                
                # Still processing (queued or in_progress)
                progress_str = f"{status.progress}%" if status.progress else "N/A"
                logger.info(f"Job {job_id} status: {status.status.value} "
                          f"(attempt {attempts}/{max_attempts}), progress: {progress_str}")
                
                time.sleep(poll_interval)
                
            except RuntimeError:
                raise
            except Exception as e:
                logger.warning(f"Error polling status (attempt {attempts}): {e}")
                if attempts >= max_attempts:
                    raise
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Video generation timed out after {max_attempts} attempts")
    
    def download_video_content(self, job_id: str, output_path: str) -> None:
        """
        Download the completed video content to a file.
        
        Args:
            job_id: The video generation job ID
            output_path: Local file path to save the video
        """
        logger.info(f"Downloading video content for job {job_id}")
        
        try:
            # Official API: openai.videos.download_content(video_id)
            content = self.client.videos.download_content(job_id)
            
            # Write binary content directly to file
            with open(output_path, 'wb') as f:
                f.write(content.read())
            
            logger.info(f"Video downloaded to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to download video content: {e}", exc_info=True)
            raise


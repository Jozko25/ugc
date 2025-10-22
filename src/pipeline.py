"""Main pipeline orchestration for UGC video generation."""

import logging
from datetime import datetime
from typing import Optional

from .config import settings
from .models import VideoResult, VideoStatus, GeneratedScript
from .llm_service import LLMService
from .video_service import VideoService
from .storage_service import StorageService

logger = logging.getLogger(__name__)


class UGCVideoPipeline:
    """
    Main pipeline for generating UGC marketing videos.
    
    Orchestrates the full workflow:
    1. Generate script and video prompt via LLM
    2. Generate video via Sora 2
    3. Poll for completion
    4. Store result
    """
    
    def __init__(self):
        """Initialize all services."""
        self.llm_service = LLMService()
        self.video_service = VideoService()
        self.storage_service = StorageService()
        logger.info("UGC Video Pipeline initialized")
    
    def generate(
        self,
        topic: str,
        duration: Optional[int] = None,
        store_result: bool = True,
        download_video: bool = True
    ) -> VideoResult:
        """
        Generate a complete UGC video from topic to final result.
        
        Args:
            topic: The topic/feature to create content about
            duration: Target video duration in seconds
            store_result: Whether to store the result
            download_video: Whether to download the video file locally
            
        Returns:
            VideoResult with complete metadata and video URL
        """
        logger.info(f"Starting UGC video generation pipeline for topic: '{topic}'")
        
        start_time = datetime.utcnow()
        job_id = None
        
        try:
            # Step 1: Generate script and video prompt
            logger.info("Step 1/4: Generating script and video prompt...")
            script_data = self.llm_service.generate_script(topic, duration)
            
            logger.info(f"Script generated ({len(script_data.script)} chars)")
            logger.debug(f"Script: {script_data.script}")
            logger.debug(f"Sora prompt: {script_data.sora_prompt}")
            
            # Step 2: Initiate video generation
            logger.info("Step 2/4: Initiating video generation...")
            job_id = self.video_service.generate_video(
                prompt=script_data.sora_prompt,
                duration=script_data.metadata.duration,
                size=settings.default_video_size
            )
            
            logger.info(f"Video generation job created: {job_id}")
            
            # Step 3: Poll for completion
            logger.info("Step 3/4: Polling for video completion...")
            video_status = self.video_service.poll_video_status(job_id)
            
            if not video_status.video_url:
                raise RuntimeError("Video completed but no URL returned")
            
            logger.info(f"Video generation completed: {video_status.video_url}")
            
            # Step 4: Create result object
            logger.info("Step 4/4: Creating result object...")
            result = VideoResult(
                job_id=job_id,
                topic=topic,
                script=script_data.script,
                sora_prompt=script_data.sora_prompt,
                video_url=video_status.video_url,
                metadata=script_data.metadata,
                status=VideoStatus.COMPLETED,
                created_at=start_time,
                completed_at=datetime.utcnow()
            )
            
            # Store result if requested
            if store_result:
                storage_path = self.storage_service.store_result(
                    result, 
                    download_video,
                    video_service=self.video_service
                )
                logger.info(f"Result stored at: {storage_path}")
            
            logger.info(f"Pipeline completed successfully in "
                       f"{(result.completed_at - result.created_at).total_seconds():.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            
            # Create failed result
            result = VideoResult(
                job_id=job_id or "unknown",
                topic=topic,
                script="",
                sora_prompt="",
                video_url="",
                metadata={
                    "duration": duration or settings.default_video_duration,
                    "tone": "unknown",
                    "hashtags": [],
                    "target_audience": "unknown"
                },
                status=VideoStatus.FAILED,
                created_at=start_time,
                completed_at=datetime.utcnow(),
                error=str(e)
            )
            
            if store_result:
                try:
                    self.storage_service.store_result(
                        result, 
                        download_video=False,
                        video_service=self.video_service
                    )
                except:
                    pass
            
            raise


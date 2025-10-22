"""Storage service for saving video results and metadata."""

import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import httpx

from .config import settings
from .models import VideoResult

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing video results and metadata."""
    
    def __init__(self):
        """Initialize storage service based on configuration."""
        self.storage_type = settings.storage_type
        
        if self.storage_type == "local":
            self.storage_path = Path(settings.storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized local storage at: {self.storage_path}")
        
        elif self.storage_type == "s3":
            # S3 storage would be initialized here
            logger.info("Initialized S3 storage")
            # import boto3
            # self.s3_client = boto3.client('s3', ...)
    
    def _download_video(self, video_url: str, output_path: Path) -> None:
        """
        Download video from URL to local file.
        
        Args:
            video_url: URL of the video to download
            output_path: Local path to save the video
        """
        logger.info(f"Downloading video from {video_url}")
        
        with httpx.Client(timeout=300.0) as client:
            response = client.get(video_url)
            response.raise_for_status()
            
            output_path.write_bytes(response.content)
            
        logger.info(f"Video downloaded: {output_path}")
    
    def _save_local(self, result: VideoResult, download_video: bool = True, video_service = None) -> str:
        """
        Save result to local filesystem.
        
        Args:
            result: VideoResult to save
            download_video: Whether to download the actual video file
            video_service: VideoService instance for downloading (if needed)
            
        Returns:
            Path to saved metadata file
        """
        # Create subdirectory for this job
        job_dir = self.storage_path / result.job_id
        job_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata_path = job_dir / "metadata.json"
        metadata_path.write_text(result.model_dump_json(indent=2))
        
        # Download video if requested
        if download_video and result.video_url:
            video_path = job_dir / "video.mp4"
            try:
                # Check if we have a URL or need to download via API
                if result.video_url.startswith("completed:"):
                    # Extract job_id and use video service to download
                    if video_service:
                        video_service.download_video_content(result.job_id, str(video_path))
                    else:
                        logger.warning("Cannot download video: video_service not provided")
                else:
                    # Direct URL download
                    self._download_video(result.video_url, video_path)
                
                logger.info(f"Video saved locally: {video_path}")
            except Exception as e:
                logger.error(f"Failed to download video: {e}")
        
        logger.info(f"Metadata saved: {metadata_path}")
        return str(metadata_path)
    
    def _save_s3(self, result: VideoResult) -> str:
        """
        Save result to S3.
        
        Args:
            result: VideoResult to save
            
        Returns:
            S3 path
        """
        # Placeholder for S3 implementation
        # import boto3
        # s3_client = boto3.client('s3')
        # metadata_key = f"videos/{result.job_id}/metadata.json"
        # s3_client.put_object(
        #     Bucket=settings.aws_bucket_name,
        #     Key=metadata_key,
        #     Body=result.model_dump_json(indent=2),
        #     ContentType='application/json'
        # )
        
        logger.info(f"Would save to S3: videos/{result.job_id}/metadata.json")
        return f"s3://{settings.aws_bucket_name}/videos/{result.job_id}/metadata.json"
    
    def store_result(
        self,
        result: VideoResult,
        download_video: bool = True,
        video_service = None
    ) -> str:
        """
        Store video result and metadata.
        
        Args:
            result: VideoResult to store
            download_video: Whether to download the video file (local storage only)
            video_service: VideoService instance for downloading (if needed)
            
        Returns:
            Storage path/URL where result was saved
        """
        logger.info(f"Storing result for job {result.job_id}")
        
        try:
            if self.storage_type == "local":
                return self._save_local(result, download_video, video_service)
            elif self.storage_type == "s3":
                return self._save_s3(result)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"Failed to store result: {e}", exc_info=True)
            raise
    
    def load_result(self, job_id: str) -> Optional[VideoResult]:
        """
        Load a previously stored result.
        
        Args:
            job_id: Job ID to load
            
        Returns:
            VideoResult if found, None otherwise
        """
        try:
            if self.storage_type == "local":
                metadata_path = self.storage_path / job_id / "metadata.json"
                if metadata_path.exists():
                    data = json.loads(metadata_path.read_text())
                    return VideoResult(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load result for job {job_id}: {e}")
            return None


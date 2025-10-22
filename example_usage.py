#!/usr/bin/env python3
"""Example usage of the UGC video generation pipeline."""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.pipeline import UGCVideoPipeline
from src.config import settings


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Run example video generation."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Example topic: 3-minute breathing tool
    topic = "3-minute breathing tool"
    
    logger.info("="*80)
    logger.info("UGC VIDEO GENERATION - EXAMPLE USAGE")
    logger.info("="*80)
    logger.info(f"Topic: {topic}")
    logger.info(f"Model (Text): {settings.openai_model_text}")
    logger.info(f"Model (Video): {settings.openai_model_video}")
    logger.info(f"Default Duration: {settings.default_video_duration}s")
    logger.info(f"Video Size: {settings.default_video_size}")
    logger.info("="*80 + "\n")
    
    try:
        # Initialize pipeline
        pipeline = UGCVideoPipeline()
        
        # Generate video
        logger.info("Starting video generation...")
        result = pipeline.generate(
            topic=topic,
            duration=8,  # 8 seconds for quick example
            store_result=True,
            download_video=True
        )
        
        # Display results
        print("\n" + "="*80)
        print("GENERATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nJob ID: {result.job_id}")
        print(f"Topic: {result.topic}")
        print(f"Status: {result.status.value}")
        print(f"\nMetadata:")
        print(f"  Duration: {result.metadata.duration}s")
        print(f"  Tone: {result.metadata.tone}")
        print(f"  Target Audience: {result.metadata.target_audience}")
        print(f"  Hashtags: {', '.join(result.metadata.hashtags)}")
        print(f"\nGenerated Script:")
        print("-" * 80)
        print(result.script)
        print("-" * 80)
        print(f"\nSora 2 Prompt:")
        print("-" * 80)
        print(result.sora_prompt)
        print("-" * 80)
        print(f"\nVideo URL: {result.video_url}")
        print(f"Created: {result.created_at}")
        print(f"Completed: {result.completed_at}")
        print(f"Duration: {(result.completed_at - result.created_at).total_seconds():.1f}s")
        
        # Check for local file
        video_path = Path(settings.storage_path) / result.job_id / "video.mp4"
        if video_path.exists():
            print(f"\nLocal video file: {video_path}")
            print(f"File size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        print("="*80 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nError: {e}", exc_info=True)
        print(f"\nFailed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


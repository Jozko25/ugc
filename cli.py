#!/usr/bin/env python3
"""CLI tool for generating UGC videos."""

import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.pipeline import UGCVideoPipeline
from src.config import settings


def setup_logging(level: str = "INFO"):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ugc_pipeline.log')
        ]
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate UGC-style marketing videos using AI"
    )
    parser.add_argument(
        "topic",
        help="Topic for the video (e.g., 'breathing exercise', 'panic relief tool')"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help=f"Video duration in seconds (default: {settings.default_video_duration})"
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="Don't store the result to disk"
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Don't download the video file"
    )
    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize pipeline
        pipeline = UGCVideoPipeline()
        
        # Generate video
        result = pipeline.generate(
            topic=args.topic,
            duration=args.duration,
            store_result=not args.no_store,
            download_video=not args.no_download
        )
        
        # Print result
        print("\n" + "="*80)
        print("VIDEO GENERATION COMPLETED")
        print("="*80)
        print(f"\nJob ID: {result.job_id}")
        print(f"Topic: {result.topic}")
        print(f"Duration: {result.metadata.duration}s")
        print(f"Tone: {result.metadata.tone}")
        print(f"Target Audience: {result.metadata.target_audience}")
        print(f"\nHashtags: {', '.join(result.metadata.hashtags)}")
        print(f"\nScript:\n{result.script}")
        print(f"\nVideo URL: {result.video_url}")
        print(f"\nCompleted in: {(result.completed_at - result.created_at).total_seconds():.1f}s")
        print("="*80 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


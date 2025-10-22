#!/usr/bin/env python3
"""REST API for UGC video generation."""

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

from src.pipeline import UGCVideoPipeline
from src.models import VideoGenerationRequest, VideoResult, VideoStatus
from src.config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global pipeline instance
pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    global pipeline
    logger.info("Starting UGC Video API...")
    pipeline = UGCVideoPipeline()
    yield
    logger.info("Shutting down UGC Video API...")


app = FastAPI(
    title="UGC Video Generation API",
    description="Generate UGC-style marketing videos using AI",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "UGC Video Generation API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "generate_video": "/api/v1/videos",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_text": settings.openai_model_text,
        "model_video": settings.openai_model_video
    }


@app.post("/api/v1/videos", response_model=VideoResult)
async def generate_video(request: VideoGenerationRequest):
    """
    Generate a UGC-style marketing video.
    
    This endpoint initiates the full pipeline:
    1. Generate script via LLM
    2. Generate video via Sora 2
    3. Poll for completion
    4. Store result
    
    Note: This is a synchronous operation that may take several minutes.
    """
    logger.info(f"Received video generation request for topic: {request.topic}")
    
    try:
        result = pipeline.generate(
            topic=request.topic,
            duration=request.duration,
            store_result=True,
            download_video=True
        )
        
        return result
        
    except TimeoutError as e:
        logger.error(f"Video generation timeout: {e}")
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/videos/async", response_model=dict)
async def generate_video_async(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a UGC-style marketing video asynchronously.
    
    This endpoint starts the generation in the background and returns immediately.
    Use the job_id to check status later.
    
    Note: This is a simplified implementation. For production, use a proper
    task queue like Celery or RQ.
    """
    import uuid
    
    job_id = f"job_{uuid.uuid4().hex[:16]}"
    
    def generate_in_background():
        try:
            pipeline.generate(
                topic=request.topic,
                duration=request.duration,
                store_result=True,
                download_video=True
            )
        except Exception as e:
            logger.error(f"Background generation failed for job {job_id}: {e}")
    
    background_tasks.add_task(generate_in_background)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation started in background"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level.lower()
    )


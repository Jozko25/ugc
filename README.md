# UGC Video Generation Pipeline

Automated system for generating authentic user-generated-content (UGC) style marketing videos using OpenAI GPT-4o and Sora 2 APIs.

## Overview

This production-grade Python application creates UGC-style promotional videos for the **Wellbewing** anxiety & wellbeing app. It orchestrates:

1. **Script Generation** - GPT-4o creates natural, conversational UGC scripts
2. **Video Generation** - Sora 2 renders authentic smartphone-style video clips
3. **Status Polling** - Monitors job progress until completion
4. **Result Storage** - Saves videos and metadata locally or to S3

## Features

- ✅ Full OpenAI Sora 2 API integration (official endpoints)
- ✅ Intelligent script generation with GPT-4o
- ✅ Automatic polling with progress tracking
- ✅ Robust error handling and retry logic
- ✅ Local and cloud storage support
- ✅ REST API server (FastAPI)
- ✅ CLI tool for quick generation
- ✅ Extensible prompt templates
- ✅ Environment-based configuration
- ✅ Production-ready logging

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key with Sora 2 access
- pip or pipenv

### Installation

```bash
# Clone or download the repository
cd ugc

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### Configuration

Edit `.env` file:

```bash
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_MODEL_TEXT=gpt-4o
OPENAI_MODEL_VIDEO=sora-2

DEFAULT_VIDEO_DURATION=8
DEFAULT_VIDEO_SIZE=1280x720
STORAGE_PATH=./output/videos
```

### Usage

#### CLI Tool

```bash
# Generate a video
python cli.py "breathing exercise"

# With custom duration
python cli.py "panic relief tool" --duration 15

# Don't download video file
python cli.py "daily gratitude" --no-download
```

#### Python API

```python
from src.pipeline import UGCVideoPipeline

pipeline = UGCVideoPipeline()

result = pipeline.generate(
    topic="3-minute breathing tool",
    duration=8,
    store_result=True,
    download_video=True
)

print(f"Video URL: {result.video_url}")
print(f"Script: {result.script}")
```

#### REST API Server

```bash
# Start server
python api.py

# Or with uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000
```

```bash
# Generate video via API
curl -X POST "http://localhost:8000/api/v1/videos" \
  -H "Content-Type: application/json" \
  -d '{"topic": "breathing exercise", "duration": 8}'
```

#### Example Script

```bash
# Run the example
python example_usage.py
```

## Architecture

```
ugc/
├── src/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Settings & environment variables
│   ├── models.py             # Pydantic data models
│   ├── prompts.py            # LLM prompt templates
│   ├── llm_service.py        # GPT-4o script generation
│   ├── video_service.py      # Sora 2 video generation
│   ├── storage_service.py    # Local/S3 storage
│   └── pipeline.py           # Main orchestration
├── cli.py                    # Command-line interface
├── api.py                    # REST API server
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
└── .env.example              # Environment template
```

## API Reference

### Core Functions

#### `generate_script(topic: str) -> GeneratedScript`

Generates UGC script and Sora 2 prompt via GPT-4o.

**Parameters:**
- `topic` - Feature or benefit to highlight (e.g., "breathing exercise")

**Returns:**
- `GeneratedScript` with script text, Sora prompt, and metadata

#### `generate_video(prompt: str, duration: int, size: str) -> str`

Initiates Sora 2 video generation.

**Parameters:**
- `prompt` - Detailed video generation prompt
- `duration` - Video length in seconds (8, 15, 30, etc.)
- `size` - Resolution like "1280x720", "1920x1080"

**Returns:**
- Job ID for tracking

#### `poll_video_status(job_id: str) -> VideoJobStatus`

Polls video generation status until completion.

**Parameters:**
- `job_id` - Video generation job identifier

**Returns:**
- `VideoJobStatus` with status, progress, and video URL

#### `store_result(result: VideoResult) -> str`

Saves video and metadata to configured storage.

**Parameters:**
- `result` - Complete VideoResult object

**Returns:**
- Storage path or URL

### Data Models

#### `VideoResult`

```python
{
    "job_id": "video_abc123",
    "topic": "breathing exercise",
    "script": "Hey guys! So I've been dealing with...",
    "sora_prompt": "UGC style video: Person filming...",
    "video_url": "completed:video_abc123",
    "metadata": {
        "duration": 8,
        "tone": "calm",
        "hashtags": ["#mentalhealth", "#wellbeing"],
        "target_audience": "young adults with anxiety"
    },
    "status": "completed",
    "created_at": "2025-10-22T10:30:00",
    "completed_at": "2025-10-22T10:33:45"
}
```

## Sora 2 API Details

This implementation follows the [official OpenAI Video API documentation](https://platform.openai.com/docs/guides/video).

### Key Endpoints Used

- `POST /v1/videos` - Create video generation job
- `GET /v1/videos/{video_id}` - Retrieve job status
- `GET /v1/videos/{video_id}/content` - Download MP4

### Video Parameters

- **Model**: `sora-2` (fast) or `sora-2-pro` (high quality)
- **Duration**: String value (e.g., "8", "15", "30")
- **Size**: Resolution in format "WIDTHxHEIGHT"
  - 720p: `1280x720`
  - 1080p: `1920x1080`
  - Vertical: `720x1280` (9:16 for social media)

### Status Values

- `queued` - Job accepted, waiting to start
- `in_progress` - Video being generated
- `completed` - Video ready for download
- `failed` - Generation failed

## Deployment

### Local Development

```bash
# Run directly
python cli.py "topic here"

# Or start API server
python api.py
```

### Vercel (Serverless)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Create `vercel.json`:

```json
{
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "OPENAI_API_KEY": "@openai-api-key"
  }
}
```

### AWS Lambda

```bash
# Package for Lambda
pip install -r requirements.txt -t ./package
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip api.py src/*.py

# Upload to Lambda via AWS CLI
aws lambda update-function-code \
  --function-name ugc-video-generator \
  --zip-file fileb://deployment.zip
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ugc-video-gen .
docker run -p 8000:8000 --env-file .env ugc-video-gen
```

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ugc-video-gen
gcloud run deploy ugc-video-gen \
  --image gcr.io/PROJECT_ID/ugc-video-gen \
  --platform managed \
  --set-env-vars OPENAI_API_KEY=sk-...
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `OPENAI_MODEL_TEXT` | `gpt-4o` | LLM model for scripts |
| `OPENAI_MODEL_VIDEO` | `sora-2` | Sora model (`sora-2` or `sora-2-pro`) |
| `DEFAULT_VIDEO_DURATION` | `8` | Default video length in seconds |
| `DEFAULT_VIDEO_SIZE` | `1280x720` | Default resolution |
| `MAX_POLL_ATTEMPTS` | `60` | Max polling attempts |
| `POLL_INTERVAL_SECONDS` | `10` | Seconds between polls |
| `STORAGE_TYPE` | `local` | Storage backend (`local` or `s3`) |
| `STORAGE_PATH` | `./output/videos` | Local storage directory |
| `AWS_BUCKET_NAME` | - | S3 bucket (if using S3) |
| `LOG_LEVEL` | `INFO` | Logging level |

## Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Automatic retries with exponential backoff for API calls
- **Timeout Protection**: Configurable max polling attempts
- **Validation**: Input validation via Pydantic models
- **Logging**: Detailed logging at all levels
- **Graceful Degradation**: Continues operation on non-critical failures

## Extending the System

### Custom Prompt Templates

Edit `src/prompts.py`:

```python
SCRIPT_GENERATION_SYSTEM_PROMPT = """
Your custom system prompt here...
"""
```

### Different Brands

Modify the topic generation or create brand-specific pipelines:

```python
class BrandSpecificPipeline(UGCVideoPipeline):
    def __init__(self, brand_name: str):
        super().__init__()
        self.brand_name = brand_name
        # Customize prompts, durations, etc.
```

### Webhooks (Production)

For production, use OpenAI webhooks instead of polling:

1. Configure webhook URL in OpenAI dashboard
2. Receive `video.completed` / `video.failed` events
3. Process asynchronously via queue (Celery/RQ)

## Example Output

### Input
```
Topic: "3-minute breathing tool"
```

### Generated Script
```
Hey! So I've been super anxious lately and I found this
breathing tool in the Wellbewing app that's honestly been
a game-changer. It's just 3 minutes but it completely 
calms me down. If you struggle with anxiety, you need to
try this. Download Wellbewing - link in bio!
```

### Sora Prompt
```
UGC style video: Young woman in her mid-20s filming 
herself in a cozy bedroom with natural window lighting.
She's sitting cross-legged on her bed, speaking directly
to camera with genuine warmth. Shot on smartphone camera
vertical format, soft focus, authentic non-professional
aesthetic. She demonstrates calm breathing while talking.
Warm color palette, subtle handheld movement. Duration: 8
seconds. Mood: calm, relatable, genuine.
```

### Output Files
```
output/videos/video_abc123/
├── metadata.json          # Full result metadata
└── video.mp4             # Downloaded MP4 file
```

## Troubleshooting

### "Invalid API key"
Ensure `OPENAI_API_KEY` is set correctly in `.env`

### "Sora 2 access denied"
Sora 2 is in limited preview - ensure your API key has access

### "Video generation timeout"
Increase `MAX_POLL_ATTEMPTS` or `POLL_INTERVAL_SECONDS`

### "Import errors"
Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

MIT

## Support

For issues or questions, refer to:
- [OpenAI Video API Docs](https://platform.openai.com/docs/guides/video)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)


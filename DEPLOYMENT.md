# Deployment Guide

Complete deployment instructions for the UGC Video Generation Pipeline.

## Table of Contents

1. [Local Development](#local-development)
2. [Vercel (Serverless)](#vercel-serverless)
3. [AWS Lambda](#aws-lambda)
4. [Google Cloud Run](#google-cloud-run)
5. [Docker](#docker)
6. [Production Considerations](#production-considerations)

---

## Local Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# Test CLI
python cli.py "test topic" --log-level DEBUG

# Test API server
python api.py
```

### Running the API Server

```bash
# Development mode
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Vercel (Serverless)

Perfect for REST API deployments with automatic scaling.

### Prerequisites

```bash
npm install -g vercel
```

### Configuration

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "OPENAI_API_KEY": "@openai-api-key",
    "OPENAI_MODEL_TEXT": "gpt-4o",
    "OPENAI_MODEL_VIDEO": "sora-2",
    "DEFAULT_VIDEO_DURATION": "8",
    "DEFAULT_VIDEO_SIZE": "1280x720",
    "STORAGE_TYPE": "s3",
    "LOG_LEVEL": "INFO"
  }
}
```

### Deploy

```bash
# Add API key as secret
vercel secrets add openai-api-key "sk-proj-your-key-here"

# Deploy
vercel --prod

# Test
curl https://your-deployment.vercel.app/health
```

### Limitations

- 10 second timeout on Hobby plan (use Pro for longer)
- 50MB max deployment size
- Consider using async endpoints for long-running jobs

---

## AWS Lambda

Ideal for event-driven architectures and AWS integrations.

### Prerequisites

- AWS CLI configured
- IAM role with Lambda execution permissions

### Package for Lambda

```bash
# Create deployment package
mkdir package
pip install -r requirements.txt -t package/
cd package
zip -r ../deployment.zip .
cd ..

# Add application code
zip -g deployment.zip api.py
zip -g deployment.zip -r src/

# Upload to S3 (if >50MB)
aws s3 cp deployment.zip s3://your-bucket/ugc-video-gen/
```

### Create Lambda Function

```bash
# Create function
aws lambda create-function \
  --function-name ugc-video-generator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler api.handler \
  --zip-file fileb://deployment.zip \
  --timeout 900 \
  --memory-size 2048 \
  --environment Variables="{
    OPENAI_API_KEY=sk-proj-your-key,
    OPENAI_MODEL_TEXT=gpt-4o,
    OPENAI_MODEL_VIDEO=sora-2,
    STORAGE_TYPE=s3,
    AWS_BUCKET_NAME=your-videos-bucket
  }"

# Update existing function
aws lambda update-function-code \
  --function-name ugc-video-generator \
  --zip-file fileb://deployment.zip
```

### Add API Gateway

```bash
# Create REST API
aws apigatewayv2 create-api \
  --name ugc-video-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:REGION:ACCOUNT:function:ugc-video-generator
```

### Lambda Handler

Add to `api.py`:

```python
from mangum import Mangum

# ... existing FastAPI app ...

handler = Mangum(app)  # Lambda handler
```

Update `requirements.txt`:

```
mangum>=0.17.0
```

---

## Google Cloud Run

Containerized deployment with automatic scaling.

### Prerequisites

```bash
# Install gcloud CLI
gcloud auth login
gcloud config set project PROJECT_ID
```

### Create Dockerfile

Already included in the repository:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Build and Deploy

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/ugc-video-gen

# Deploy to Cloud Run
gcloud run deploy ugc-video-gen \
  --image gcr.io/PROJECT_ID/ugc-video-gen \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=sk-proj-your-key" \
  --set-env-vars "OPENAI_MODEL_TEXT=gpt-4o" \
  --set-env-vars "OPENAI_MODEL_VIDEO=sora-2" \
  --set-env-vars "STORAGE_TYPE=local" \
  --max-instances 10 \
  --memory 2Gi \
  --timeout 900 \
  --cpu 2

# Get URL
gcloud run services describe ugc-video-gen --format 'value(status.url)'
```

### Use Cloud Storage

```bash
# Create bucket
gsutil mb gs://your-videos-bucket

# Update deployment
gcloud run services update ugc-video-gen \
  --set-env-vars "STORAGE_TYPE=s3" \
  --set-env-vars "AWS_BUCKET_NAME=your-videos-bucket"
```

---

## Docker

### Build Image

```bash
docker build -t ugc-video-gen:latest .
```

### Run Locally

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ugc-video-gen \
  ugc-video-gen:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL_TEXT=gpt-4o
      - OPENAI_MODEL_VIDEO=sora-2
      - DEFAULT_VIDEO_DURATION=8
      - DEFAULT_VIDEO_SIZE=1280x720
      - STORAGE_TYPE=local
      - STORAGE_PATH=/app/output/videos
      - LOG_LEVEL=INFO
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### Push to Registry

```bash
# Docker Hub
docker tag ugc-video-gen:latest username/ugc-video-gen:latest
docker push username/ugc-video-gen:latest

# AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag ugc-video-gen:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ugc-video-gen:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ugc-video-gen:latest
```

---

## Production Considerations

### 1. Use Webhooks Instead of Polling

OpenAI Sora 2 supports webhooks for job completion:

```python
# Configure webhook in OpenAI dashboard
# Endpoint: https://your-api.com/webhooks/sora

@app.post("/webhooks/sora")
async def sora_webhook(event: dict):
    if event["type"] == "video.completed":
        job_id = event["data"]["id"]
        # Process completed video
        process_completed_video(job_id)
    return {"status": "received"}
```

### 2. Use Task Queue

For production, use Celery or RQ for async job processing:

```python
# tasks.py
from celery import Celery

celery = Celery('ugc_tasks', broker='redis://localhost:6379')

@celery.task
def generate_video_async(topic, duration):
    pipeline = UGCVideoPipeline()
    return pipeline.generate(topic, duration)

# api.py
@app.post("/api/v1/videos/async")
async def generate_async(request: VideoGenerationRequest):
    task = generate_video_async.delay(request.topic, request.duration)
    return {"task_id": task.id}
```

### 3. Rate Limiting

Add rate limiting to protect your API:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/videos")
@limiter.limit("5/minute")
async def generate_video(request: Request, ...):
    ...
```

### 4. Monitoring and Logging

Add monitoring with Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### 5. Database for Job Tracking

Use PostgreSQL or MongoDB to track jobs:

```python
# models.py
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VideoJob(Base):
    __tablename__ = "video_jobs"
    
    job_id = Column(String, primary_key=True)
    topic = Column(String, nullable=False)
    status = Column(Enum(VideoStatus))
    created_at = Column(DateTime)
    video_url = Column(String)
```

### 6. Caching

Cache LLM-generated scripts for common topics:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_script(topic: str, duration: int):
    return llm_service.generate_script(topic, duration)
```

### 7. S3 Storage Configuration

```python
# For production, use S3 for video storage
import boto3

class S3StorageService:
    def __init__(self):
        self.s3 = boto3.client('s3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
    
    def upload_video(self, file_path, key):
        self.s3.upload_file(file_path, settings.aws_bucket_name, key)
        url = f"https://{settings.aws_bucket_name}.s3.amazonaws.com/{key}"
        return url
```

### 8. Environment-Specific Configs

```bash
# .env.production
OPENAI_MODEL_VIDEO=sora-2-pro  # Use Pro for production
MAX_POLL_ATTEMPTS=120          # Longer timeout for Pro
STORAGE_TYPE=s3                # Cloud storage
LOG_LEVEL=WARNING              # Less verbose
```

### 9. Health Checks

Enhanced health check:

```python
@app.get("/health/detailed")
async def detailed_health():
    checks = {
        "api": "healthy",
        "openai_connection": check_openai_connection(),
        "storage": check_storage_availability(),
        "memory": get_memory_usage(),
    }
    return checks
```

### 10. Cost Optimization

- Use `sora-2` (not Pro) for drafts/testing
- Cache common scripts
- Implement request deduplication
- Set reasonable timeouts
- Monitor API usage via OpenAI dashboard

---

## Orchestration Platforms

### n8n Workflow

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Generate UGC Video",
      "method": "POST",
      "url": "https://your-api.com/api/v1/videos",
      "body": {
        "topic": "={{$json.topic}}",
        "duration": 8
      }
    }
  ]
}
```

### Zapier Integration

1. Trigger: New row in Google Sheets
2. Action: HTTP Request to your API
3. Action: Save result to Airtable/Notion

### Make.com

Create HTTP module calling your API endpoint with topics from any trigger source.

---

## Troubleshooting

### Memory Issues

Increase Lambda/Cloud Run memory to 2GB+

### Timeout Issues

- Increase function timeout to 900s (15 min)
- Use webhooks instead of polling
- Implement async job processing

### Cold Starts

- Use Provisioned Concurrency (Lambda)
- Set min instances > 0 (Cloud Run)
- Keep endpoints warm with scheduled pings

---

## Security Checklist

- [ ] API keys stored as environment variables/secrets
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] HTTPS only in production
- [ ] CORS configured properly
- [ ] Logging excludes sensitive data
- [ ] Webhook signatures verified
- [ ] S3 buckets have proper IAM policies
- [ ] Regular dependency updates

---

For questions or issues, consult the main [README.md](README.md).


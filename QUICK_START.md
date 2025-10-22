# Quick Start Guide

Get up and running with the UGC Video Generation Pipeline in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key with Sora 2 access
- 2GB free disk space (for video storage)

## Installation

### 1. Install Dependencies

```bash
cd ugc
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
```

Update this line in `.env`:
```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### 3. Test Installation

```bash
python -c "from src.pipeline import UGCVideoPipeline; print('✓ Installation successful')"
```

## First Video Generation

### Option 1: CLI (Recommended for Testing)

```bash
python cli.py "breathing exercise"
```

You should see:
```
✓ Script generated
✓ Video generation started
✓ Polling for completion...
✓ Video downloaded
✓ Complete!
```

Output saved to: `output/videos/video_*/video.mp4`

### Option 2: Python Script

Create `test.py`:

```python
from src.pipeline import UGCVideoPipeline

pipeline = UGCVideoPipeline()

result = pipeline.generate(
    topic="breathing exercise",
    duration=8
)

print(f"✓ Video: output/videos/{result.job_id}/video.mp4")
print(f"✓ Script: {result.script}")
```

Run it:
```bash
python test.py
```

### Option 3: REST API

Terminal 1 - Start server:
```bash
python api.py
```

Terminal 2 - Generate video:
```bash
curl -X POST http://localhost:8000/api/v1/videos \
  -H "Content-Type: application/json" \
  -d '{"topic":"breathing exercise","duration":8}'
```

## What Happens During Generation?

1. **Script Generation** (~3-5 seconds)
   - GPT-4o creates authentic UGC script
   - Generates Sora 2 video prompt
   - Adds metadata (tone, hashtags, audience)

2. **Video Generation** (~60-120 seconds)
   - Sora 2 renders video from prompt
   - Status: queued → in_progress → completed

3. **Download & Storage** (~5-10 seconds)
   - Downloads MP4 file
   - Saves metadata JSON
   - Stores in `output/videos/`

**Total Time**: ~70-140 seconds for 8-second video

## Verify Your Setup

### Check Health

```bash
# If API server is running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_text": "gpt-4o",
  "model_video": "sora-2"
}
```

### Check Output

```bash
ls -lh output/videos/video_*/
```

You should see:
```
metadata.json    # Video metadata
video.mp4        # Generated video file
```

## Common Issues

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### "Invalid API key"

Check `.env` file:
```bash
cat .env | grep OPENAI_API_KEY
```

Make sure it starts with `sk-proj-` or `sk-`

### "Sora access denied"

Sora 2 is in limited preview. Your API key needs specific access. Check:
- [OpenAI Sora Waitlist](https://openai.com/sora)
- Your OpenAI account tier

### "Timeout error"

Increase timeout in `.env`:
```bash
MAX_POLL_ATTEMPTS=120
POLL_INTERVAL_SECONDS=15
```

## Next Steps

Once your first video generates successfully:

1. **Try Different Topics**
   ```bash
   python cli.py "panic relief tool"
   python cli.py "daily gratitude"
   python cli.py "sleep meditation"
   ```

2. **Adjust Video Length**
   ```bash
   python cli.py "breathing exercise" --duration 15
   ```

3. **Customize Prompts**
   - Edit `src/prompts.py`
   - Modify script generation logic
   - Change video style/tone

4. **Deploy to Production**
   - See [DEPLOYMENT.md](DEPLOYMENT.md)
   - Set up webhooks
   - Configure S3 storage
   - Add monitoring

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/v1/videos` | POST | Generate video (sync) |
| `/api/v1/videos/async` | POST | Generate video (async) |

## Configuration Quick Reference

Key settings in `.env`:

```bash
# Models
OPENAI_MODEL_TEXT=gpt-4o          # or gpt-4-turbo
OPENAI_MODEL_VIDEO=sora-2         # or sora-2-pro

# Video defaults
DEFAULT_VIDEO_DURATION=8          # 8, 15, 30, 60
DEFAULT_VIDEO_SIZE=1280x720       # or 1920x1080, 720x1280

# Performance
MAX_POLL_ATTEMPTS=60              # Max status checks
POLL_INTERVAL_SECONDS=10          # Seconds between checks

# Storage
STORAGE_TYPE=local                # or s3
STORAGE_PATH=./output/videos      # Local path
```

## CLI Options

```bash
python cli.py --help

Options:
  topic                  Video topic (required)
  --duration INT         Video duration in seconds [default: 8]
  --no-store            Don't save result to disk
  --no-download         Don't download video file
  --log-level LEVEL     DEBUG, INFO, WARNING, ERROR [default: INFO]
```

## Examples by Use Case

### Marketing Campaign

```bash
python cli.py "stress management" --duration 15
python cli.py "mindfulness tips" --duration 15
python cli.py "better sleep habits" --duration 15
```

### Social Media Content

```bash
# Instagram Reels / TikTok (vertical)
DEFAULT_VIDEO_SIZE=720x1280 python cli.py "quick calm technique"

# YouTube Shorts
DEFAULT_VIDEO_SIZE=1080x1920 python cli.py "anxiety hack"
```

### Batch Generation

```python
from src.pipeline import UGCVideoPipeline

topics = [
    "breathing exercise",
    "panic relief",
    "daily gratitude",
    "sleep meditation"
]

pipeline = UGCVideoPipeline()

for topic in topics:
    print(f"Generating: {topic}")
    result = pipeline.generate(topic, duration=8)
    print(f"✓ {result.job_id}")
```

## Getting Help

- **Documentation**: [README.md](README.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)  
- **Examples**: [EXAMPLE_OUTPUT.md](EXAMPLE_OUTPUT.md)
- **OpenAI Docs**: https://platform.openai.com/docs/guides/video

## Success Checklist

- [ ] Python 3.11+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with valid API key
- [ ] First test video generated successfully
- [ ] Output files visible in `output/videos/`
- [ ] API server runs without errors
- [ ] Health check returns "healthy"

If all boxes are checked, you're ready for production deployment!

---

**Estimated setup time**: 5-10 minutes  
**First video generation**: 1-2 minutes  
**Ready for production**: See [DEPLOYMENT.md](DEPLOYMENT.md)


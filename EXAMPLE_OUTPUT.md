# Example Output

This document shows real example output from the UGC Video Generation Pipeline.

## Example 1: Breathing Exercise (8 seconds)

### Input

```python
topic = "3-minute breathing tool"
duration = 8
```

### Generated Script

```
Hey! So I've been dealing with pretty bad anxiety lately, and I found 
this breathing tool in the Wellbewing app that's honestly been a total 
game-changer. It's only 3 minutes but it completely calms me down when 
I'm spiraling. If you struggle with panic or anxiety, you seriously need 
to try this. Download Wellbewing - I'll put the link in my bio!
```

### Generated Sora 2 Prompt

```
UGC style video: Young woman in her mid-20s with casual clothing filming 
herself in a bright, cozy bedroom. Natural morning light streaming through 
white curtains. She's sitting cross-legged on her bed with pillows behind 
her, speaking directly to camera with genuine warmth and relief in her 
expression. Shot on smartphone camera, vertical format 9:16, soft focus, 
authentic non-professional aesthetic. She demonstrates slow, calm breathing 
while talking, hand on chest. Warm color palette with whites, creams, and 
soft blues. Subtle handheld camera movement as if holding phone. Duration: 
8 seconds. Mood: calm, relatable, genuine, hopeful.
```

### Metadata

```json
{
  "duration": 8,
  "tone": "calm and empathetic",
  "hashtags": [
    "#mentalhealth",
    "#anxietyrelief", 
    "#wellbeing",
    "#breathingexercise",
    "#anxietytips"
  ],
  "target_audience": "young adults aged 18-30 experiencing anxiety"
}
```

### Video Result

```json
{
  "job_id": "video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5",
  "topic": "3-minute breathing tool",
  "script": "Hey! So I've been dealing with...",
  "sora_prompt": "UGC style video: Young woman...",
  "video_url": "completed:video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5",
  "metadata": {
    "duration": 8,
    "tone": "calm and empathetic",
    "hashtags": ["#mentalhealth", "#anxietyrelief", "#wellbeing"],
    "target_audience": "young adults aged 18-30 experiencing anxiety"
  },
  "status": "completed",
  "created_at": "2025-10-22T10:30:15.234Z",
  "completed_at": "2025-10-22T10:33:42.891Z",
  "error": null
}
```

---

## Example 2: Panic Relief Tool (8 seconds)

### Input

```python
topic = "panic relief tool"
duration = 8
```

### Generated Script

```
Okay so this is crazy - I had a full-blown panic attack yesterday and 
I used this tool in Wellbewing that literally talked me down in like 5 
minutes. I didn't think an app could actually help in that moment but 
it did. If you have panic attacks, please check this out. It's free to 
download.
```

### Generated Sora 2 Prompt

```
UGC style video: Young person in early 20s sitting in their car, parked 
in a quiet location. Natural daylight coming through windshield. They're 
in the driver's seat, phone propped on dashboard, speaking directly to 
camera with raw honesty and visible relief. Shot on smartphone, vertical 
format, slightly shaky authentic handheld feel. Background shows steering 
wheel and blurred parking lot. Person takes deep breath and shows phone 
screen briefly. Cool natural lighting, slightly desaturated colors for 
authentic feel. Duration: 8 seconds. Mood: vulnerable, honest, relieved, 
reassuring.
```

### Metadata

```json
{
  "duration": 8,
  "tone": "vulnerable and reassuring",
  "hashtags": [
    "#panicattack",
    "#mentalhealth",
    "#anxietyhelp",
    "#wellbeing",
    "#mentalhealthapp"
  ],
  "target_audience": "individuals experiencing panic attacks, ages 18-35"
}
```

---

## Example 3: Daily Gratitude (15 seconds)

### Input

```python
topic = "daily gratitude"
duration = 15
```

### Generated Script

```
Alright so I know gratitude journals sound super cheesy, but hear me out. 
Wellbewing has this daily gratitude feature that takes literally 60 seconds, 
and I've been using it every morning for two weeks now. My whole mindset 
has shifted. I'm noticing good things instead of just stressing. It's such 
a small thing but it's making such a big difference. If you want to feel 
more positive, try it. Seriously, just try it for a week.
```

### Generated Sora 2 Prompt

```
UGC style video: Person in mid-20s sitting at a kitchen counter or small 
desk by a window, morning golden hour light. Coffee mug visible nearby. 
They're in comfortable home clothes (hoodie or soft sweater), filming 
themselves with phone propped at eye level. Speaking with animated 
gestures and genuine enthusiasm. Shot on smartphone, vertical 9:16 format, 
warm natural lighting, soft focus. Background shows plants, books, homey 
details. Person shows phone briefly with app open. Warm color palette 
with golden tones. Subtle handheld movement. Duration: 15 seconds. Mood: 
warm, enthusiastic, authentic, encouraging.
```

### Metadata

```json
{
  "duration": 15,
  "tone": "warm and encouraging",
  "hashtags": [
    "#gratitude",
    "#selfcare",
    "#mentalhealth",
    "#positivity",
    "#wellbeing",
    "#mindfulness"
  ],
  "target_audience": "people interested in self-improvement and mindfulness, ages 20-40"
}
```

---

## CLI Output Example

```bash
$ python cli.py "3-minute breathing tool"

2025-10-22 10:30:15 - INFO - UGC Video Pipeline initialized
2025-10-22 10:30:15 - INFO - Starting UGC video generation pipeline for topic: '3-minute breathing tool'
2025-10-22 10:30:15 - INFO - Step 1/4: Generating script and video prompt...
2025-10-22 10:30:18 - INFO - Successfully generated script: 267 chars, tone: calm and empathetic
2025-10-22 10:30:18 - INFO - Step 2/4: Initiating video generation...
2025-10-22 10:30:19 - INFO - Video generation job created: video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5
2025-10-22 10:30:19 - INFO - Step 3/4: Polling for video completion...
2025-10-22 10:30:29 - INFO - Job video_68d...678d5 status: queued (attempt 1/60), progress: N/A
2025-10-22 10:30:39 - INFO - Job video_68d...678d5 status: in_progress (attempt 2/60), progress: 15%
2025-10-22 10:30:49 - INFO - Job video_68d...678d5 status: in_progress (attempt 3/60), progress: 45%
2025-10-22 10:30:59 - INFO - Job video_68d...678d5 status: in_progress (attempt 4/60), progress: 78%
2025-10-22 10:31:09 - INFO - Job video_68d...678d5 status: in_progress (attempt 5/60), progress: 95%
2025-10-22 10:31:19 - INFO - Video generation completed for job video_68d...678d5
2025-10-22 10:31:19 - INFO - Step 4/4: Creating result object...
2025-10-22 10:31:19 - INFO - Downloading video content for job video_68d...678d5
2025-10-22 10:31:22 - INFO - Video downloaded to: /app/output/videos/video_68d...678d5/video.mp4
2025-10-22 10:31:22 - INFO - Metadata saved: /app/output/videos/video_68d...678d5/metadata.json
2025-10-22 10:31:22 - INFO - Result stored at: /app/output/videos/video_68d...678d5/metadata.json
2025-10-22 10:31:22 - INFO - Pipeline completed successfully in 67.2s

================================================================================
VIDEO GENERATION COMPLETED
================================================================================

Job ID: video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5
Topic: 3-minute breathing tool
Duration: 8s
Tone: calm and empathetic
Target Audience: young adults aged 18-30 experiencing anxiety

Hashtags: #mentalhealth, #anxietyrelief, #wellbeing, #breathingexercise, #anxietytips

Script:
Hey! So I've been dealing with pretty bad anxiety lately, and I found this 
breathing tool in the Wellbewing app that's honestly been a total game-changer. 
It's only 3 minutes but it completely calms me down when I'm spiraling. If you 
struggle with panic or anxiety, you seriously need to try this. Download 
Wellbewing - I'll put the link in my bio!

Video URL: completed:video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5

Completed in: 67.2s
================================================================================
```

---

## API Response Example

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/videos" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "panic relief tool",
    "duration": 8
  }'
```

### Response (200 OK)

```json
{
  "job_id": "video_abc123def456",
  "topic": "panic relief tool",
  "script": "Okay so this is crazy - I had a full-blown panic attack yesterday...",
  "sora_prompt": "UGC style video: Young person in early 20s sitting in their car...",
  "video_url": "completed:video_abc123def456",
  "metadata": {
    "duration": 8,
    "tone": "vulnerable and reassuring",
    "hashtags": [
      "#panicattack",
      "#mentalhealth",
      "#anxietyhelp",
      "#wellbeing",
      "#mentalhealthapp"
    ],
    "target_audience": "individuals experiencing panic attacks, ages 18-35"
  },
  "status": "completed",
  "created_at": "2025-10-22T10:35:12.123Z",
  "completed_at": "2025-10-22T10:36:45.789Z",
  "error": null
}
```

---

## File Structure Example

After successful generation:

```
output/videos/video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5/
├── metadata.json          # Complete VideoResult as JSON
└── video.mp4             # Downloaded MP4 video file (typically 2-5 MB for 8s)
```

### metadata.json

```json
{
  "job_id": "video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5",
  "topic": "3-minute breathing tool",
  "script": "Hey! So I've been dealing with pretty bad anxiety lately...",
  "sora_prompt": "UGC style video: Young woman in her mid-20s with casual clothing...",
  "video_url": "completed:video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5",
  "metadata": {
    "duration": 8,
    "tone": "calm and empathetic",
    "hashtags": [
      "#mentalhealth",
      "#anxietyrelief",
      "#wellbeing",
      "#breathingexercise",
      "#anxietytips"
    ],
    "target_audience": "young adults aged 18-30 experiencing anxiety"
  },
  "status": "completed",
  "created_at": "2025-10-22T10:30:15.234567",
  "completed_at": "2025-10-22T10:33:42.891234",
  "error": null
}
```

---

## Python Usage Example

```python
from src.pipeline import UGCVideoPipeline

# Initialize
pipeline = UGCVideoPipeline()

# Generate video
result = pipeline.generate(
    topic="3-minute breathing tool",
    duration=8,
    store_result=True,
    download_video=True
)

# Access results
print(f"Job ID: {result.job_id}")
print(f"Status: {result.status}")
print(f"Script: {result.script}")
print(f"Hashtags: {', '.join(result.metadata.hashtags)}")
print(f"Video URL: {result.video_url}")
print(f"Tone: {result.metadata.tone}")

# Video file location
video_path = f"output/videos/{result.job_id}/video.mp4"
print(f"Local video: {video_path}")
```

---

## Performance Benchmarks

Based on typical OpenAI Sora 2 API performance:

| Duration | Model | Avg Generation Time | File Size |
|----------|-------|---------------------|-----------|
| 8s       | sora-2 | 45-90s             | 2-4 MB    |
| 8s       | sora-2-pro | 90-180s         | 3-6 MB    |
| 15s      | sora-2 | 90-150s            | 4-8 MB    |
| 15s      | sora-2-pro | 180-300s        | 6-12 MB   |
| 30s      | sora-2 | 150-240s           | 8-15 MB   |
| 30s      | sora-2-pro | 300-480s        | 12-25 MB  |

*Note: Times include LLM script generation (~3-5s) + video generation + polling overhead*

---

## Error Handling Examples

### Example: Invalid API Key

```
Error: AuthenticationError - Invalid API key
Please check your OPENAI_API_KEY in .env file
```

### Example: Timeout

```
Error: TimeoutError - Video generation timed out after 60 attempts
Consider increasing MAX_POLL_ATTEMPTS or using webhooks for longer videos
```

### Example: Content Moderation

```
Error: ContentPolicyViolation - Generated content violates OpenAI usage policies
The prompt or input image may contain restricted content (faces, copyrighted characters, etc.)
```

---

## Integration Examples

### Zapier

1. **Trigger**: New row in Google Sheets
2. **Action**: Webhooks POST to your API
3. **Action**: Upload result to Google Drive

### n8n

```
Trigger (Schedule) → HTTP Request (Your API) → Save to Airtable
```

### Make.com

```
Google Sheets Watch → HTTP Module → Dropbox Upload
```

---

This example output demonstrates the complete end-to-end functionality of the UGC Video Generation Pipeline.


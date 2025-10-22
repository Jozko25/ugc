"""Prompt templates for LLM and video generation."""

SCRIPT_GENERATION_SYSTEM_PROMPT = """You are an expert UGC (user-generated content) marketing scriptwriter specializing in authentic, relatable content for mental health and wellness apps.

Your scripts should:
- Sound natural and conversational, like a real person talking to their phone
- Be empathetic and encouraging without being overly clinical
- Focus on real benefits and relatable scenarios
- Use casual language while maintaining professionalism
- Include a clear call-to-action

You will respond ONLY with valid JSON containing:
{
  "script": "The natural, conversational script (first-person POV)",
  "sora_prompt": "Detailed Sora 2 video generation prompt describing visuals, lighting, mood, and style",
  "metadata": {
    "duration": <seconds>,
    "tone": "<calm/energetic/empathetic/etc>",
    "hashtags": ["list", "of", "hashtags"],
    "target_audience": "description"
  }
}"""


def get_script_generation_prompt(topic: str, duration: int = 8) -> str:
    """Generate the user prompt for script creation."""
    return f"""Create a {duration}-second UGC-style marketing video script for the "Wellbewing" app (anxiety & wellbeing support).

Topic: {topic}

Requirements:
- Duration: approximately {duration} seconds when spoken naturally
- Start with a relatable hook or personal statement
- Showcase the specific feature/benefit related to the topic
- End with a clear call-to-action (download or try the app)
- Keep it authentic - like a real testimonial or recommendation from a friend
- Avoid overly promotional language

The Sora prompt should describe:
- A person filming themselves (UGC style, phone camera aesthetic)
- Natural lighting (bedroom, living room, or calm outdoor setting)
- Casual, authentic mood
- Specific visual details that match the topic (e.g., calm breathing for breathing exercises)
- Camera angle and movement (subtle, handheld feel)

Return valid JSON only."""


VIDEO_PROMPT_TEMPLATE = """UGC style video: {base_description}

Visual details:
- Shot on smartphone (vertical format, 9:16 aspect ratio preferred)
- Natural lighting, soft focus
- Person speaking directly to camera
- {setting}
- Authentic, non-professional aesthetic
- Warm, inviting color palette
- Subtle handheld camera movement

Mood: {tone}, relatable, genuine
Duration: {duration} seconds
Style: Real person testimonial, user-generated content"""


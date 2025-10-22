#!/usr/bin/env python3
"""
Modern GUI interface for UGC Video Generation Pipeline.
Clean, professional interface with all configuration options.
"""

import gradio as gr
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from src.pipeline import UGCVideoPipeline
from src.config import settings
from src.prompts import SCRIPT_GENERATION_SYSTEM_PROMPT, get_script_generation_prompt


class VideoGeneratorGUI:
    """GUI wrapper for video generation pipeline."""
    
    def __init__(self):
        """Initialize the GUI and pipeline."""
        self.pipeline = None
        self.current_job_id = None
    
    def generate_video(
        self,
        topic: str,
        duration: int,
        size: str,
        image_input,
        system_prompt: str,
        progress=gr.Progress()
    ):
        """
        Generate video with progress tracking.
        
        Args:
            topic: Video topic
            duration: Duration in seconds
            size: Video resolution
            image_input: Optional input image
            system_prompt: Custom system prompt
            progress: Gradio progress tracker
        """
        if not topic or topic.strip() == "":
            return None, "❌ Please enter a topic", ""
        
        try:
            # Update system prompt if changed
            if system_prompt != SCRIPT_GENERATION_SYSTEM_PROMPT:
                import src.prompts as prompts
                prompts.SCRIPT_GENERATION_SYSTEM_PROMPT = system_prompt
            
            # Initialize pipeline
            progress(0.1, desc="Initializing pipeline...")
            if self.pipeline is None:
                self.pipeline = UGCVideoPipeline()
            
            # Step 1: Generate script
            progress(0.2, desc="Generating script with AI...")
            script_data = self.pipeline.llm_service.generate_script(topic, duration)
            
            script_info = f"""**Generated Script:**
{script_data.script}

**Tone:** {script_data.metadata.tone}
**Hashtags:** {', '.join(script_data.metadata.hashtags)}
**Target Audience:** {script_data.metadata.target_audience}

**Sora Prompt:**
{script_data.sora_prompt}
"""
            
            # Step 2: Generate video
            progress(0.3, desc="Initiating video generation...")
            
            # Handle image input if provided
            if image_input is not None:
                # Save temp image
                temp_image_path = "temp_input_image.jpg"
                from PIL import Image
                if isinstance(image_input, str):
                    # File path
                    img = Image.open(image_input)
                else:
                    # PIL Image or array
                    img = Image.fromarray(image_input) if hasattr(image_input, 'shape') else image_input
                img.save(temp_image_path)
                
                # Use image-to-video generation
                job_id = self._generate_with_image(
                    script_data.sora_prompt,
                    duration,
                    size,
                    temp_image_path
                )
            else:
                # Text-to-video generation
                job_id = self.pipeline.video_service.generate_video(
                    prompt=script_data.sora_prompt,
                    duration=duration,
                    size=size
                )
            
            self.current_job_id = job_id
            
            # Step 3: Poll for completion
            progress(0.4, desc="Video generation in progress...")
            
            attempts = 0
            max_attempts = settings.max_poll_attempts
            
            while attempts < max_attempts:
                attempts += 1
                status = self.pipeline.video_service.check_video_status(job_id)
                
                # Update progress
                if status.progress:
                    progress_pct = 0.4 + (status.progress / 100) * 0.5
                    progress(progress_pct, desc=f"Generating video... {status.progress}%")
                
                if status.status.value == "completed":
                    break
                elif status.status.value == "failed":
                    return None, f"❌ Video generation failed: {status.error}", script_info
                
                import time
                time.sleep(settings.poll_interval_seconds)
            
            if attempts >= max_attempts:
                return None, "❌ Video generation timed out", script_info
            
            # Step 4: Download video
            progress(0.95, desc="Downloading video...")
            
            output_dir = Path(settings.storage_path) / job_id
            output_dir.mkdir(parents=True, exist_ok=True)
            video_path = output_dir / "video.mp4"
            
            self.pipeline.video_service.download_video_content(job_id, str(video_path))
            
            # Save metadata
            metadata = {
                "job_id": job_id,
                "topic": topic,
                "script": script_data.script,
                "sora_prompt": script_data.sora_prompt,
                "metadata": script_data.metadata.model_dump(),
                "created_at": datetime.utcnow().isoformat(),
                "video_path": str(video_path)
            }
            
            metadata_path = output_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2))
            
            progress(1.0, desc="Complete!")
            
            success_msg = f"""✅ **Video Generated Successfully!**

**Job ID:** {job_id}
**Duration:** {duration}s
**Size:** {size}
**File:** {video_path}

Video is ready to view below and saved locally."""
            
            return str(video_path), success_msg, script_info
            
        except Exception as e:
            error_msg = f"❌ **Error:** {str(e)}\n\nCheck your API key and try again."
            return None, error_msg, ""
    
    def _generate_with_image(self, prompt: str, duration: int, size: str, image_path: str) -> str:
        """Generate video with input image reference."""
        import httpx
        
        # Manual API call for image input (multipart/form-data)
        with open(image_path, 'rb') as f:
            files = {
                'input_reference': (image_path, f, 'image/jpeg')
            }
            data = {
                'prompt': prompt,
                'model': settings.openai_model_video,
                'size': size,
                'seconds': str(duration)
            }
            
            response = httpx.post(
                'https://api.openai.com/v1/videos',
                headers={'Authorization': f'Bearer {settings.openai_api_key}'},
                files=files,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            return result['id']


def create_interface():
    """Create and configure the Gradio interface."""
    
    gui = VideoGeneratorGUI()
    
    # Custom CSS for professional look
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .tab-nav button {
        font-size: 16px;
    }
    """
    
    with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="UGC Video Generator") as interface:
        
        gr.Markdown("""
        # 🎥 UGC Video Generator
        ### AI-Powered Marketing Video Creation with Sora 2
        Generate authentic user-generated content style videos for your brand.
        """)
        
        with gr.Tabs():
            # Main Generation Tab
            with gr.Tab("Generate Video"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Input")
                        
                        topic_input = gr.Textbox(
                            label="Topic",
                            placeholder="e.g., breathing exercise, panic relief tool, daily gratitude",
                            lines=2
                        )
                        
                        with gr.Row():
                            duration_input = gr.Slider(
                                minimum=5,
                                maximum=15,
                                value=8,
                                step=1,
                                label="Duration (seconds - API limit: 15s)"
                            )
                            
                            size_input = gr.Dropdown(
                                choices=[
                                    "720x1280",   # 720p vertical (portrait)
                                    "1080x1920",  # 1080p vertical (portrait)
                                    "1280x720",   # 720p landscape
                                    "1920x1080"   # 1080p landscape
                                ],
                                value="720x1280",
                                label="Resolution"
                            )
                        
                        image_input = gr.Image(
                            label="Input Image (Optional)",
                            type="filepath",
                            sources=["upload", "clipboard"],
                            height=200
                        )
                        
                        gr.Markdown("Upload an image to use as the first frame (optional)")
                        
                        generate_btn = gr.Button(
                            "🎬 Generate Video",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Output")
                        
                        status_output = gr.Markdown("Ready to generate...")
                        
                        video_output = gr.Video(
                            label="Generated Video",
                            height=400
                        )
                        
                        script_output = gr.Markdown(
                            label="Script & Details",
                            value=""
                        )
            
            # Settings Tab
            with gr.Tab("Settings"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### System Prompt Configuration")
                        gr.Markdown("Customize how the AI generates scripts")
                        
                        system_prompt_input = gr.Textbox(
                            label="System Prompt",
                            value=SCRIPT_GENERATION_SYSTEM_PROMPT,
                            lines=20,
                            max_lines=30
                        )
                        
                        with gr.Row():
                            reset_prompt_btn = gr.Button("Reset to Default")
                            save_prompt_btn = gr.Button("Save Changes", variant="primary")
                        
                        prompt_status = gr.Markdown("")
                    
                    with gr.Column():
                        gr.Markdown("### Current Configuration")
                        
                        config_display = gr.Markdown(f"""
**OpenAI Model (Text):** `{settings.openai_model_text}` (cheaper than gpt-4o)  
**OpenAI Model (Video):** `{settings.openai_model_video}`  
**Default Duration:** {settings.default_video_duration}s  
**Default Size:** {settings.default_video_size} (portrait/vertical)  
**Storage Type:** {settings.storage_type}  
**Storage Path:** `{settings.storage_path}`  
**Max Poll Attempts:** {settings.max_poll_attempts}  
**Poll Interval:** {settings.poll_interval_seconds}s  

**API Key Status:** {"✅ Configured" if settings.openai_api_key else "❌ Missing"}
                        """)
                        
                        gr.Markdown("### Example Topics")
                        gr.Markdown("""
- `breathing exercise for anxiety`
- `panic attack relief tool`
- `daily gratitude practice`
- `sleep meditation feature`
- `stress management tips`
- `mindfulness reminder`
                        """)
            
            # History Tab
            with gr.Tab("History"):
                gr.Markdown("### Recent Generations")
                
                refresh_btn = gr.Button("🔄 Refresh History")
                
                history_output = gr.Dataframe(
                    headers=["Job ID", "Topic", "Duration", "Created At", "Status"],
                    datatype=["str", "str", "str", "str", "str"],
                    interactive=False
                )
                
                def load_history():
                    """Load generation history from storage."""
                    history_data = []
                    storage_path = Path(settings.storage_path)
                    
                    if storage_path.exists():
                        for job_dir in sorted(storage_path.iterdir(), reverse=True):
                            if job_dir.is_dir() and job_dir.name.startswith("video_"):
                                metadata_file = job_dir / "metadata.json"
                                if metadata_file.exists():
                                    try:
                                        metadata = json.loads(metadata_file.read_text())
                                        history_data.append([
                                            metadata.get("job_id", "unknown"),
                                            metadata.get("topic", "N/A"),
                                            f"{metadata.get('metadata', {}).get('duration', 'N/A')}s",
                                            metadata.get("created_at", "N/A"),
                                            "✅ Complete"
                                        ])
                                    except:
                                        pass
                    
                    return history_data
                
                refresh_btn.click(fn=load_history, outputs=history_output)
                
                # Load on startup
                interface.load(fn=load_history, outputs=history_output)
        
        # Event handlers
        def reset_prompt():
            return SCRIPT_GENERATION_SYSTEM_PROMPT, "✅ Prompt reset to default"
        
        def save_prompt(prompt):
            return "✅ Prompt saved for this session"
        
        generate_btn.click(
            fn=gui.generate_video,
            inputs=[
                topic_input,
                duration_input,
                size_input,
                image_input,
                system_prompt_input
            ],
            outputs=[video_output, status_output, script_output]
        )
        
        reset_prompt_btn.click(
            fn=reset_prompt,
            outputs=[system_prompt_input, prompt_status]
        )
        
        save_prompt_btn.click(
            fn=save_prompt,
            inputs=[system_prompt_input],
            outputs=[prompt_status]
        )
    
    return interface


if __name__ == "__main__":
    import os
    
    interface = create_interface()
    
    # Get port from environment (Railway sets PORT variable)
    port = int(os.environ.get("PORT", 7860))
    
    # Launch with custom settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        quiet=False
    )


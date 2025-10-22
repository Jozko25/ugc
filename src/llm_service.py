"""LLM service for script generation using OpenAI GPT."""

import json
import logging
from typing import Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .models import GeneratedScript, ScriptMetadata
from .prompts import SCRIPT_GENERATION_SYSTEM_PROMPT, get_script_generation_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM (GPT-5)."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model_text
        logger.info(f"Initialized LLM service with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with retry logic.
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User query/request
            
        Returns:
            LLM response text
        """
        logger.debug(f"Calling LLM with model: {self.model}")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        logger.debug(f"LLM response received: {len(content)} characters")
        return content
    
    def generate_script(self, topic: str, duration: int | None = None) -> GeneratedScript:
        """
        Generate UGC script and video prompt for a given topic.
        
        Args:
            topic: The topic/feature to create content about
            duration: Target video duration in seconds (default from settings)
            
        Returns:
            GeneratedScript object with script, prompt, and metadata
        """
        if duration is None:
            duration = settings.default_video_duration
        
        logger.info(f"Generating script for topic: '{topic}', duration: {duration}s")
        
        try:
            # Call LLM
            user_prompt = get_script_generation_prompt(topic, duration)
            response_text = self._call_llm(SCRIPT_GENERATION_SYSTEM_PROMPT, user_prompt)
            
            # Parse JSON response
            response_data = json.loads(response_text)
            
            # Validate and create structured output
            script = GeneratedScript(
                script=response_data["script"],
                sora_prompt=response_data["sora_prompt"],
                metadata=ScriptMetadata(**response_data["metadata"])
            )
            
            logger.info(f"Successfully generated script: {len(script.script)} chars, "
                       f"tone: {script.metadata.tone}")
            
            return script
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except KeyError as e:
            logger.error(f"Missing required field in LLM response: {e}")
            raise ValueError(f"LLM response missing required field: {e}")
        except Exception as e:
            logger.error(f"Error generating script: {e}", exc_info=True)
            raise


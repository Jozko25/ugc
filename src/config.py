"""Configuration management for UGC video generation system."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    openai_model_text: str = Field(default="gpt-4o", validation_alias="OPENAI_MODEL_TEXT")
    openai_model_video: str = Field(default="sora-2", validation_alias="OPENAI_MODEL_VIDEO")
    
    # Video Generation Settings
    default_video_duration: int = Field(default=8, validation_alias="DEFAULT_VIDEO_DURATION")
    default_video_size: str = Field(default="1280x720", validation_alias="DEFAULT_VIDEO_SIZE")
    max_poll_attempts: int = Field(default=60, validation_alias="MAX_POLL_ATTEMPTS")
    poll_interval_seconds: int = Field(default=10, validation_alias="POLL_INTERVAL_SECONDS")
    
    # Storage Configuration
    storage_type: Literal["local", "s3"] = Field(default="local", validation_alias="STORAGE_TYPE")
    storage_path: str = Field(default="./output/videos", validation_alias="STORAGE_PATH")
    aws_access_key_id: str | None = Field(default=None, validation_alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(default=None, validation_alias="AWS_SECRET_ACCESS_KEY")
    aws_bucket_name: str | None = Field(default=None, validation_alias="AWS_BUCKET_NAME")
    aws_region: str = Field(default="us-east-1", validation_alias="AWS_REGION")
    
    # API Server Configuration
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


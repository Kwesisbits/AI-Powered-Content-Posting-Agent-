"""
Configuration settings for the AI Content Agent System.
Uses Pydantic Settings for environment variable management.
"""
import secrets
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Content Agent System"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite:///./content_agent.db"
    
    # AI/LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, mock
    LLM_MODEL: str = "gemma:7b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 60
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov"]
    
    # System Controls
    DEFAULT_SYSTEM_MODE: str = "NORMAL"  # NORMAL, MANUAL, CRISIS
    AUTO_APPROVE: bool = False  # Never True in production
    
    # Platform Configurations
    PLATFORMS: list = ["linkedin", "instagram", "twitter"]
    
    # Email/Notifications (mock for demo)
    SMTP_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

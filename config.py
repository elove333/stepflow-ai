"""Configuration management for the AI service."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        protected_namespaces=('settings_',)
    )
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    ai_service_url: str = "http://localhost:8000"
    
    # Model Configuration
    model_version: str = "1.0.0"
    scoring_threshold: float = 0.7
    
    # Performance Settings
    max_workers: int = 4
    timeout_seconds: int = 5


settings = Settings()

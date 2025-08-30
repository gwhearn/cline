import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """Application settings."""
    
    # App settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-secret-key-for-dev-only")
    
    # LLM settings
    PREFERRED_LLM_PROVIDER: str = os.getenv("PREFERRED_LLM_PROVIDER", "openai")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    # Ollama settings
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
    
    # Security settings
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    
    # Ansible settings
    ANSIBLE_OUTPUT_DIR: Path = Path(os.getenv("ANSIBLE_OUTPUT_DIR", "ansible_output"))
    
    @property
    def is_development(self) -> bool:
        """Check if the application is in development mode."""
        return self.APP_ENV.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if the application is in production mode."""
        return self.APP_ENV.lower() == "production"
    
    def get_ansible_output_path(self) -> Path:
        """Get the absolute path to the Ansible output directory."""
        output_dir = BASE_DIR / self.ANSIBLE_OUTPUT_DIR
        output_dir.mkdir(exist_ok=True, parents=True)
        return output_dir


# Create settings instance
settings = Settings()

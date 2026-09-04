from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fincheck AI"
    DATABASE_URL: str = "sqlite:///./finance_controller.db"
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    LLM_CONFIDENCE_THRESHOLD: float = 0.85
    LLM_MAX_CONCURRENCY: int = 5
    AUTH_ENABLED: bool = False
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "*"
    ]

    model_config = ConfigDict(env_file=".env", extra="allow")

settings = Settings()

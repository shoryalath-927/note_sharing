from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    hf_api_key: str = ""
    openrouter_api_key: str = ""

    database_url: str = "sqlite+aiosqlite:///./noteshare.db"
    upload_dir: str = "./uploads"
    embeddings_dir: str = "./embeddings_store"
    max_file_size_mb: int = 100
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure directories exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.embeddings_dir).mkdir(parents=True, exist_ok=True)

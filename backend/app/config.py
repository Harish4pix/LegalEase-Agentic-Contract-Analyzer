from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    app_name: str = "LegalEase"
    provider: str = os.getenv("LLM_PROVIDER", "demo").lower()
    model: str = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    max_contract_chars: int = int(os.getenv("MAX_CONTRACT_CHARS", "180000"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    data_dir: Path = BASE_DIR / "data" / "analyses"
    admin_data_file: Path = BASE_DIR / "data" / "admin_state.json"
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@legalease.local")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "Admin@123")
    admin_secret: str = os.getenv("ADMIN_SECRET", "change-this-secret-before-deployment")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings

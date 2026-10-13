from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = "sqlite:///./feature_intelligence.db"
    cors_origins: str = "http://localhost:5173"

    ai_enabled: bool = True
    ai_primary_provider: str = "openai"
    ai_fallback_provider: str = "gemini"
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    ai_request_timeout_seconds: int = Field(default=30, ge=5, le=120)

    openai_embedding_model: str = "text-embedding-3-small"
    semantic_top_k: int = Field(default=5, ge=1, le=50)
    semantic_min_candidate_score: float = Field(default=0.50, ge=0.0, le=1.0)
    semantic_strong_candidate_score: float = Field(default=0.75, ge=0.0, le=1.0)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

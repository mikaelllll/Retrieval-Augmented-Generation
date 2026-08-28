from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "RAG Explorer API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://rag:rag_local_password@postgres:5432/rag"
    redis_url: str = "redis://redis:6379/0"
    upload_dir: str = "/app/uploads"
    max_upload_mb: int = Field(default=15, ge=1, le=100)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384
    gemini_model: str = "gemini-2.5-flash-lite"
    retrieval_limit: int = Field(default=6, ge=1, le=20)
    similarity_threshold: float = Field(default=0.28, ge=0, le=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


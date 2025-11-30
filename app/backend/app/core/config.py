from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SEARCHBOOK_", extra="allow")

    project_name: str = "SearchBook"
    api_prefix: str = "/api"

    # PostgreSQL configuration
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "searchbook"
    db_user: str = "searchbook"
    db_password: str = "searchbook_password"

    # Application settings
    cors_allow_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    suggestions_limit: int = 5
    min_word_count: int = 10000  # Minimum words per book for ingestion
    bm25_results_limit: int = 50  # Max results from BM25 search


@lru_cache
def get_settings(**kwargs: Any) -> Settings:
    return Settings(**kwargs)


settings = get_settings()



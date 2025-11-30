from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SEARCHBOOK_", extra="allow")

    project_name: str = "SearchBook"
    api_prefix: str = "/api"

    elasticsearch_host: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "searchbook"
    elasticsearch_username: str = "elastic"
    elasticsearch_password: str = "changeme"

    cors_allow_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    suggestions_limit: int = 5


@lru_cache
def get_settings(**kwargs: Any) -> Settings:
    return Settings(**kwargs)


settings = get_settings()



from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CRG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "赛规通 API"
    environment: str = "development"
    database_url: str = "sqlite:///./data/contest-rule-guard.db"
    frontend_origin: str = "http://localhost:5173"
    model_project_default_budget_yuan: float = 1.0
    model_project_hard_budget_yuan: float = 20.0
    project_storage_roots: tuple[Path, ...] = (
        Path("./data/uploads"),
        Path("./data/submission-artifacts"),
        Path("./data/reports"),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

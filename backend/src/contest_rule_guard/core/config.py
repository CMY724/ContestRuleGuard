from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator
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
    model_project_default_budget_yuan: float = Field(
        default=1.0,
        ge=0,
        allow_inf_nan=False,
    )
    model_project_hard_budget_yuan: float = Field(
        default=20.0,
        ge=0,
        allow_inf_nan=False,
    )
    deepseek_api_key: str = Field(default="", description="DeepSeek API key")
    deepseek_model: str = Field(default="deepseek-chat")
    deepseek_timeout_s: float = Field(default=120, ge=10, le=600)
    project_storage_roots: tuple[Path, ...] = (
        Path("./data/uploads"),
        Path("./data/submission-artifacts"),
        Path("./data/reports"),
    )

    @model_validator(mode="after")
    def validate_model_budget_limits(self) -> Self:
        if self.model_project_default_budget_yuan > self.model_project_hard_budget_yuan:
            raise ValueError("default model project budget cannot exceed hard budget")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

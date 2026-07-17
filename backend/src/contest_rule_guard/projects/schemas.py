from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

TargetStage = Literal["school", "provincial", "national"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    competition_name: str = Field(min_length=1, max_length=200)
    competition_year: int = Field(ge=2000, le=2100)
    track: str = Field(min_length=1, max_length=120)
    target_stage: TargetStage


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    competition_name: str | None = Field(default=None, min_length=1, max_length=200)
    competition_year: int | None = Field(default=None, ge=2000, le=2100)
    track: str | None = Field(default=None, min_length=1, max_length=120)
    target_stage: TargetStage | None = None


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def normalize_utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @field_serializer("created_at", "updated_at")
    def serialize_utc_timestamp(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")

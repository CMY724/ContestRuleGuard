from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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

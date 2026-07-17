from uuid import UUID

from pydantic import BaseModel, Field

from contest_rule_guard.projects.schemas import TargetStage


class ProjectDiscoveryContext(BaseModel):
    project_id: UUID
    competition_name: str = Field(min_length=1, max_length=200)
    aliases: tuple[str, ...] = ()
    competition_year: int = Field(ge=2000, le=2100)
    track: str = Field(min_length=1, max_length=120)
    target_stage: TargetStage
    public_organizations: tuple[str, ...] = ()

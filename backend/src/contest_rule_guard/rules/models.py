"""Eight ContestRule types as a discriminated union with evidence bindings."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, TypeAdapter, model_validator

from contest_rule_guard.evidence.models import FieldEvidenceBinding
from contest_rule_guard.ingestion.models import NonEmptyString

# ?? Enums ????????????????????????????????????????????????????????

class RuleSeverity(StrEnum):
    BLOCK = "block"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"


class RuleStatus(StrEnum):
    NEEDS_REVIEW = "needs_review"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ConsistencyRelation(StrEnum):
    EQUAL = "equal"
    SUBSET = "subset"
    DISJOINT = "disjoint"
    OVERLAP = "overlap"


class DependencyType(StrEnum):
    BLOCKS = "blocks"
    REQUIRES = "requires"
    SUGGESTS = "suggests"


# ?? Common Scope ?????????????????????????????????????????????????

class RuleScope(BaseModel):
    stages: list[str] = Field(min_length=1)
    tracks: list[str] = Field(min_length=1)
    artifact_kinds: list[str] = Field(default_factory=list)


# ?? Base Rule ????????????????????????????????????????????????????

class BaseRule(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    rule_type: str
    title: NonEmptyString
    scope: RuleScope
    severity: RuleSeverity = RuleSeverity.WARN
    status: RuleStatus = RuleStatus.NEEDS_REVIEW
    confidence: float = Field(ge=0, le=1, default=0.0)
    bindings: list[FieldEvidenceBinding] = Field(default_factory=list)
    notes: str = ""


# ?? Eight Rule Types ?????????????????????????????????????????????

class DeadlineRule(BaseRule):
    rule_type: Literal["deadline"] = "deadline"
    action: NonEmptyString
    due_at: datetime
    timezone: str = "Asia/Shanghai"
    inclusive: bool = True


class EligibilityRule(BaseRule):
    rule_type: Literal["eligibility"] = "eligibility"
    condition: NonEmptyString
    qualification: NonEmptyString


class TeamSizeRule(BaseRule):
    rule_type: Literal["team_size"] = "team_size"
    min_members: int = Field(ge=1)
    max_members: int = Field(ge=1)
    advisor_required: bool = False

    @model_validator(mode="after")
    def validate_range(self) -> TeamSizeRule:
        if self.min_members > self.max_members:
            raise ValueError("min_members must not exceed max_members")
        return self


class FileRequiredRule(BaseRule):
    rule_type: Literal["file_required"] = "file_required"
    file_name_pattern: NonEmptyString
    description: str = ""
    mandatory: bool = True


class FileConstraintRule(BaseRule):
    rule_type: Literal["file_constraint"] = "file_constraint"
    file_name_pattern: NonEmptyString
    max_size_bytes: int | None = None
    allowed_formats: list[str] = Field(default_factory=list)
    page_limit: int | None = None


class ConsistencyRule(BaseRule):
    rule_type: Literal["consistency"] = "consistency"
    left_field: NonEmptyString
    right_field: NonEmptyString
    relation: ConsistencyRelation = ConsistencyRelation.EQUAL


class AnonymityRule(BaseRule):
    rule_type: Literal["anonymity"] = "anonymity"
    prohibited_patterns: list[str] = Field(min_length=1)


class DependencyRule(BaseRule):
    rule_type: Literal["dependency"] = "dependency"
    depends_on_rule_id: UUID
    dependency_type: DependencyType = DependencyType.REQUIRES


# ?? Discriminated Union ??????????????????????????????????????????

ContestRule = (
    DeadlineRule
    | EligibilityRule
    | TeamSizeRule
    | FileRequiredRule
    | FileConstraintRule
    | ConsistencyRule
    | AnonymityRule
    | DependencyRule
)

ContestRuleAdapter = TypeAdapter(Annotated[ContestRule, Field(discriminator="rule_type")])

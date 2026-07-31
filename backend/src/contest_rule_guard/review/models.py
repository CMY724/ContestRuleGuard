"""Review result models."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RuleCheckResult(BaseModel):
    rule_id: UUID
    rule_title: str
    rule_type: str
    passed: bool | None = None
    severity: str = "warn"
    evidence_quote: str = ""
    detail: str = ""
    blocked_reason: str = ""


class ReviewReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_rules: int = 0
    passed: int = 0
    failed: int = 0
    blocked: int = 0
    results: list[RuleCheckResult] = Field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total_rules == 0:
            return 0.0
        return self.passed / self.total_rules

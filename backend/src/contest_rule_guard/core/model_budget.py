from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import ModelUsageEvent


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelCallLimit:
    max_prompt_tokens: int
    max_output_tokens: int
    prompt_yuan_per_million: float
    completion_yuan_per_million: float

    @property
    def reserved_cost_yuan(self) -> float:
        if self.max_prompt_tokens <= 0 or self.max_output_tokens <= 0:
            raise ValueError("token limits must be positive")
        return round(
            (
                self.max_prompt_tokens * self.prompt_yuan_per_million
                + self.max_output_tokens * self.completion_yuan_per_million
            )
            / 1_000_000,
            6,
        )


class ModelBudgetLedger:
    def __init__(
        self,
        session: Session,
        *,
        default_budget_yuan: float,
        hard_budget_yuan: float,
    ) -> None:
        self._session = session
        self._default = default_budget_yuan
        self._hard = hard_budget_yuan

    def reserve(
        self,
        project_id: UUID,
        purpose: str,
        limit: ModelCallLimit,
        *,
        requested_project_budget_yuan: float,
        override_confirmed: bool,
    ) -> ModelUsageEvent:
        if requested_project_budget_yuan > self._hard:
            raise BudgetExceeded("requested project budget exceeds hard limit")
        if requested_project_budget_yuan > self._default and not override_confirmed:
            raise BudgetExceeded("budget override requires explicit confirmation")
        approved = max(0.0, requested_project_budget_yuan)
        charged = float(
            self._session.scalar(
                select(func.coalesce(func.sum(ModelUsageEvent.charged_cost_yuan), 0.0)).where(
                    ModelUsageEvent.project_id == project_id
                )
            )
            or 0.0
        )
        reserve = limit.reserved_cost_yuan
        if charged + reserve > approved:
            raise BudgetExceeded("project model budget exhausted before call")
        event = ModelUsageEvent(
            project_id=project_id,
            purpose=purpose,
            status="reserved",
            reserved_cost_yuan=reserve,
            charged_cost_yuan=reserve,
            prompt_tokens=0,
            completion_tokens=0,
        )
        self._session.add(event)
        self._session.commit()
        return event

    def finalize(
        self,
        event_id: UUID,
        *,
        succeeded: bool,
        prompt_tokens: int,
        completion_tokens: int,
        actual_cost_yuan: float | None = None,
    ) -> None:
        event = self._session.get(ModelUsageEvent, event_id)
        if event is None or event.status != "reserved":
            raise LookupError("model budget reservation not found or already finalized")
        actual = event.reserved_cost_yuan if not succeeded else float(actual_cost_yuan or 0.0)
        event.prompt_tokens = prompt_tokens
        event.completion_tokens = completion_tokens
        event.charged_cost_yuan = actual
        event.status = "succeeded" if succeeded else "failed"
        event.finalized_at = datetime.now(UTC)
        self._session.commit()
        if actual > event.reserved_cost_yuan + 1e-6:
            event.status = "budget_breach"
            self._session.commit()
            raise BudgetExceeded("provider usage exceeded preflight token-cost reservation")

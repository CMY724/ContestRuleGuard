from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from contest_rule_guard.core.model_budget import (
    BudgetExceeded,
    ModelBudgetLedger,
    ModelCallLimit,
)
from contest_rule_guard.db.base import Base
from contest_rule_guard.db.models import Project


def test_call_limit_rejects_negative_or_non_finite_prices() -> None:
    for invalid_price in (-1.0, float("nan"), float("inf")):
        limit = ModelCallLimit(
            max_prompt_tokens=100,
            max_output_tokens=100,
            prompt_yuan_per_million=invalid_price,
            completion_yuan_per_million=1.0,
        )
        with pytest.raises(ValueError, match="prices"):
            _ = limit.reserved_cost_yuan


@pytest.mark.parametrize(
    ("default_budget", "hard_budget"),
    [
        (-1.0, 20.0),
        (float("nan"), 20.0),
        (1.0, -1.0),
        (1.0, float("inf")),
        (2.0, 1.0),
    ],
)
def test_ledger_rejects_invalid_budget_limits(
    default_budget: float,
    hard_budget: float,
) -> None:
    with Session() as session, pytest.raises(ValueError, match="budget"):
        ModelBudgetLedger(
            session,
            default_budget_yuan=default_budget,
            hard_budget_yuan=hard_budget,
        )


@pytest.mark.parametrize("requested_budget", [-1.0, float("nan"), float("inf")])
def test_reservation_rejects_invalid_requested_budget(requested_budget: float) -> None:
    with Session() as session:
        ledger = ModelBudgetLedger(
            session,
            default_budget_yuan=1.0,
            hard_budget_yuan=20.0,
        )
        limit = ModelCallLimit(
            max_prompt_tokens=100,
            max_output_tokens=100,
            prompt_yuan_per_million=1.0,
            completion_yuan_per_million=1.0,
        )
        with pytest.raises(ValueError, match="requested project budget"):
            ledger.reserve(
                uuid4(),
                "rule_extraction",
                limit,
                requested_project_budget_yuan=requested_budget,
                override_confirmed=False,
            )


def test_project_budget_is_shared_and_override_requires_confirmation() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    project_id = uuid4()
    with Session(engine) as session:
        session.add(
            Project(
                id=project_id,
                name="demo",
                competition_name="demo",
                competition_year=2026,
                track="创新",
                target_stage="school",
            )
        )
        session.commit()
        ledger = ModelBudgetLedger(
            session,
            default_budget_yuan=1.0,
            hard_budget_yuan=20.0,
        )
        limit = ModelCallLimit(
            max_prompt_tokens=1000,
            max_output_tokens=1000,
            prompt_yuan_per_million=500,
            completion_yuan_per_million=500,
        )
        first = ledger.reserve(
            project_id,
            "rule_extraction",
            limit,
            requested_project_budget_yuan=1.0,
            override_confirmed=False,
        )
        ledger.finalize(
            first.id,
            succeeded=False,
            prompt_tokens=0,
            completion_tokens=0,
        )
        with pytest.raises(BudgetExceeded):
            ledger.reserve(
                project_id,
                "semantic_audit",
                limit,
                requested_project_budget_yuan=1.0,
                override_confirmed=False,
            )
        with pytest.raises(BudgetExceeded, match="explicit confirmation"):
            ledger.reserve(
                project_id,
                "query_expansion",
                limit,
                requested_project_budget_yuan=2.0,
                override_confirmed=False,
            )
        second = ledger.reserve(
            project_id,
            "query_expansion",
            limit,
            requested_project_budget_yuan=2.0,
            override_confirmed=True,
        )
        assert second.project_id == project_id


def test_successful_settlement_requires_finite_non_negative_actual_cost() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    project_id = uuid4()
    with Session(engine) as session:
        session.add(
            Project(
                id=project_id,
                name="demo",
                competition_name="demo",
                competition_year=2026,
                track="创新",
                target_stage="school",
            )
        )
        session.commit()
        ledger = ModelBudgetLedger(
            session,
            default_budget_yuan=1.0,
            hard_budget_yuan=20.0,
        )
        limit = ModelCallLimit(
            max_prompt_tokens=1000,
            max_output_tokens=1000,
            prompt_yuan_per_million=100,
            completion_yuan_per_million=100,
        )

        for actual_cost in (None, -0.1, float("nan"), float("inf")):
            event = ledger.reserve(
                project_id,
                "rule_extraction",
                limit,
                requested_project_budget_yuan=1.0,
                override_confirmed=False,
            )
            with pytest.raises(ValueError, match="actual cost"):
                ledger.finalize(
                    event.id,
                    succeeded=True,
                    prompt_tokens=10,
                    completion_tokens=10,
                    actual_cost_yuan=actual_cost,
                )
            ledger.finalize(
                event.id,
                succeeded=False,
                prompt_tokens=0,
                completion_tokens=0,
            )


def test_settlement_rejects_negative_token_usage_and_duplicate_finalization() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    project_id = uuid4()
    with Session(engine) as session:
        session.add(
            Project(
                id=project_id,
                name="demo",
                competition_name="demo",
                competition_year=2026,
                track="创新",
                target_stage="school",
            )
        )
        session.commit()
        ledger = ModelBudgetLedger(
            session,
            default_budget_yuan=1.0,
            hard_budget_yuan=20.0,
        )
        limit = ModelCallLimit(
            max_prompt_tokens=100,
            max_output_tokens=100,
            prompt_yuan_per_million=100,
            completion_yuan_per_million=100,
        )
        event = ledger.reserve(
            project_id,
            "semantic_audit",
            limit,
            requested_project_budget_yuan=1.0,
            override_confirmed=False,
        )
        with pytest.raises(ValueError, match="token usage"):
            ledger.finalize(
                event.id,
                succeeded=True,
                prompt_tokens=-1,
                completion_tokens=1,
                actual_cost_yuan=0.01,
            )
        ledger.finalize(
            event.id,
            succeeded=True,
            prompt_tokens=1,
            completion_tokens=1,
            actual_cost_yuan=0.01,
        )
        with pytest.raises(LookupError):
            ledger.finalize(
                event.id,
                succeeded=True,
                prompt_tokens=1,
                completion_tokens=1,
                actual_cost_yuan=0.01,
            )

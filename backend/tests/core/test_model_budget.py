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

import pytest
from pydantic import ValidationError

from contest_rule_guard.core.config import Settings


@pytest.mark.parametrize(
    "overrides",
    [
        {"model_project_default_budget_yuan": -1.0},
        {"model_project_default_budget_yuan": float("nan")},
        {"model_project_hard_budget_yuan": -1.0},
        {"model_project_hard_budget_yuan": float("inf")},
        {
            "model_project_default_budget_yuan": 2.0,
            "model_project_hard_budget_yuan": 1.0,
        },
    ],
)
def test_settings_reject_invalid_model_budgets(overrides: dict[str, float]) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **overrides)

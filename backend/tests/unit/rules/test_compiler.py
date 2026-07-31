from datetime import UTC, datetime

from contest_rule_guard.rules.compiler import CompilationKind, compile_rule
from contest_rule_guard.rules.models import (
    DeadlineRule,
    EligibilityRule,
    RuleScope,
    RuleStatus,
    TeamSizeRule,
)


def _school_scope() -> RuleScope:
    return RuleScope(stages=["school"], tracks=["AI"])


def test_unconfirmed_rule_returns_blocked() -> None:
    rule = DeadlineRule(
        title="test",
        scope=_school_scope(),
        action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
    )
    result = compile_rule(rule)
    assert result.kind == CompilationKind.BLOCKED


def test_confirmed_deadline_without_facts_returns_missing() -> None:
    rule = DeadlineRule(
        title="test",
        scope=_school_scope(),
        action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    result = compile_rule(rule)
    assert result.kind == CompilationKind.MISSING_FACTS
    assert len(result.checks) == 1
    assert result.checks[0]["check"] == "deadline_not_passed"


def test_confirmed_deadline_with_facts_passed() -> None:
    rule = DeadlineRule(
        title="test",
        scope=_school_scope(),
        action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    result = compile_rule(rule, {"current_time": "2026-08-01T00:00:00+00:00"})
    assert result.kind == CompilationKind.EXECUTABLE
    assert result.checks[0].get("_passed") is True


def test_confirmed_deadline_with_facts_failed() -> None:
    rule = DeadlineRule(
        title="test",
        scope=_school_scope(),
        action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    result = compile_rule(rule, {"current_time": "2026-10-01T00:00:00+00:00"})
    assert result.kind == CompilationKind.EXECUTABLE
    assert result.checks[0].get("_passed") is False


def test_eligibility_compiles_to_check() -> None:
    rule = EligibilityRule(
        title="test",
        scope=_school_scope(),
        condition="student",
        qualification="undergrad",
        status=RuleStatus.CONFIRMED,
    )
    result = compile_rule(rule)
    assert result.checks[0]["check"] == "eligibility_match"


def test_team_size_compiles_to_check() -> None:
    rule = TeamSizeRule(
        title="test",
        scope=_school_scope(),
        min_members=1,
        max_members=5,
        status=RuleStatus.CONFIRMED,
    )
    result = compile_rule(rule)
    assert result.checks[0]["check"] == "team_size_in_range"

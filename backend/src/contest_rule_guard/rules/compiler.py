"""Deterministic rule compiler: confirmed rules -> executable checks."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel

from contest_rule_guard.rules.models import (
    AnonymityRule,
    ConsistencyRule,
    ContestRule,
    DeadlineRule,
    DependencyRule,
    EligibilityRule,
    FileConstraintRule,
    FileRequiredRule,
    RuleStatus,
    TeamSizeRule,
)


class CompilationKind(StrEnum):
    BLOCKED = "blocked"
    EXECUTABLE = "executable"
    MISSING_FACTS = "missing_facts"


class CompilationResult(BaseModel):
    kind: CompilationKind
    rule_id: str
    checks: list[dict] = []


def compile_rule(rule: ContestRule, facts: dict | None = None) -> CompilationResult:
    if rule.status != RuleStatus.CONFIRMED:
        return CompilationResult(kind=CompilationKind.BLOCKED, rule_id=str(rule.id))

    checks: list[dict] = []

    if isinstance(rule, DeadlineRule):
        checks.append({
            "check": "deadline_not_passed",
            "action": rule.action,
            "due_at": rule.due_at.isoformat(),
            "timezone": rule.timezone,
            "inclusive": rule.inclusive,
        })
        if facts:
            now = facts.get("current_time")
            if now:
                current = datetime.fromisoformat(now) if isinstance(now, str) else now
                if current.tzinfo is None:
                    current = current.replace(tzinfo=UTC)
                dl = rule.due_at
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=UTC)
                passed = current > dl if rule.inclusive else current >= dl
                checks[0]["_result"] = not passed
                checks[0]["_passed"] = not passed
    elif isinstance(rule, EligibilityRule):
        checks.append({
            "check": "eligibility_match",
            "condition": rule.condition,
            "qualification": rule.qualification,
        })
    elif isinstance(rule, TeamSizeRule):
        checks.append({
            "check": "team_size_in_range",
            "min": rule.min_members,
            "max": rule.max_members,
        })
    elif isinstance(rule, FileRequiredRule):
        checks.append({
            "check": "file_present",
            "pattern": rule.file_name_pattern,
            "mandatory": rule.mandatory,
        })
    elif isinstance(rule, FileConstraintRule):
        checks.append({
            "check": "file_meets_constraints",
            "pattern": rule.file_name_pattern,
            "max_size_bytes": rule.max_size_bytes,
            "allowed_formats": rule.allowed_formats,
            "page_limit": rule.page_limit,
        })
    elif isinstance(rule, ConsistencyRule):
        checks.append({
            "check": "fields_consistent",
            "left": rule.left_field,
            "right": rule.right_field,
            "relation": rule.relation.value,
        })
    elif isinstance(rule, AnonymityRule):
        checks.append({"check": "no_prohibited_patterns", "patterns": rule.prohibited_patterns})
    elif isinstance(rule, DependencyRule):
        checks.append({"check": "dependency_satisfied", "depends_on": str(rule.depends_on_rule_id),
                       "type": rule.dependency_type.value})

    if facts is None and checks:
        return CompilationResult(
            kind=CompilationKind.MISSING_FACTS,
            rule_id=str(rule.id),
            checks=checks,
        )

    return CompilationResult(
            kind=CompilationKind.EXECUTABLE,
            rule_id=str(rule.id),
            checks=checks,
        )

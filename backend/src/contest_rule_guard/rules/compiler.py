"""Deterministic rule compiler: confirmed rules -> executable checks.

All eight ContestRule types are evaluated against SubmissionFacts.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from contest_rule_guard.review.facts import SubmissionFacts
from contest_rule_guard.rules.models import (
    AnonymityRule,
    ConsistencyRelation,
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


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _coerce_facts(facts: dict | None) -> SubmissionFacts:
    if facts is None:
        return SubmissionFacts()
    if isinstance(facts, SubmissionFacts):
        return facts
    return SubmissionFacts(**facts)


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    dt = datetime.fromisoformat(str(value))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _glob_to_regex(pattern: str) -> re.Pattern:
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")
    return re.compile(escaped, re.IGNORECASE)


# ---------------------------------------------------------------------------
# per-type evaluators
# ---------------------------------------------------------------------------

def _eval_deadline(rule: DeadlineRule, facts: SubmissionFacts) -> list[dict]:
    check: dict = {
        "check": "deadline_not_passed",
        "action": rule.action,
        "due_at": rule.due_at.isoformat(),
        "timezone": rule.timezone,
        "inclusive": rule.inclusive,
    }
    if facts.current_time is not None:
        current = _parse_datetime(facts.current_time)
        dl = rule.due_at
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=UTC)
        passed = current > dl if rule.inclusive else current >= dl
        check["_result"] = not passed
        check["_passed"] = not passed
    return [check]


def _eval_eligibility(
    rule: EligibilityRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "eligibility_match",
        "condition": rule.condition,
        "qualification": rule.qualification,
    }
    if facts.eligibility_met is not None:
        check["_result"] = facts.eligibility_met
        check["_passed"] = facts.eligibility_met
    return [check]


def _eval_team_size(
    rule: TeamSizeRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "team_size_in_range",
        "min": rule.min_members,
        "max": rule.max_members,
    }
    if facts.team_member_count is not None:
        ok = rule.min_members <= facts.team_member_count <= rule.max_members
        check["_result"] = ok
        check["_passed"] = ok
        check["_actual"] = facts.team_member_count
    return [check]


def _eval_file_required(
    rule: FileRequiredRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "file_present",
        "pattern": rule.file_name_pattern,
        "mandatory": rule.mandatory,
    }
    if facts.files:
        pat = _glob_to_regex(rule.file_name_pattern)
        matched = [f.name for f in facts.files if pat.search(f.name)]
        present = len(matched) > 0
        check["_result"] = present
        check["_passed"] = present
        check["_matched_files"] = matched
    return [check]


def _eval_file_constraint(
    rule: FileConstraintRule, facts: SubmissionFacts
) -> list[dict]:
    checks: list[dict] = []
    if not facts.files:
        return checks

    pat = _glob_to_regex(rule.file_name_pattern)
    matching = [f for f in facts.files if pat.search(f.name)]

    for f in matching:
        violations: list[str] = []
        # format check
        allowed_lower = [a.lower() for a in rule.allowed_formats]
        if rule.allowed_formats and f.format.lower() not in allowed_lower:
            violations.append(
                f"format '{f.format}' not in allowed {rule.allowed_formats}"
            )
        # size check
        if (
            rule.max_size_bytes is not None
            and f.size_bytes > rule.max_size_bytes
        ):
            violations.append(
                f"size {f.size_bytes} > max {rule.max_size_bytes}"
            )
        # page count check
        if (
            rule.page_limit is not None
            and f.page_count is not None
            and f.page_count > rule.page_limit
        ):
            violations.append(
                f"pages {f.page_count} > limit {rule.page_limit}"
            )

        checks.append({
            "check": "file_meets_constraints",
            "file": f.name,
            "format": f.format,
            "size_bytes": f.size_bytes,
            "page_count": f.page_count,
            "allowed_formats": rule.allowed_formats,
            "max_size_bytes": rule.max_size_bytes,
            "page_limit": rule.page_limit,
            "_passed": len(violations) == 0,
            "_violations": violations,
        })

    if not matching:
        checks.append({
            "check": "file_meets_constraints",
            "pattern": rule.file_name_pattern,
            "_passed": True,
            "_note": "no files matched the pattern",
        })

    return checks


def _eval_consistency(
    rule: ConsistencyRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "fields_consistent",
        "left": rule.left_field,
        "right": rule.right_field,
        "relation": rule.relation.value,
    }
    left_val = facts.field_values.get(rule.left_field)
    right_val = facts.field_values.get(rule.right_field)

    if left_val is not None and right_val is not None:
        ok = False
        if rule.relation == ConsistencyRelation.EQUAL:
            ok = left_val == right_val
        elif rule.relation == ConsistencyRelation.SUBSET:
            ok = set(str(left_val).split(",")).issubset(
                set(str(right_val).split(","))
            )
        elif rule.relation == ConsistencyRelation.DISJOINT:
            ok = not bool(
                set(str(left_val).split(","))
                & set(str(right_val).split(","))
            )
        elif rule.relation == ConsistencyRelation.OVERLAP:
            ok = bool(
                set(str(left_val).split(","))
                & set(str(right_val).split(","))
            )
        check["_result"] = ok
        check["_passed"] = ok
        check["_left_value"] = str(left_val)
        check["_right_value"] = str(right_val)
    return [check]


def _eval_anonymity(
    rule: AnonymityRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "no_prohibited_patterns",
        "patterns": rule.prohibited_patterns,
    }
    if facts.submission_text:
        text = facts.submission_text
        hits: list[str] = []
        for pat in rule.prohibited_patterns:
            if pat.lower() in text.lower():
                hits.append(pat)
        passed = len(hits) == 0
        check["_result"] = passed
        check["_passed"] = passed
        check["_hits"] = hits
    return [check]


def _eval_dependency(
    rule: DependencyRule, facts: SubmissionFacts
) -> list[dict]:
    check: dict = {
        "check": "dependency_satisfied",
        "depends_on": str(rule.depends_on_rule_id),
        "type": rule.dependency_type.value,
    }
    dep_id = str(rule.depends_on_rule_id)
    if dep_id in facts.rule_results:
        passed = facts.rule_results[dep_id]
        check["_result"] = passed
        check["_passed"] = passed
    return [check]


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------

def compile_rule(
    rule: ContestRule, facts: dict | SubmissionFacts | None = None
) -> CompilationResult:
    """Compile a confirmed rule into checks, evaluating against facts."""

    if rule.status != RuleStatus.CONFIRMED:
        return CompilationResult(
            kind=CompilationKind.BLOCKED, rule_id=str(rule.id)
        )

    facts_obj = _coerce_facts(facts)

    if isinstance(rule, DeadlineRule):
        checks = _eval_deadline(rule, facts_obj)
    elif isinstance(rule, EligibilityRule):
        checks = _eval_eligibility(rule, facts_obj)
    elif isinstance(rule, TeamSizeRule):
        checks = _eval_team_size(rule, facts_obj)
    elif isinstance(rule, FileRequiredRule):
        checks = _eval_file_required(rule, facts_obj)
    elif isinstance(rule, FileConstraintRule):
        checks = _eval_file_constraint(rule, facts_obj)
    elif isinstance(rule, ConsistencyRule):
        checks = _eval_consistency(rule, facts_obj)
    elif isinstance(rule, AnonymityRule):
        checks = _eval_anonymity(rule, facts_obj)
    elif isinstance(rule, DependencyRule):
        checks = _eval_dependency(rule, facts_obj)
    else:
        return CompilationResult(
            kind=CompilationKind.BLOCKED, rule_id=str(rule.id)
        )

    if not checks:
        return CompilationResult(
            kind=CompilationKind.BLOCKED, rule_id=str(rule.id)
        )

    has_eval = any("_passed" in c for c in checks)
    if not has_eval:
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

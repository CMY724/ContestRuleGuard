"""Tests for the enhanced rule compiler — all 8 rule types with facts evaluation."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from contest_rule_guard.review.facts import FileFact, SubmissionFacts
from contest_rule_guard.rules.compiler import CompilationKind, compile_rule
from contest_rule_guard.rules.models import (
    AnonymityRule,
    ConsistencyRelation,
    ConsistencyRule,
    DeadlineRule,
    DependencyRule,
    EligibilityRule,
    FileConstraintRule,
    FileRequiredRule,
    RuleScope,
    RuleSeverity,
    RuleStatus,
    TeamSizeRule,
)


def _school_scope() -> RuleScope:
    return RuleScope(stages=["school"], tracks=["AI"])


# ---- deadline (existing logic, preserved) ----

def test_unconfirmed_rule_returns_blocked() -> None:
    rule = DeadlineRule(
        title="test", scope=_school_scope(), action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
    )
    assert compile_rule(rule).kind == CompilationKind.BLOCKED


def test_confirmed_deadline_without_facts_returns_missing() -> None:
    rule = DeadlineRule(
        title="test", scope=_school_scope(), action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule)
    assert r.kind == CompilationKind.MISSING_FACTS


def test_deadline_passed() -> None:
    rule = DeadlineRule(
        title="test", scope=_school_scope(), action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"current_time": "2026-08-01T00:00:00+00:00"})
    assert r.kind == CompilationKind.EXECUTABLE
    assert r.checks[0]["_passed"] is True


def test_deadline_failed() -> None:
    rule = DeadlineRule(
        title="test", scope=_school_scope(), action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"current_time": "2026-10-01T00:00:00+00:00"})
    assert r.checks[0]["_passed"] is False


# ---- eligibility ----

def test_eligibility_met() -> None:
    rule = EligibilityRule(
        title="only undergrads", scope=_school_scope(),
        condition="full-time undergrad", qualification="undergrad",
        status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"eligibility_met": True})
    assert r.kind == CompilationKind.EXECUTABLE
    assert r.checks[0]["_passed"] is True


def test_eligibility_not_met() -> None:
    rule = EligibilityRule(
        title="only undergrads", scope=_school_scope(),
        condition="full-time undergrad", qualification="undergrad",
        status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"eligibility_met": False})
    assert r.checks[0]["_passed"] is False


# ---- team_size ----

def test_team_size_in_range() -> None:
    rule = TeamSizeRule(
        title="1-3 members", scope=_school_scope(),
        min_members=1, max_members=3, status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"team_member_count": 2})
    assert r.checks[0]["_passed"] is True


def test_team_size_too_many() -> None:
    rule = TeamSizeRule(
        title="1-3 members", scope=_school_scope(),
        min_members=1, max_members=3, status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"team_member_count": 5})
    assert r.checks[0]["_passed"] is False


def test_team_size_too_few() -> None:
    rule = TeamSizeRule(
        title="1-3 members", scope=_school_scope(),
        min_members=1, max_members=3, status=RuleStatus.CONFIRMED,
    )
    r = compile_rule(rule, {"team_member_count": 0})
    assert r.checks[0]["_passed"] is False


# ---- file_required ----

def test_file_required_present() -> None:
    rule = FileRequiredRule(
        title="project desc required", scope=_school_scope(),
        file_name_pattern="*.pdf", mandatory=True, status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="report.pdf", size_bytes=1000)])
    r = compile_rule(rule, facts)
    assert r.kind == CompilationKind.EXECUTABLE
    assert r.checks[0]["_passed"] is True


def test_file_required_missing() -> None:
    rule = FileRequiredRule(
        title="project desc required", scope=_school_scope(),
        file_name_pattern="*.pdf", mandatory=True, status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="report.docx", size_bytes=1000)])
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


# ---- file_constraint ----

def test_file_constraint_format_ok() -> None:
    rule = FileConstraintRule(
        title="PDF only", scope=_school_scope(),
        file_name_pattern="*.pdf", allowed_formats=["pdf"],
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="a.pdf", size_bytes=1000, format="pdf")])
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is True


def test_file_constraint_format_wrong() -> None:
    rule = FileConstraintRule(
        title="PDF only", scope=_school_scope(),
        file_name_pattern="*", allowed_formats=["pdf"],
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="a.docx", size_bytes=1000, format="docx")])
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


def test_file_constraint_size_exceeded() -> None:
    rule = FileConstraintRule(
        title="max 100MB", scope=_school_scope(),
        file_name_pattern="*", max_size_bytes=100_000_000,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="big.zip", size_bytes=150_000_000)])
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


def test_file_constraint_page_limit_exceeded() -> None:
    rule = FileConstraintRule(
        title="max 20 pages", scope=_school_scope(),
        file_name_pattern="*", page_limit=20,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(files=[FileFact(name="long.pdf", size_bytes=1000, page_count=25)])
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


# ---- anonymity ----

def test_anonymity_clean() -> None:
    rule = AnonymityRule(
        title="no identifiers", scope=_school_scope(),
        prohibited_patterns=["WHU", "Wuhan University", "张三"],
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(submission_text="This is a clean submission without identifiers.")
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is True


def test_anonymity_violation() -> None:
    rule = AnonymityRule(
        title="no identifiers", scope=_school_scope(),
        prohibited_patterns=["WHU", "Wuhan University", "张三"],
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(submission_text="We are from Wuhan University, advised by 张三.")
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


# ---- consistency ----

def test_consistency_equal_match() -> None:
    rule = ConsistencyRule(
        title="names match", scope=_school_scope(),
        left_field="project_name_a", right_field="project_name_b",
        relation=ConsistencyRelation.EQUAL,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(field_values={"project_name_a": "赛规通", "project_name_b": "赛规通"})
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is True


def test_consistency_equal_mismatch() -> None:
    rule = ConsistencyRule(
        title="names match", scope=_school_scope(),
        left_field="project_name_a", right_field="project_name_b",
        relation=ConsistencyRelation.EQUAL,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(field_values={"project_name_a": "赛规通", "project_name_b": "赛规通2"})
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


# ---- dependency ----

def test_dependency_satisfied() -> None:
    dep_id = uuid4()
    rule = DependencyRule(
        title="depends on doc", scope=_school_scope(),
        depends_on_rule_id=dep_id,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(rule_results={str(dep_id): True})
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is True


def test_dependency_failed() -> None:
    dep_id = uuid4()
    rule = DependencyRule(
        title="depends on doc", scope=_school_scope(),
        depends_on_rule_id=dep_id,
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(rule_results={str(dep_id): False})
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is False


# ---- SubmissionFacts as object ----

def test_accepts_submission_facts_object() -> None:
    rule = DeadlineRule(
        title="test", scope=_school_scope(), action="submit",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        status=RuleStatus.CONFIRMED,
    )
    facts = SubmissionFacts(current_time=datetime(2026, 8, 1, tzinfo=UTC))
    r = compile_rule(rule, facts)
    assert r.checks[0]["_passed"] is True

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from contest_rule_guard.evidence.models import FieldEvidenceBinding
from contest_rule_guard.rules.models import (
    AnonymityRule,
    ConsistencyRelation,
    ConsistencyRule,
    ContestRuleAdapter,
    DeadlineRule,
    DependencyRule,
    DependencyType,
    EligibilityRule,
    FileConstraintRule,
    FileRequiredRule,
    RuleScope,
    RuleStatus,
    TeamSizeRule,
)


def _scope() -> RuleScope:
    return RuleScope(stages=["school"], tracks=["AI"])


def _binding(field_path: str = "/payload/test") -> FieldEvidenceBinding:
    return FieldEvidenceBinding(
        field_path=field_path,
        evidence_ids=[uuid4()],
        quote="test quote",
    )


# ?? DeadlineRule ?????????????????????????????????????????????

def test_deadline_rule_defaults() -> None:
    rule = DeadlineRule(
        title="??????",
        scope=_scope(),
        action="school_submission",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
    )
    assert rule.rule_type == "deadline"
    assert rule.status == RuleStatus.NEEDS_REVIEW
    assert rule.inclusive is True
    assert rule.timezone == "Asia/Shanghai"


def test_deadline_rule_with_evidence() -> None:
    binding = _binding("/payload/due_at")
    rule = DeadlineRule(
        title="????",
        scope=_scope(),
        action="school_submission",
        due_at=datetime(2026, 9, 25, 17, 0, tzinfo=UTC),
        bindings=[binding],
    )
    assert len(rule.bindings) == 1
    assert rule.bindings[0].field_path == "/payload/due_at"


# ?? EligibilityRule ??????????????????????????????????????????

def test_eligibility_rule() -> None:
    rule = EligibilityRule(
        title="????????",
        scope=_scope(),
        condition="???????????????",
        qualification="?????????",
    )
    assert rule.rule_type == "eligibility"
    assert "???" in rule.condition


# ?? TeamSizeRule ?????????????????????????????????????????????

def test_team_size_valid_range() -> None:
    rule = TeamSizeRule(
        title="????",
        scope=_scope(),
        min_members=1,
        max_members=5,
    )
    assert rule.min_members == 1
    assert rule.max_members == 5


def test_team_size_rejects_inverted_range() -> None:
    with pytest.raises(ValidationError):
        TeamSizeRule(
            title="????",
            scope=_scope(),
            min_members=5,
            max_members=1,
        )


# ?? FileRequiredRule ?????????????????????????????????????????

def test_file_required_rule() -> None:
    rule = FileRequiredRule(
        title="????????",
        scope=_scope(),
        file_name_pattern="?????.docx",
        mandatory=True,
    )
    assert rule.rule_type == "file_required"
    assert rule.mandatory is True


# ?? FileConstraintRule ???????????????????????????????????????

def test_file_constraint_rule() -> None:
    rule = FileConstraintRule(
        title="PDF????",
        scope=_scope(),
        file_name_pattern="*.pdf",
        max_size_bytes=10 * 1024 * 1024,
        page_limit=20,
        allowed_formats=[".pdf"],
    )
    assert rule.max_size_bytes == 10_485_760
    assert rule.page_limit == 20


# ?? ConsistencyRule ??????????????????????????????????????????

def test_consistency_rule() -> None:
    rule = ConsistencyRule(
        title="?????",
        scope=_scope(),
        left_field="project.school_name",
        right_field="team.member_school",
        relation=ConsistencyRelation.EQUAL,
    )
    assert rule.relation == ConsistencyRelation.EQUAL


# ?? AnonymityRule ????????????????????????????????????????????

def test_anonymity_rule() -> None:
    rule = AnonymityRule(
        title="????????",
        scope=_scope(),
        prohibited_patterns=["??????", "WHUT"],
    )
    assert len(rule.prohibited_patterns) == 2


def test_anonymity_requires_at_least_one_pattern() -> None:
    with pytest.raises(ValidationError):
        AnonymityRule(
            title="???",
            scope=_scope(),
            prohibited_patterns=[],
        )


# ?? DependencyRule ???????????????????????????????????????????

def test_dependency_rule() -> None:
    target_id = uuid4()
    rule = DependencyRule(
        title="???????",
        scope=_scope(),
        depends_on_rule_id=target_id,
        dependency_type=DependencyType.REQUIRES,
    )
    assert rule.depends_on_rule_id == target_id
    assert rule.dependency_type == DependencyType.REQUIRES


# ?? Discriminated Union ??????????????????????????????????????

def test_contest_rule_discriminated_union_parses_correct_subtype() -> None:
    data = {
        "rule_type": "deadline",
        "title": "????",
        "scope": {"stages": ["school"], "tracks": ["AI"], "artifact_kinds": []},
        "action": "submit",
        "due_at": "2026-09-25T17:00:00+08:00",
    }
    rule = ContestRuleAdapter.validate_python(data)
    assert isinstance(rule, DeadlineRule)
    assert rule.action == "submit"


def test_contest_rule_rejects_unknown_type() -> None:
    with pytest.raises(ValidationError):
        ContestRuleAdapter.validate_python({
            "rule_type": "unknown_type",
            "title": "??",
            "scope": {"stages": ["school"], "tracks": ["AI"]},
        })

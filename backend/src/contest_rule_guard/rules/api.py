from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.rules.compiler import compile_rule
from contest_rule_guard.rules.models import (
    ContestRule,
    RuleStatus,
)
from contest_rule_guard.rules.repository import RuleRepository

router = APIRouter(prefix="/api/projects/{project_id}/rules", tags=["rules"])


@router.get("", response_model=list[ContestRule])
def list_rules(project_id: UUID, session: Session = Depends(get_session)) -> list[ContestRule]:  # noqa: B008
    return RuleRepository(session).list_by_project(project_id)


@router.get("/{rule_id}", response_model=ContestRule)
def get_rule(
    project_id: UUID, rule_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> ContestRule:
    rule = RuleRepository(session).get(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="rule not found")
    return rule


@router.patch("/{rule_id}", response_model=ContestRule)
def update_rule_status(
    project_id: UUID,
    rule_id: UUID,
    body: dict,
    session: Session = Depends(get_session),  # noqa: B008
) -> ContestRule:
    new_status = body.get("status")
    if new_status not in {s.value for s in RuleStatus}:
        raise HTTPException(status_code=422, detail=f"invalid status: {new_status}")
    updated = RuleRepository(session).update_status(rule_id, new_status)
    if updated is None:
        raise HTTPException(status_code=404, detail="rule not found")
    return updated


@router.post("/{rule_id}:compile")
def compile_rule_endpoint(
    project_id: UUID,
    rule_id: UUID,
    facts: dict | None = None,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    rule = RuleRepository(session).get(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="rule not found")
    result = compile_rule(rule, facts)
    return result.model_dump()

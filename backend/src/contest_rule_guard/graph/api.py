from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.graph.models import ConflictResolution, RuleGraph
from contest_rule_guard.graph.repository import GraphRepository

router = APIRouter(prefix="/api/projects/{project_id}", tags=["graph"])


@router.get("/rule-graph", response_model=RuleGraph)
def get_graph(project_id: UUID, session: Session = Depends(get_session)) -> RuleGraph:  # noqa: B008
    return GraphRepository(session).build_graph(project_id)


@router.get("/conflicts")
def list_conflicts(project_id: UUID, session: Session = Depends(get_session)) -> list:  # noqa: B008
    return GraphRepository(session).list_conflicts(project_id)


@router.post("/conflicts:resolve")
def resolve_conflict(
    project_id: UUID,
    resolution: ConflictResolution,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    repo = GraphRepository(session)
    conflicts = repo.list_conflicts(project_id)
    for c in conflicts:
        if resolution.superseding_rule_id in (c.rule_a_id, c.rule_b_id):
            updated = repo.resolve_conflict(c.id, resolution.superseding_rule_id)
            if updated:
                return {"status": "resolved", "conflict_id": str(c.id)}
    raise HTTPException(status_code=404, detail="conflict not found for given rule")

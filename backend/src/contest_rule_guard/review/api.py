from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.review.engine import ReviewEngine
from contest_rule_guard.review.models import ReviewReport
from contest_rule_guard.review.reporter import export_html

router = APIRouter(prefix="/api/projects/{project_id}/review", tags=["review"])


@router.post("", response_model=ReviewReport)
def run_review(
    project_id: UUID,
    facts: dict | None = None,
    session: Session = Depends(get_session),  # noqa: B008
) -> ReviewReport:
    return ReviewEngine(session).review(project_id, facts)


@router.get("/report", response_class=HTMLResponse)
def download_report(
    project_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> str:
    report = ReviewEngine(session).review(project_id)
    return export_html(report)

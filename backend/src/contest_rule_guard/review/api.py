from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.ingestion.repository import DocumentRepository
from contest_rule_guard.review.engine import ReviewEngine
from contest_rule_guard.review.facts_extractor import FactsExtractor
from contest_rule_guard.review.models import ReviewReport
from contest_rule_guard.review.reporter import export_html

router = APIRouter(prefix="/api/projects/{project_id}/review", tags=["review"])


@router.post("", response_model=ReviewReport)
def run_review(
    project_id: UUID,
    facts: dict | None = Body(None),  # noqa: B008
    session: Session = Depends(get_session),  # noqa: B008
) -> ReviewReport:
    """Run a full review.

    Facts are auto-extracted from all project documents.
    Pass optional facts dict to override/supplement auto-extracted values.
    Keys: team_member_count, eligibility_met, field_values, rule_results.
    """
    doc_repo = DocumentRepository(session)
    documents = doc_repo.list_by_project(project_id)
    auto_facts = FactsExtractor.extract(documents)
    if facts:
        auto_facts = FactsExtractor.merge(auto_facts, facts)
    return ReviewEngine(session).review(project_id, auto_facts)


@router.get("/report", response_class=HTMLResponse)
def download_report(
    project_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> str:
    doc_repo = DocumentRepository(session)
    documents = doc_repo.list_by_project(project_id)
    auto_facts = FactsExtractor.extract(documents)
    report = ReviewEngine(session).review(project_id, auto_facts)
    return export_html(report)

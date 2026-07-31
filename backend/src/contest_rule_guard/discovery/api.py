from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.discovery.scraper import DiscoveryScraper
from contest_rule_guard.ingestion.api import parser_registry
from contest_rule_guard.ingestion.models import DocumentStage, SourceTier
from contest_rule_guard.ingestion.repository import DocumentRepository
from contest_rule_guard.ingestion.service import IngestionService

router = APIRouter(prefix="/api/projects/{project_id}", tags=["discovery"])


class DiscoveryRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=20)
    source_tier: SourceTier = SourceTier.PRIMARY
    stage: DocumentStage = DocumentStage.SCHOOL


@router.post("/discovery:scan")
async def discover_rules(
    project_id: UUID,
    body: DiscoveryRequest,
    request: Request,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    registry = parser_registry()
    scraper = DiscoveryScraper()
    try:
        pages = await scraper.discover(body.urls, registry)
    finally:
        await scraper.close()

    repo = DocumentRepository(session)
    service = IngestionService(registry, repo)
    saved: list[dict] = []
    for page in pages:
        try:
            doc, _ = service.ingest(
                project_id,
                page.document.filename,
                page.document.media_type,
                page.document.content_sha256.encode()
                    if isinstance(page.document.content_sha256, str)
                    else b"",
                body.source_tier,
                body.stage,
            )
            saved.append({"url": page.url, "document_id": str(doc.id), "title": page.title})
        except Exception:
            continue

    return {"discovered": len(pages), "saved": len(saved), "documents": saved}

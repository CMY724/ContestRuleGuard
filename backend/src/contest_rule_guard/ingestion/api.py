from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.ingestion.models import DocumentStage, NormalizedDocument, SourceTier
from contest_rule_guard.ingestion.ocr import RapidOcrEngine
from contest_rule_guard.ingestion.parsers.docx import DocxParser
from contest_rule_guard.ingestion.parsers.html import HtmlParser
from contest_rule_guard.ingestion.parsers.image import ImageParser
from contest_rule_guard.ingestion.parsers.pdf import PdfParser
from contest_rule_guard.ingestion.parsers.pptx import PptxParser
from contest_rule_guard.ingestion.registry import ParserRegistry, UnsupportedDocumentError
from contest_rule_guard.ingestion.repository import DocumentRepository
from contest_rule_guard.ingestion.service import IngestionService

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MiB

router = APIRouter(prefix="/api/projects/{project_id}/documents", tags=["documents"])


@lru_cache(maxsize=1)
def parser_registry() -> ParserRegistry:
    ocr = RapidOcrEngine()
    return ParserRegistry(
        [PdfParser(ocr), DocxParser(), PptxParser(), HtmlParser(), ImageParser(ocr)]
    )


def ingestion_service(session: Session = Depends(get_session)) -> IngestionService:  # noqa: B008
    return IngestionService(parser_registry(), DocumentRepository(session))


@router.post("", response_model=NormalizedDocument)
async def upload_document(
    project_id: UUID,
    response: Response,
    source_tier: SourceTier = Form(),  # noqa: B008
    stage: DocumentStage = Form(),  # noqa: B008
    file: UploadFile = File(),  # noqa: B008
    service: IngestionService = Depends(ingestion_service),  # noqa: B008
) -> NormalizedDocument:
    try:
        content_bytes = await file.read()
        if len(content_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"file exceeds maximum upload size of {MAX_UPLOAD_BYTES // (1024*1024)} MiB",
            )
        document, created = service.ingest(
            project_id,
            file.filename or "upload.bin",
            file.content_type or "application/octet-stream",
            content_bytes,
            source_tier,
            stage,
        )
    except UnsupportedDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)
        ) from exc
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return document


@router.get("/{document_id}", response_model=NormalizedDocument)
def get_document(
    project_id: UUID,
    document_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> NormalizedDocument:
    document = DocumentRepository(session).get(project_id, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return document

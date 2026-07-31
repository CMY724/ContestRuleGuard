from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from contest_rule_guard.db.session import get_session
from contest_rule_guard.evidence.models import EvidenceSpan
from contest_rule_guard.evidence.repository import EvidenceRepository
from contest_rule_guard.ingestion.repository import DocumentRepository

router = APIRouter(
    prefix="/api/projects/{project_id}/documents/{document_id}/evidence",
    tags=["evidence"],
)


@router.get("", response_model=list[EvidenceSpan])
def list_evidence(
    project_id: UUID,
    document_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> list[EvidenceSpan]:
    doc_repo = DocumentRepository(session)
    if doc_repo.get(project_id, document_id) is None:
        raise HTTPException(status_code=404, detail="document not found")
    return EvidenceRepository(session).list_by_document(document_id)


@router.post("", response_model=EvidenceSpan, status_code=201)
def create_evidence(
    project_id: UUID,
    document_id: UUID,
    span: EvidenceSpan,
    session: Session = Depends(get_session),  # noqa: B008
) -> EvidenceSpan:
    doc_repo = DocumentRepository(session)
    doc = doc_repo.get(project_id, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    # Validate that the block_id belongs to this document
    block_ids = {block.id for unit in doc.units for block in unit.blocks}
    if span.block_id not in block_ids:
        raise HTTPException(
            status_code=422,
            detail=f"block {span.block_id} does not belong to document {document_id}",
        )
    # Validate quote exists in the block
    block = next(
        (b for unit in doc.units for b in unit.blocks if b.id == span.block_id),
        None,
    )
    if block and span.quote not in block.text:
        raise HTTPException(
            status_code=422,
            detail="evidence quote does not match block text",
        )
    return EvidenceRepository(session).add(span)


@router.get("/{evidence_id}", response_model=EvidenceSpan)
def get_evidence(
    project_id: UUID,
    document_id: UUID,
    evidence_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> EvidenceSpan:
    spans = EvidenceRepository(session).list_by_document(document_id)
    for span in spans:
        if span.id == evidence_id:
            return span
    raise HTTPException(status_code=404, detail="evidence span not found")

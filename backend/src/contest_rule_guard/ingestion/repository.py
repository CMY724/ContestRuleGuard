from json import loads
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import NormalizedDocumentRow
from contest_rule_guard.ingestion.models import NormalizedDocument


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, project_id: UUID, document: NormalizedDocument) -> NormalizedDocument:
        row = NormalizedDocumentRow(
            id=document.id,
            project_id=project_id,
            filename=document.filename,
            media_type=document.media_type,
            content_sha256=document.content_sha256,
            source_tier=document.source_tier.value,
            stage=document.stage.value,
            units_json=document.model_dump_json(include={"units"}),
        )
        self._session.add(row)
        self._session.commit()
        return document

    def find_by_hash(self, project_id: UUID, content_sha256: str) -> NormalizedDocument | None:
        statement = select(NormalizedDocumentRow).where(
            NormalizedDocumentRow.project_id == project_id,
            NormalizedDocumentRow.content_sha256 == content_sha256,
        )
        row = self._session.scalars(statement).first()
        if row is None:
            return None
        return self._to_domain(row)

    def get(self, project_id: UUID, document_id: UUID) -> NormalizedDocument | None:
        statement = select(NormalizedDocumentRow).where(
            NormalizedDocumentRow.project_id == project_id,
            NormalizedDocumentRow.id == document_id,
        )
        row = self._session.scalars(statement).first()
        if row is None:
            return None
        return self._to_domain(row)


    def list_by_project(self, project_id: UUID) -> list[NormalizedDocument]:
        statement = select(NormalizedDocumentRow).where(
            NormalizedDocumentRow.project_id == project_id,
        )
        rows = self._session.scalars(statement).all()
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: NormalizedDocumentRow) -> NormalizedDocument:
        from contest_rule_guard.ingestion.models import DocumentStage, SourceTier

        stored = loads(row.units_json)
        return NormalizedDocument(
            id=row.id,
            filename=row.filename,
            media_type=row.media_type,
            content_sha256=row.content_sha256,
            source_tier=SourceTier(row.source_tier),
            stage=DocumentStage(row.stage),
            units=stored["units"],
        )

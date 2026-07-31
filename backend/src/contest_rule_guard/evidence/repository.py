from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from contest_rule_guard.db.models import EvidenceSpanRow
from contest_rule_guard.evidence.models import EvidenceSpan


class EvidenceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, span: EvidenceSpan) -> EvidenceSpan:
        row = EvidenceSpanRow(
            id=span.id,
            document_id=span.document_id,
            block_id=span.block_id,
            field_path=span.field_path,
            quote=span.quote,
            start_char=span.start_char,
            end_char=span.end_char,
            source_tier=span.source_tier,
            stage=span.stage,
            document_sha256=span.document_sha256,
        )
        self._session.add(row)
        self._session.commit()
        return span

    def list_by_document(self, document_id: UUID) -> list[EvidenceSpan]:
        statement = select(EvidenceSpanRow).where(
            EvidenceSpanRow.document_id == document_id,
        )
        rows = self._session.scalars(statement).all()
        return [self._to_domain(row) for row in rows]

    def find_by_field_path(
        self, document_id: UUID, field_path: str,
    ) -> EvidenceSpan | None:
        statement = select(EvidenceSpanRow).where(
            EvidenceSpanRow.document_id == document_id,
            EvidenceSpanRow.field_path == field_path,
        )
        row = self._session.scalars(statement).first()
        return self._to_domain(row) if row else None

    @staticmethod
    def _to_domain(row: EvidenceSpanRow) -> EvidenceSpan:
        return EvidenceSpan(
            id=row.id,
            document_id=row.document_id,
            block_id=row.block_id,
            field_path=row.field_path,
            quote=row.quote,
            start_char=row.start_char,
            end_char=row.end_char,
            source_tier=row.source_tier,
            stage=row.stage,
            document_sha256=row.document_sha256,
        )

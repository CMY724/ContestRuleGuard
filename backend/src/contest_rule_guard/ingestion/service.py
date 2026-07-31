from uuid import UUID, uuid4

from contest_rule_guard.ingestion.models import (
    DocumentStage,
    NormalizedDocument,
    ParseContext,
    SourceTier,
)
from contest_rule_guard.ingestion.registry import ParserRegistry
from contest_rule_guard.ingestion.repository import DocumentRepository


class IngestionService:
    def __init__(self, registry: ParserRegistry, repository: DocumentRepository) -> None:
        self._registry = registry
        self._repository = repository

    def ingest(
        self,
        project_id: UUID,
        filename: str,
        media_type: str,
        content: bytes,
        source_tier: SourceTier,
        stage: DocumentStage,
    ) -> tuple[NormalizedDocument, bool]:
        context = ParseContext.from_upload(
            document_id=uuid4(),
            filename=filename,
            media_type=media_type,
            content=content,
        )
        existing = self._repository.find_by_hash(project_id, context.content_sha256)
        if existing is not None:
            return existing, False
        parser = self._registry.resolve(media_type, filename)
        parsed = parser.parse(content, context).model_copy(
            update={"source_tier": source_tier, "stage": stage}
        )
        return self._repository.add(project_id, parsed), True

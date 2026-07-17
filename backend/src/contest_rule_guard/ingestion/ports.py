from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from contest_rule_guard.ingestion.models import NormalizedDocument, ParseContext


class DocumentParser(ABC):
    media_types: frozenset[str] = frozenset()
    extensions: frozenset[str] = frozenset()

    @abstractmethod
    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        raise NotImplementedError


class IngestionPort(Protocol):
    async def import_remote_document(
        self,
        project_id: UUID,
        url: str,
        source_profile_id: UUID,
        idempotency_key: str,
    ) -> UUID: ...

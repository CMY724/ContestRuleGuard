from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from PIL import Image
from pydantic import BaseModel, Field

from contest_rule_guard.ingestion.models import NormalizedDocument, ParseContext


class DocumentParser(ABC):
    media_types: frozenset[str] = frozenset()
    extensions: frozenset[str] = frozenset()

    @abstractmethod
    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        raise NotImplementedError


class IngestionPort(Protocol):
    # TODO(phase-c): implement remote document import from official competition websites

    async def import_remote_document(
        self,
        project_id: UUID,
        url: str,
        source_profile_id: str,
        idempotency_key: str,
    ) -> UUID: ...


class OcrToken(BaseModel):
    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    polygon: list[tuple[float, float]] = Field(min_length=4)


class OcrEngine(ABC):
    @abstractmethod
    def recognize(self, image: Image.Image) -> list[OcrToken]:
        raise NotImplementedError

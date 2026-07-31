from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel, Field

from contest_rule_guard.ingestion.models import ContentSha256, NonEmptyString


class EvidenceSpan(BaseModel):
    """An immutable slice of a document block selected as evidence for a rule field."""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    block_id: UUID
    field_path: str = Field(min_length=1)
    quote: NonEmptyString
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    source_tier: str
    stage: str
    document_sha256: ContentSha256

    @classmethod
    def build(
        cls,
        *,
        document_id: UUID,
        block_id: UUID,
        field_path: str,
        quote: str,
        start_char: int,
        end_char: int,
        source_tier: str,
        stage: str,
        document_sha256: str,
    ) -> EvidenceSpan:
        return cls(
                        id=uuid5(
                NAMESPACE_URL,
                f"{document_id}:{block_id}:{field_path}:{start_char}:{end_char}",
            ),
            document_id=document_id,
            block_id=block_id,
            field_path=field_path,
            quote=quote.strip(),
            start_char=start_char,
            end_char=end_char,
            source_tier=source_tier,
            stage=stage,
            document_sha256=document_sha256,
        )


class FieldEvidenceBinding(BaseModel):
    """Links a ContestRule field to one or more evidence spans."""
    field_path: str = Field(min_length=1)
    evidence_ids: list[UUID] = Field(min_length=1)
    quote: NonEmptyString

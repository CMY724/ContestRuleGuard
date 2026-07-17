from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Self
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ContentSha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class UnitKind(StrEnum):
    PAGE = "page"
    FLOW = "flow"
    SLIDE = "slide"
    IMAGE = "image"


class BlockKind(StrEnum):
    PARAGRAPH = "paragraph"
    TABLE_CELL = "table_cell"
    TEXT_BOX = "text_box"
    OCR_LINE = "ocr_line"


class SourceTier(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    AUXILIARY = "auxiliary"


class DocumentStage(StrEnum):
    SCHOOL = "school"
    PROVINCIAL = "provincial"
    NATIONAL = "national"


class BoundingBox(BaseModel):
    left: float = Field(ge=0, le=1)
    top: float = Field(ge=0, le=1)
    right: float = Field(ge=0, le=1)
    bottom: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_coordinate_order(self) -> Self:
        if self.left > self.right or self.top > self.bottom:
            raise ValueError("bounding box coordinates are reversed")
        return self


class TextBlock(BaseModel):
    id: UUID
    unit_index: int = Field(ge=1)
    block_index: int = Field(ge=0)
    source_path: NonEmptyString
    text: NonEmptyString
    kind: BlockKind
    bbox: BoundingBox | None = None
    confidence: float = Field(default=1, ge=0, le=1)
    needs_review: bool = False

    @classmethod
    def build(
        cls,
        *,
        document_id: UUID,
        unit_index: int,
        block_index: int,
        source_path: str,
        text: str,
        kind: BlockKind,
        bbox: BoundingBox | None = None,
        confidence: float = 1,
    ) -> Self:
        return cls(
            id=uuid5(NAMESPACE_URL, f"{document_id}:{unit_index}:{source_path}"),
            unit_index=unit_index,
            block_index=block_index,
            source_path=source_path,
            text=text.strip(),
            kind=kind,
            bbox=bbox,
            confidence=confidence,
            needs_review=confidence < 0.80,
        )


class DocumentUnit(BaseModel):
    index: int = Field(ge=1)
    kind: UnitKind
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    blocks: list[TextBlock]


class NormalizedDocument(BaseModel):
    id: UUID
    filename: NonEmptyString
    media_type: NonEmptyString
    content_sha256: ContentSha256
    source_tier: SourceTier = SourceTier.AUXILIARY
    stage: DocumentStage = DocumentStage.SCHOOL
    units: list[DocumentUnit] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_block_ids(self) -> Self:
        block_ids = [block.id for unit in self.units for block in unit.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("duplicate block id")
        return self


class ParseContext(BaseModel):
    document_id: UUID
    filename: NonEmptyString
    media_type: NonEmptyString
    content_sha256: ContentSha256

    @classmethod
    def from_upload(
        cls,
        *,
        document_id: UUID,
        filename: str,
        media_type: str,
        content: bytes,
    ) -> Self:
        return cls(
            document_id=document_id,
            filename=Path(filename).name,
            media_type=media_type,
            content_sha256=sha256(content).hexdigest(),
        )

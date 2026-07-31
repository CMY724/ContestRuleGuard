from hashlib import sha256
from typing import get_type_hints
from uuid import uuid4

import pytest
from pydantic import ValidationError

from contest_rule_guard.ingestion.models import (
    BlockKind,
    DocumentUnit,
    NormalizedDocument,
    ParseContext,
    TextBlock,
    UnitKind,
)
from contest_rule_guard.ingestion.ports import DocumentParser, IngestionPort
from contest_rule_guard.ingestion.registry import ParserRegistry, UnsupportedDocumentError


class StubParser(DocumentParser):
    media_types = frozenset({"application/x-stub"})
    extensions = frozenset({".stub"})

    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        block = TextBlock.build(
            document_id=context.document_id,
            unit_index=1,
            block_index=0,
            source_path="paragraph[0]",
            text=content.decode(),
            kind=BlockKind.PARAGRAPH,
        )
        return NormalizedDocument(
            id=context.document_id,
            filename=context.filename,
            media_type=context.media_type,
            content_sha256=context.content_sha256,
            units=[DocumentUnit(index=1, kind=UnitKind.FLOW, blocks=[block])],
        )


class ExtensionOnlyParser(StubParser):
    media_types = frozenset({"application/x-extension-only"})


def test_ingestion_port_source_profile_id_is_string() -> None:
    type_hints = get_type_hints(IngestionPort.import_remote_document)

    assert type_hints["source_profile_id"] is str


def test_text_block_build_uses_a_stable_source_uuid() -> None:
    document_id = uuid4()

    first = TextBlock.build(
        document_id=document_id,
        unit_index=1,
        block_index=0,
        source_path="paragraph[0]",
        text=" first text ",
        kind=BlockKind.PARAGRAPH,
    )
    second = TextBlock.build(
        document_id=document_id,
        unit_index=1,
        block_index=1,
        source_path="paragraph[0]",
        text="different text",
        kind=BlockKind.PARAGRAPH,
    )

    assert first.id == second.id
    assert first.text == "first text"


def test_normalized_document_rejects_duplicate_block_ids_across_units() -> None:
    context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="rules.stub",
        media_type="application/x-stub",
        content=b"rules",
    )
    block = TextBlock.build(
        document_id=context.document_id,
        unit_index=1,
        block_index=0,
        source_path="paragraph[0]",
        text="rules",
        kind=BlockKind.PARAGRAPH,
    )

    with pytest.raises(ValidationError, match="duplicate block id"):
        NormalizedDocument(
            id=context.document_id,
            filename=context.filename,
            media_type=context.media_type,
            content_sha256=context.content_sha256,
            units=[
                DocumentUnit(index=1, kind=UnitKind.FLOW, blocks=[block]),
                DocumentUnit(index=2, kind=UnitKind.FLOW, blocks=[block]),
            ],
        )


def test_registry_prefers_media_type_then_lowercase_extension() -> None:
    media_parser = StubParser()
    extension_parser = ExtensionOnlyParser()
    registry = ParserRegistry([extension_parser, media_parser])

    assert registry.resolve("application/x-stub", "rules.STUB") is media_parser
    assert registry.resolve("application/octet-stream", "rules.STUB") is extension_parser

    unknown_media_type = "application/x-unknown"
    with pytest.raises(UnsupportedDocumentError, match=unknown_media_type):
        registry.resolve(unknown_media_type, "rules.unknown")

    upload_context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="../rules.stub",
        media_type="application/x-stub",
        content=b"rules",
    )
    assert upload_context.filename == "rules.stub"
    assert upload_context.content_sha256 == sha256(b"rules").hexdigest()

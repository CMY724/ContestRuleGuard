# backend/src/contest_rule_guard/ingestion/parsers/pdf.py
from __future__ import annotations

import fitz  # type: ignore[import-untyped]

from contest_rule_guard.ingestion.models import (
    BlockKind,
    BoundingBox,
    DocumentUnit,
    NormalizedDocument,
    ParseContext,
    TextBlock,
    UnitKind,
)
from contest_rule_guard.ingestion.ports import DocumentParser


def _bbox(x0: float, y0: float, x1: float, y1: float, width: float, height: float) -> BoundingBox:
    return BoundingBox(left=x0 / width, top=y0 / height, right=x1 / width, bottom=y1 / height)


class PdfParser(DocumentParser):
    media_types = frozenset({"application/pdf"})
    extensions = frozenset({".pdf"})

    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        units: list[DocumentUnit] = []
        with fitz.open(stream=content, filetype="pdf") as source:
            for page_number, page in enumerate(source, start=1):
                blocks: list[TextBlock] = []
                for raw in page.get_text("blocks", sort=True):
                    x0, y0, x1, y1, text = raw[:5]
                    cleaned = " ".join(str(text).split())
                    if not cleaned:
                        continue
                    block_index = len(blocks)
                    blocks.append(
                        TextBlock.build(
                            document_id=context.document_id,
                            unit_index=page_number,
                            block_index=block_index,
                            source_path=f"page[{page_number}].block[{block_index}]",
                            text=cleaned,
                            kind=BlockKind.PARAGRAPH,
                            bbox=_bbox(x0, y0, x1, y1, page.rect.width, page.rect.height),
                        )
                    )
                units.append(
                    DocumentUnit(
                        index=page_number,
                        kind=UnitKind.PAGE,
                        width=page.rect.width,
                        height=page.rect.height,
                        blocks=blocks,
                    )
                )
        return NormalizedDocument(
            id=context.document_id,
            filename=context.filename,
            media_type=context.media_type,
            content_sha256=context.content_sha256,
            units=units,
        )

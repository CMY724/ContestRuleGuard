# backend/tests/unit/ingestion/test_pdf_parser.py
from uuid import uuid4

import fitz

from contest_rule_guard.ingestion.models import ParseContext, UnitKind
from contest_rule_guard.ingestion.parsers.pdf import PdfParser


def make_text_pdf() -> bytes:
    document = fitz.open()
    first = document.new_page(width=400, height=600)
    first.insert_text((40, 80), "Deadline: 2026-09-25 17:00")
    second = document.new_page(width=400, height=600)
    second.insert_text((40, 80), "Team size: 1-3")
    content = document.tobytes()
    document.close()
    return content


def test_pdf_parser_preserves_page_and_bbox() -> None:
    content = make_text_pdf()
    context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="notice.pdf",
        media_type="application/pdf",
        content=content,
    )
    parsed = PdfParser().parse(content, context)
    assert [unit.kind for unit in parsed.units] == [UnitKind.PAGE, UnitKind.PAGE]
    assert parsed.units[0].index == 1
    assert "Deadline" in parsed.units[0].blocks[0].text
    assert parsed.units[1].blocks[0].source_path == "page[2].block[0]"
    bbox = parsed.units[0].blocks[0].bbox
    assert bbox is not None
    assert 0 <= bbox.left < bbox.right <= 1
    assert 0 <= bbox.top < bbox.bottom <= 1

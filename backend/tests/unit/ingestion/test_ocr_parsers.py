from io import BytesIO
from uuid import uuid4

import fitz
from PIL import Image

from contest_rule_guard.ingestion.models import ParseContext
from contest_rule_guard.ingestion.parsers.image import ImageParser
from contest_rule_guard.ingestion.parsers.pdf import PdfParser
from contest_rule_guard.ingestion.ports import OcrEngine, OcrToken


class FakeOcrEngine(OcrEngine):
    def recognize(self, image: Image.Image) -> list[OcrToken]:
        width, height = image.size
        return [
            OcrToken(
                text="校赛材料不得出现学校名称",
                confidence=0.76,
                polygon=[(10, 10), (width - 10, 10), (width - 10, height - 10), (10, height - 10)],
            )
        ]


def make_png() -> bytes:
    image = Image.new("RGB", (320, 120), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_scanned_pdf(png: bytes) -> bytes:
    document = fitz.open()
    page = document.new_page(width=320, height=120)
    page.insert_image(page.rect, stream=png)
    content = document.tobytes()
    document.close()
    return content


def test_image_parser_marks_low_confidence_ocr_for_review() -> None:
    content = make_png()
    context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="notice.png",
        media_type="image/png",
        content=content,
    )
    parsed = ImageParser(FakeOcrEngine()).parse(content, context)
    block = parsed.units[0].blocks[0]
    assert block.source_path == "image[1].ocr[0]"
    assert block.needs_review is True
    assert block.confidence == 0.76
    assert block.bbox is not None


def test_pdf_parser_calls_ocr_only_for_empty_text_page() -> None:
    content = make_scanned_pdf(make_png())
    context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="scan.pdf",
        media_type="application/pdf",
        content=content,
    )
    parsed = PdfParser(FakeOcrEngine()).parse(content, context)
    assert parsed.units[0].blocks[0].source_path == "page[1].ocr[0]"
    assert parsed.units[0].blocks[0].needs_review is True

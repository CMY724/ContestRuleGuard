from io import BytesIO
from uuid import UUID

from PIL import Image

from contest_rule_guard.ingestion.models import (
    BlockKind,
    BoundingBox,
    DocumentUnit,
    NormalizedDocument,
    ParseContext,
    TextBlock,
    UnitKind,
)
from contest_rule_guard.ingestion.ports import DocumentParser, OcrEngine, OcrToken


def token_bbox(token: OcrToken, width: int, height: int) -> BoundingBox:
    xs = [point[0] for point in token.polygon]
    ys = [point[1] for point in token.polygon]
    return BoundingBox(
        left=max(0.0, min(xs) / width),
        top=max(0.0, min(ys) / height),
        right=min(1.0, max(xs) / width),
        bottom=min(1.0, max(ys) / height),
    )


def ocr_blocks(
    image: Image.Image,
    engine: OcrEngine,
    document_id: UUID,
    unit_index: int,
    unit_label: str,
) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    width, height = image.size
    for token in engine.recognize(image):
        block_index = len(blocks)
        blocks.append(
            TextBlock.build(
                document_id=document_id,
                unit_index=unit_index,
                block_index=block_index,
                source_path=f"{unit_label}.ocr[{block_index}]",
                text=token.text,
                kind=BlockKind.OCR_LINE,
                bbox=token_bbox(token, width, height),
                confidence=token.confidence,
            )
        )
    return blocks


class ImageParser(DocumentParser):
    media_types = frozenset({"image/png", "image/jpeg", "image/webp", "image/tiff", "image/bmp"})
    extensions = frozenset({".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif", ".bmp"})

    def __init__(self, ocr: OcrEngine) -> None:
        self._ocr = ocr

    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        image = Image.open(BytesIO(content))
        blocks = ocr_blocks(image, self._ocr, context.document_id, 1, "image[1]")
        return NormalizedDocument(
            id=context.document_id,
            filename=context.filename,
            media_type=context.media_type,
            content_sha256=context.content_sha256,
            units=[
                DocumentUnit(
                    index=1,
                    kind=UnitKind.IMAGE,
                    width=image.width,
                    height=image.height,
                    blocks=blocks,
                )
            ],
        )

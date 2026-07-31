# backend/src/contest_rule_guard/ingestion/parsers/pptx.py
from io import BytesIO

from pptx import Presentation

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


def _shape_bbox(shape: object, width: int, height: int) -> BoundingBox:
    left = int(getattr(shape, "left"))
    top = int(getattr(shape, "top"))
    right = left + int(getattr(shape, "width"))
    bottom = top + int(getattr(shape, "height"))
    return BoundingBox(
        left=left / width,
        top=top / height,
        right=right / width,
        bottom=bottom / height,
    )


class PptxParser(DocumentParser):
    media_types = frozenset(
        {"application/vnd.openxmlformats-officedocument.presentationml.presentation"}
    )
    extensions = frozenset({".pptx"})

    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        deck = Presentation(BytesIO(content))
        units: list[DocumentUnit] = []
        for slide_number, slide in enumerate(deck.slides, start=1):
            blocks: list[TextBlock] = []
            for shape_index, shape in enumerate(slide.shapes):
                bbox = _shape_bbox(shape, deck.slide_width, deck.slide_height)
                if shape.has_table:
                    table = shape.table
                    for row_index, row in enumerate(table.rows):
                        for cell_index, cell in enumerate(row.cells):
                            text = " ".join(cell.text.split())
                            if text:
                                path = f"slide[{slide_number}].shape[{shape_index}].table.row[{row_index}].cell[{cell_index}]"
                                blocks.append(
                                    TextBlock.build(
                                        document_id=context.document_id,
                                        unit_index=slide_number,
                                        block_index=len(blocks),
                                        source_path=path,
                                        text=text,
                                        kind=BlockKind.TABLE_CELL,
                                        bbox=bbox,
                                    )
                                )
                elif shape.has_text_frame:
                    for paragraph_index, paragraph in enumerate(shape.text_frame.paragraphs):
                        text = " ".join(paragraph.text.split())
                        if text:
                            path = f"slide[{slide_number}].shape[{shape_index}].paragraph[{paragraph_index}]"
                            blocks.append(
                                TextBlock.build(
                                    document_id=context.document_id,
                                    unit_index=slide_number,
                                    block_index=len(blocks),
                                    source_path=path,
                                    text=text,
                                    kind=BlockKind.TEXT_BOX,
                                    bbox=bbox,
                                )
                            )
            units.append(
                DocumentUnit(
                    index=slide_number,
                    kind=UnitKind.SLIDE,
                    width=deck.slide_width,
                    height=deck.slide_height,
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

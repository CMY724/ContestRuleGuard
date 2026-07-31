# backend/src/contest_rule_guard/ingestion/parsers/html.py
from html.parser import HTMLParser

from contest_rule_guard.ingestion.models import (
    BlockKind,
    DocumentUnit,
    NormalizedDocument,
    ParseContext,
    TextBlock,
    UnitKind,
)
from contest_rule_guard.ingestion.ports import DocumentParser


class _VisibleBlockParser(HTMLParser):
    BLOCK_TAGS = frozenset({"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "a"})
    IGNORED_TAGS = frozenset({"script", "style", "noscript", "template", "svg"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._active: list[dict[str, object]] = []
        self._tag_counts: dict[str, int] = {}
        self.blocks: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth or tag not in self.BLOCK_TAGS:
            return
        index = self._tag_counts.get(tag, 0)
        self._tag_counts[tag] = index + 1
        href = dict(attrs).get("href") if tag == "a" else None
        self._active.append({"tag": tag, "path": f"html.{tag}[{index}]", "text": [], "href": href})

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            for item in self._active:
                item["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.IGNORED_TAGS:
            self._ignored_depth = max(0, self._ignored_depth - 1)
            return
        if self._ignored_depth:
            return
        for position in range(len(self._active) - 1, -1, -1):
            item = self._active[position]
            if item["tag"] != tag:
                continue
            self._active.pop(position)
            text = " ".join("".join(item["text"]).split())
            if text:
                href = item["href"]
                if href:
                    text = f"{text} [href={href}]"
                self.blocks.append((str(item["path"]), text))
            break


class HtmlParser(DocumentParser):
    media_types = frozenset({"text/html", "application/xhtml+xml"})
    extensions = frozenset({".html", ".htm", ".xhtml"})

    def parse(self, content: bytes, context: ParseContext) -> NormalizedDocument:
        parser = _VisibleBlockParser()
        parser.feed(content.decode("utf-8", errors="replace"))
        blocks = [
            TextBlock.build(
                document_id=context.document_id,
                unit_index=1,
                block_index=index,
                source_path=path,
                text=text,
                kind=BlockKind.PARAGRAPH,
            )
            for index, (path, text) in enumerate(parser.blocks)
        ]
        if not blocks:
            raise ValueError("HTML contains no visible rule text")
        return NormalizedDocument(
            id=context.document_id,
            filename=context.filename,
            media_type=context.media_type,
            content_sha256=context.content_sha256,
            units=[DocumentUnit(index=1, kind=UnitKind.FLOW, blocks=blocks)],
        )

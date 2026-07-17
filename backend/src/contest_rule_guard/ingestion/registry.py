from collections.abc import Iterable
from pathlib import Path

from contest_rule_guard.ingestion.ports import DocumentParser


class UnsupportedDocumentError(ValueError):
    pass


class ParserRegistry:
    def __init__(self, parsers: Iterable[DocumentParser]) -> None:
        self._parsers = tuple(parsers)

    def resolve(self, media_type: str, filename: str) -> DocumentParser:
        for parser in self._parsers:
            if media_type in parser.media_types:
                return parser

        suffix = Path(filename).suffix.lower()
        for parser in self._parsers:
            if suffix in parser.extensions:
                return parser

        raise UnsupportedDocumentError(f"unsupported document: {media_type} {suffix}")

from collections.abc import Iterable
from pathlib import Path

from contest_rule_guard.ingestion.ports import DocumentParser


class UnsupportedDocumentError(ValueError):
    pass


class ParserRegistry:
    def __init__(self, parsers: Iterable[DocumentParser]) -> None:
        self._parsers = tuple(parsers)
        seen_media: dict[str, str] = {}
        seen_ext: dict[str, str] = {}
        for parser in self._parsers:
            cls_name = type(parser).__name__
            for mt in parser.media_types:
                if mt in seen_media:
                    import warnings
                    warnings.warn(
                        f"Duplicate media type '{mt}' registered by {cls_name} "
                        f"(previously registered by {seen_media[mt]}); "
                        f"the first registration will be used",
                        stacklevel=2,
                    )
                else:
                    seen_media[mt] = cls_name
            for ext in parser.extensions:
                if ext in seen_ext:
                    import warnings
                    warnings.warn(
                        f"Duplicate extension '{ext}' registered by {cls_name} "
                        f"(previously registered by {seen_ext[ext]}); "
                        f"the first registration will be used",
                        stacklevel=2,
                    )
                else:
                    seen_ext[ext] = cls_name

    def resolve(self, media_type: str, filename: str) -> DocumentParser:
        for parser in self._parsers:
            if media_type in parser.media_types:
                return parser

        suffix = Path(filename).suffix.lower()
        for parser in self._parsers:
            if suffix in parser.extensions:
                return parser

        raise UnsupportedDocumentError(f"unsupported document: {media_type} {suffix}")

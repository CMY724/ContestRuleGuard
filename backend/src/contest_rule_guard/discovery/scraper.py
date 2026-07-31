"""Active evidence discovery: scrape competition official sites for rules."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID

import httpx

from contest_rule_guard.ingestion.models import NormalizedDocument, ParseContext
from contest_rule_guard.ingestion.registry import ParserRegistry


@dataclass
class DiscoveredPage:
    url: str
    title: str
    document: NormalizedDocument


class DiscoveryScraper:
    """Fetches competition notice pages and extracts rule-bearing text."""

    USER_AGENT = "ContestRuleGuard/0.1 (academic-research; +https://github.com/CMY724/ContestRuleGuard)"

    def __init__(self, timeout_s: float = 30) -> None:
        self._client = httpx.AsyncClient(
            headers={"User-Agent": self.USER_AGENT},
            timeout=timeout_s,
            follow_redirects=True,
        )

    async def discover(
        self,
        urls: list[str],
        parser_registry: ParserRegistry,
    ) -> list[DiscoveredPage]:
        results: list[DiscoveredPage] = []
        html_parser = parser_registry.resolve("text/html", "page.html")

        async def fetch_one(url: str) -> None:
            try:
                response = await self._client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "text/html")
                content = response.content
                context = ParseContext.from_upload(
                    document_id=UUID(int=hash(url) & 0xFFFFFFFFFFFFFFFF),
                    filename=url.rsplit("/", 1)[-1] or "index.html",
                    media_type=content_type.split(";")[0].strip(),
                    content=content,
                )
                doc = html_parser.parse(content, context)
                title = url
                results.append(DiscoveredPage(url=url, title=title, document=doc))
            except Exception:
                pass  # Skip failed pages silently

        await asyncio.gather(*[fetch_one(url) for url in urls])
        return results

    async def close(self) -> None:
        await self._client.aclose()

import pytest

from contest_rule_guard.discovery.scraper import DiscoveryScraper


@pytest.mark.asyncio
async def test_scraper_creates_and_closes() -> None:
    scraper = DiscoveryScraper(timeout_s=5)
    assert scraper._client is not None
    await scraper.close()


def test_discovered_page_dataclass() -> None:
    from uuid import uuid4

    from contest_rule_guard.discovery.scraper import DiscoveredPage
    from contest_rule_guard.ingestion.models import (
        BlockKind,
        DocumentUnit,
        NormalizedDocument,
        TextBlock,
        UnitKind,
    )
    doc_id = uuid4()
    doc = NormalizedDocument(
        id=doc_id, filename="test.html", media_type="text/html",
        content_sha256="a" * 64,
        units=[DocumentUnit(index=1, kind=UnitKind.FLOW, blocks=[
            TextBlock.build(document_id=doc_id, unit_index=1, block_index=0,
                          source_path="p[0]", text="rule text", kind=BlockKind.PARAGRAPH)
        ])]
    )
    page = DiscoveredPage(url="https://example.com", title="Test", document=doc)
    assert page.url == "https://example.com"
    assert page.document.id == doc_id

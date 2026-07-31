# backend/tests/unit/ingestion/test_html_parser.py
from uuid import uuid4

from contest_rule_guard.ingestion.models import BlockKind, ParseContext, UnitKind
from contest_rule_guard.ingestion.parsers.html import HtmlParser


_HTML_TEXT = """\
<!DOCTYPE html>
<html>
<head><title>竞赛规则</title></head>
<body>
  <h1>报名截止</h1>
  <p>截止时间为 <script>evil()</script>2026年9月25日</p>
  <style>.hidden{}</style>
  <li>团队人数 1-3</li>
  <a href="http://example.com">详细规则</a>
</body>
</html>"""


def make_html() -> bytes:
    return _HTML_TEXT.encode("utf-8")


def test_html_parser_extracts_visible_blocks_and_link_text() -> None:
    content = make_html()
    context = ParseContext.from_upload(
        document_id=uuid4(),
        filename="rules.html",
        media_type="text/html",
        content=content,
    )
    parsed = HtmlParser().parse(content, context)
    assert parsed.units[0].kind is UnitKind.FLOW
    texts = [block.text for block in parsed.units[0].blocks]
    assert "竞赛规则" in texts
    assert "报名截止" in texts
    assert "截止时间为 2026年9月25日" in texts
    assert "团队人数 1-3" in texts
    assert "详细规则 [href=http://example.com]" in texts
    assert "evil()" not in " ".join(texts)
    assert "hidden" not in " ".join(texts)
    assert parsed.units[0].blocks[0].source_path.startswith("html.")

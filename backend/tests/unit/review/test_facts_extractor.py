"""Tests for FactsExtractor."""

from contest_rule_guard.ingestion.models import (
    BlockKind, DocumentUnit, NormalizedDocument, TextBlock, UnitKind,
)
from contest_rule_guard.review.facts import SubmissionFacts
from contest_rule_guard.review.facts_extractor import FactsExtractor


def _make_doc(filename="test.pdf", media_type="application/pdf", texts=None):
    if texts is None:
        texts = ["Hello world"]
    from uuid import uuid4
    doc_id = uuid4()
    blocks = []
    for i, t in enumerate(texts):
        blocks.append(TextBlock(
            id=uuid4(), unit_index=1, block_index=i,
            source_path=filename, text=t, kind=BlockKind.PARAGRAPH,
        ))
    unit = DocumentUnit(index=1, kind=UnitKind.PAGE, blocks=blocks)
    return NormalizedDocument(
        id=doc_id, filename=filename, media_type=media_type,
        content_sha256="a" * 64, units=[unit],
    )


def test_extract_empty_documents():
    facts = FactsExtractor.extract([])
    assert facts.submission_text == ""
    assert facts.files == []
    assert facts.current_time is not None


def test_extract_single_document():
    doc = _make_doc("report.pdf", "application/pdf", ["Line 1", "Line 2"])
    facts = FactsExtractor.extract([doc])
    assert len(facts.files) == 1
    assert facts.files[0].name == "report.pdf"
    assert facts.files[0].format == "pdf"
    assert facts.files[0].page_count == 1
    assert "Line 1" in facts.submission_text
    assert "Line 2" in facts.submission_text


def test_extract_multiple_documents():
    docs = [
        _make_doc("a.pdf", "application/pdf", ["A"]),
        _make_doc("b.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ["B"]),
    ]
    facts = FactsExtractor.extract(docs)
    assert len(facts.files) == 2
    assert facts.files[0].format == "pdf"
    assert "docx" in facts.files[1].format or "wordprocessingml" in facts.files[1].format
    assert "A" in facts.submission_text
    assert "B" in facts.submission_text


def test_merge_overrides():
    base = SubmissionFacts(team_member_count=0)
    merged = FactsExtractor.merge(base, {"team_member_count": 3, "eligibility_met": True})
    assert merged.team_member_count == 3
    assert merged.eligibility_met is True


def test_merge_ignores_none():
    base = SubmissionFacts(team_member_count=2)
    merged = FactsExtractor.merge(base, {"team_member_count": None})
    assert merged.team_member_count == 2  # unchanged


def test_merge_unknown_field():
    base = SubmissionFacts()
    merged = FactsExtractor.merge(base, {"nonexistent": 42})
    assert not hasattr(merged, "nonexistent")

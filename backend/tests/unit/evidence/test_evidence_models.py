from uuid import uuid4

import pytest
from pydantic import ValidationError

from contest_rule_guard.evidence.models import EvidenceSpan, FieldEvidenceBinding


def test_evidence_span_id_is_deterministic() -> None:
    doc_id = uuid4()
    block_id = uuid4()
    first = EvidenceSpan.build(
        document_id=doc_id,
        block_id=block_id,
        field_path="/payload/action",
        quote="???????2026?9?25?",
        start_char=0,
        end_char=15,
        source_tier="primary",
        stage="school",
        document_sha256="a" * 64,
    )
    second = EvidenceSpan.build(
        document_id=doc_id,
        block_id=block_id,
        field_path="/payload/action",
        quote="???????2026?9?25?",
        start_char=0,
        end_char=15,
        source_tier="primary",
        stage="school",
        document_sha256="a" * 64,
    )
    assert first.id == second.id
    assert first.quote == "???????2026?9?25?"


def test_evidence_span_requires_non_empty_quote() -> None:
    with pytest.raises(ValidationError):
        EvidenceSpan(
            document_id=uuid4(),
            block_id=uuid4(),
            field_path="/payload/action",
            quote="",
            start_char=0,
            end_char=5,
            source_tier="primary",
            stage="school",
            document_sha256="a" * 64,
        )


def test_field_evidence_binding_requires_at_least_one_evidence() -> None:
    with pytest.raises(ValidationError):
        FieldEvidenceBinding(
            field_path="/payload/action",
            evidence_ids=[],
            quote="some evidence",
        )


def test_evidence_span_quote_is_stripped() -> None:
    span = EvidenceSpan(
        document_id=uuid4(),
        block_id=uuid4(),
        field_path="/payload/action",
        quote="  2026-09-25  ",
        start_char=0,
        end_char=10,
        source_tier="primary",
        stage="school",
        document_sha256="a" * 64,
    )
    assert span.quote == "2026-09-25"

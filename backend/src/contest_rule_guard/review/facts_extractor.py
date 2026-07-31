"""Auto-extract SubmissionFacts from uploaded project documents."""

from datetime import UTC, datetime

from contest_rule_guard.ingestion.models import NormalizedDocument
from contest_rule_guard.review.facts import FileFact, SubmissionFacts


class FactsExtractor:
    """Extracts baseline facts from parsed documents.

    Auto-extractable facts:
      - submission_text: all text blocks concatenated
      - files: one FileFact per document (name, format, page count)
      - current_time: now (default)

    Manual facts (must be supplied by user via API):
      - team_member_count
      - eligibility_met
      - field_values
      - rule_results
    """

    @staticmethod
    def extract(documents: list[NormalizedDocument]) -> SubmissionFacts:
        all_text_parts: list[str] = []
        file_facts: list[FileFact] = []

        for doc in documents:
            fmt = doc.media_type.split("/")[-1] if "/" in doc.media_type else doc.media_type
            page_count = len(doc.units)
            file_facts.append(FileFact(
                name=doc.filename,
                size_bytes=0,
                format=fmt,
                page_count=page_count,
            ))
            for unit in doc.units:
                for block in unit.blocks:
                    all_text_parts.append(block.text)

        return SubmissionFacts(
            current_time=datetime.now(UTC),
            files=file_facts,
            submission_text=chr(10).join(all_text_parts),
        )

    @staticmethod
    def merge(base: SubmissionFacts, overrides: dict) -> SubmissionFacts:
        """Merge manual overrides into auto-extracted facts."""
        for field, value in overrides.items():
            if value is not None and hasattr(base, field):
                setattr(base, field, value)
        return base

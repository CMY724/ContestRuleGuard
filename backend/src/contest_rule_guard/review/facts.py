"""Submission facts model — consumed by the rule compiler and review engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FileFact(BaseModel):
    """Metadata about a single submitted file."""

    name: str
    size_bytes: int
    format: str = ""  # e.g. "pdf", "mp4", "zip"
    page_count: int | None = None
    duration_seconds: int | None = None


class SubmissionFacts(BaseModel):
    """Facts extracted from a user's competition submission.

    These are fed to compile_rule() so the compiler can evaluate
    every rule type against real data.
    """

    current_time: datetime | None = None
    team_member_count: int | None = None
    files: list[FileFact] = Field(default_factory=list)
    field_values: dict[str, Any] = Field(default_factory=dict)
    submission_text: str = ""
    eligibility_met: bool | None = None
    # For DependencyRule: {rule_id (str): passed (bool)}
    rule_results: dict[str, bool] = Field(default_factory=dict)

"""Model provider protocol and fake provider for testing."""

from __future__ import annotations

from typing import Any, Protocol


class ModelProvider(Protocol):
    """Protocol for AI model providers that extract rules from evidence."""

    async def extract_rules(
        self,
        evidence_texts: list[str],
        context: dict[str, Any],
        model_policy: dict[str, Any],
    ) -> dict[str, Any]: ...


class FakeModelProvider:
    """In-memory provider for testing. Set payload before calling."""

    def __init__(self) -> None:
        self.payload: dict[str, Any] = {}

    async def extract_rules(
        self,
        evidence_texts: list[str],
        context: dict[str, Any],
        model_policy: dict[str, Any],
    ) -> dict[str, Any]:
        return self.payload

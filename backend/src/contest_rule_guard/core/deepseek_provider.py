"""DeepSeek model provider for ContestRule extraction."""

from __future__ import annotations

import json
from typing import Any, cast

import httpx

from contest_rule_guard.rules.prompts import RULE_EXTRACTION_SYSTEM_PROMPT


class DeepSeekProvider:
    """Calls DeepSeek API (OpenAI-compatible) to extract ContestRules from evidence."""

    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout_s: float = 120,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout_s,
        )

    async def extract_rules(
        self,
        evidence_texts: list[str],
        context: dict[str, Any],
        model_policy: dict[str, Any],
    ) -> dict[str, Any]:
        separator = "\n\n---\n\n"
        evidence_block = separator.join(
            f"[Evidence {i}]\n{text}"
            for i, text in enumerate(evidence_texts, 1)
        )
        context_block = json.dumps(context, ensure_ascii=False, indent=2)

        user_message = (
            f"## Competition Context\n{context_block}\n\n"
            f"## Evidence Texts\n{evidence_block}\n\n"
            "Extract all contest rules from the evidence above "
            "as a JSON object with a \"rules\" array. "
            "Each rule must have a \"rule_type\" field set to one of: "
            "deadline, eligibility, team_size, file_required, "
            "file_constraint, consistency, anonymity, dependency."
        )

        response = await self._client.post(
            self.BASE_URL,
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": RULE_EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "temperature": float(model_policy.get("temperature", 0.1)),
                "max_tokens": int(model_policy.get("max_tokens", 4096)),
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        body = response.json()
        content = body["choices"][0]["message"]["content"]
        result = cast(dict[str, Any], json.loads(content))
        for rule in result.get("rules", []):
            rt = rule.get("rule_type", "")
            if rt == "team":
                rule["rule_type"] = "team_size"
            # Fix null fields to suitable defaults
            for key in ("allowed_formats", "prohibited_patterns", "bindings", "artifact_kinds"):
                if rule.get(key) is None:
                    rule[key] = []
            if rule.get("scope") and rule["scope"].get("artifact_kinds") is None:
                rule["scope"]["artifact_kinds"] = []
        return result

    async def close(self) -> None:
        await self._client.aclose()

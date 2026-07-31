import pytest

from contest_rule_guard.core.deepseek_provider import DeepSeekProvider


@pytest.mark.asyncio
async def test_deepseek_provider_structure() -> None:
    provider = DeepSeekProvider(api_key="sk-test")
    assert provider._model == "deepseek-chat"
    await provider.close()


@pytest.mark.asyncio
async def test_deepseek_provider_custom_model() -> None:
    provider = DeepSeekProvider(api_key="sk-test", model="deepseek-reasoner")
    assert provider._model == "deepseek-reasoner"
    await provider.close()


def test_prompt_template_covers_all_rule_types() -> None:
    from contest_rule_guard.rules.prompts import RULE_EXTRACTION_SYSTEM_PROMPT
    p = RULE_EXTRACTION_SYSTEM_PROMPT.lower()
    assert "contest regulation" in p
    for rt in ("deadline", "eligibility", "team_size", "file_required",
               "file_constraint", "consistency", "anonymity", "dependency"):
        assert rt in p, f"Missing rule type: {rt}"

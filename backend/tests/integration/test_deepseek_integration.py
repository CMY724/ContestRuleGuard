import os

import pytest


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("CRG_DEEPSEEK_API_KEY"),
    reason="CRG_DEEPSEEK_API_KEY not set",
)
async def test_deepseek_extracts_rules_from_real_evidence() -> None:
    from contest_rule_guard.core.deepseek_provider import DeepSeekProvider

    provider = DeepSeekProvider(api_key=os.environ["CRG_DEEPSEEK_API_KEY"])
    try:
        result = await provider.extract_rules(
            evidence_texts=[
                "第一条：参赛选手必须为在校全日制本科生。第二条：每支队伍人数为1-3人。",
                "校赛材料提交截止时间：2026年9月25日17:00（北京时间）。",
            ],
            context={
                "competition_name": "全球人工智能算法精英大赛",
                "year": 2026,
                "stage": "school",
                "track": "AI",
            },
            model_policy={"temperature": 0.1, "max_tokens": 2048},
        )
        assert "rules" in result
        assert len(result["rules"]) >= 1
        rule_types = {r["rule_type"] for r in result["rules"]}
        valid_types = {
            "deadline", "eligibility", "team_size", "file_required",
            "file_constraint", "consistency", "anonymity", "dependency",
        }
        assert rule_types.issubset(valid_types)
    finally:
        await provider.close()

"""Strategy Agent (Documento 05, secao 8)."""

from __future__ import annotations

import json

from app.agents.runtime import run_structured_agent
from app.agents.schemas import StrategyAgentOutput
from app.gateways.llm import LLMGateway
from app.models.channel_dna_version import ChannelDNAVersion
from app.models.content_strategy import ContentStrategy
from app.models.strategy_rule import StrategyRule

AGENT_ID = "strategy_agent"
VERSION = "v1"


def _build_user_prompt(
    *,
    dna: ChannelDNAVersion,
    audience_profile_json: dict | None,
    existing_strategy: ContentStrategy | None,
    active_rules: list[StrategyRule],
) -> str:
    payload = {
        "channel_dna": {
            "classification": dna.classification_json,
            "content_patterns": dna.content_patterns_json,
            "formats": dna.formats_json,
            "performance_patterns": dna.performance_patterns_json,
            "brand_rules": dna.brand_rules_json,
            "publishing_patterns": dna.publishing_patterns_json,
            "restrictions": dna.restrictions_json,
        },
        "audience_profile": audience_profile_json,
        "existing_strategy": (
            {
                "objective": existing_strategy.objective,
                "shorts_ratio": existing_strategy.shorts_ratio,
                "long_form_ratio": existing_strategy.long_form_ratio,
                "experimental_ratio": existing_strategy.experimental_ratio,
                "recommended_frequency": existing_strategy.recommended_frequency_json,
            }
            if existing_strategy
            else None
        ),
        "explicit_rules": [
            {"rule_type": rule.rule_type, "rule": rule.rule_json} for rule in active_rules
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_strategy_agent(
    gateway: LLMGateway,
    *,
    dna: ChannelDNAVersion,
    audience_profile_json: dict | None,
    existing_strategy: ContentStrategy | None,
    active_rules: list[StrategyRule],
) -> StrategyAgentOutput:
    user_prompt = _build_user_prompt(
        dna=dna,
        audience_profile_json=audience_profile_json,
        existing_strategy=existing_strategy,
        active_rules=active_rules,
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=StrategyAgentOutput,
    )

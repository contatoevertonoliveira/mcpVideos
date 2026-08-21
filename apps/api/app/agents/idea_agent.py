"""Idea Agent (Documento 05, secao 10).

Documento 05 lists "Recent Publications", "Planned Content", "Learned
Rules" and "Trend Signals" as inputs too. Planned Content (Calendar,
Fase 10), Learned Rules (Learning Engine, Fase 19) and Trend Signals
(Trend Researcher agent, not yet built) don't exist yet - omitted rather
than faked, same pattern as every other agent module so far skipping
inputs from not-yet-implemented phases.
"""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.agents.runtime import run_structured_agent
from app.agents.schemas import IdeaAgentOutput
from app.gateways.llm import LLMGateway
from app.models.channel_dna_version import ChannelDNAVersion
from app.models.content_strategy import ContentStrategy
from app.models.source_video import SourceVideo

AGENT_ID = "idea_agent"
VERSION = "v1"


def _build_user_prompt(
    *,
    dna: ChannelDNAVersion,
    audience_profile_json: dict | None,
    strategy: ContentStrategy,
    recent_videos: list[SourceVideo],
    existing_idea_titles: list[str],
) -> str:
    payload = {
        "channel_dna": {
            "classification": dna.classification_json,
            "content_patterns": dna.content_patterns_json,
            "brand_rules": dna.brand_rules_json,
            "restrictions": dna.restrictions_json,
        },
        "audience_profile": audience_profile_json,
        "active_strategy": {
            "objective": strategy.objective,
            "shorts_ratio": strategy.shorts_ratio,
            "long_form_ratio": strategy.long_form_ratio,
            "recommended_frequency": strategy.recommended_frequency_json,
        },
        "recent_publications": [
            {"title": video.title, "video_type": video.video_type.value} for video in recent_videos
        ],
        "existing_idea_titles": existing_idea_titles,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_idea_agent(
    gateway: LLMGateway,
    *,
    dna: ChannelDNAVersion,
    audience_profile_json: dict | None,
    strategy: ContentStrategy,
    recent_videos: list[SourceVideo],
    existing_idea_titles: list[str],
    session: Session,
    organization_id: uuid.UUID,
    channel_id: uuid.UUID | None = None,
    workflow_run_id: uuid.UUID | None = None,
    workflow_step_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
) -> IdeaAgentOutput:
    user_prompt = _build_user_prompt(
        dna=dna,
        audience_profile_json=audience_profile_json,
        strategy=strategy,
        recent_videos=recent_videos,
        existing_idea_titles=existing_idea_titles,
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=IdeaAgentOutput,
        session=session,
        organization_id=organization_id,
        channel_id=channel_id,
        workflow_run_id=workflow_run_id,
        workflow_step_id=workflow_step_id,
        correlation_id=correlation_id,
    )

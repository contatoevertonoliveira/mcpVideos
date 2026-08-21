"""Opportunity Evaluator agent (Documento 05, secao 11).

"Performance History" is approximated with the channel's latest metric
snapshot per video (same data ChannelSyncService/AudienceAnalyst already
use). "Production Constraints" doesn't exist as a queryable entity yet
(no budget/cost controller, Fase 14+) - omitted.
"""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.agents.runtime import run_structured_agent
from app.agents.schemas import OpportunityEvaluatorOutput
from app.gateways.llm import LLMGateway
from app.models.channel_dna_version import ChannelDNAVersion
from app.models.content_idea import ContentIdea
from app.models.content_strategy import ContentStrategy
from app.models.source_video_metric import SourceVideoMetric

AGENT_ID = "opportunity_evaluator"
VERSION = "v1"


def _build_user_prompt(
    *,
    idea: ContentIdea,
    dna: ChannelDNAVersion,
    strategy: ContentStrategy,
    audience_profile_json: dict | None,
    latest_metrics_by_video_id: dict[uuid.UUID, SourceVideoMetric],
) -> str:
    performance_history = [
        {"views": metric.views, "likes": metric.likes, "comments": metric.comments}
        for metric in latest_metrics_by_video_id.values()
    ]
    payload = {
        "idea": {
            "title": idea.title,
            "summary": idea.summary,
            "recommended_format": idea.recommended_format,
            "idea_type": idea.idea_type,
            "origin": idea.origin.value,
        },
        "channel_dna": {
            "classification": dna.classification_json,
            "content_patterns": dna.content_patterns_json,
            "performance_patterns": dna.performance_patterns_json,
            "brand_rules": dna.brand_rules_json,
            "restrictions": dna.restrictions_json,
        },
        "active_strategy": {
            "objective": strategy.objective,
            "shorts_ratio": strategy.shorts_ratio,
            "long_form_ratio": strategy.long_form_ratio,
        },
        "audience_profile": audience_profile_json,
        "performance_history": performance_history,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_opportunity_evaluator(
    gateway: LLMGateway,
    *,
    idea: ContentIdea,
    dna: ChannelDNAVersion,
    strategy: ContentStrategy,
    audience_profile_json: dict | None,
    latest_metrics_by_video_id: dict[uuid.UUID, SourceVideoMetric],
    session: Session,
    organization_id: uuid.UUID,
    channel_id: uuid.UUID | None = None,
    workflow_run_id: uuid.UUID | None = None,
    workflow_step_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
) -> OpportunityEvaluatorOutput:
    user_prompt = _build_user_prompt(
        idea=idea,
        dna=dna,
        strategy=strategy,
        audience_profile_json=audience_profile_json,
        latest_metrics_by_video_id=latest_metrics_by_video_id,
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=OpportunityEvaluatorOutput,
        session=session,
        organization_id=organization_id,
        channel_id=channel_id,
        workflow_run_id=workflow_run_id,
        workflow_step_id=workflow_step_id,
        correlation_id=correlation_id,
    )

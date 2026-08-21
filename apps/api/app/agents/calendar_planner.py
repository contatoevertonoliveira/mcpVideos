"""Calendar Planner agent (Documento 05, secao 12).

"Clusters" (Documento 05 sec. 12 input) is omitted - content_clusters
exists as a table since Fase 09 but nothing populates it yet (documented
scope trim in that phase's report). "Content Mix" is already carried by
the active strategy's shorts_ratio/long_form_ratio, passed as part of
``active_strategy`` rather than a separate input.
"""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.agents.runtime import run_structured_agent
from app.agents.schemas import CalendarPlannerOutput
from app.gateways.llm import LLMGateway
from app.models.calendar_item import CalendarItem
from app.models.content_idea import ContentIdea
from app.models.content_opportunity import ContentOpportunity
from app.models.content_strategy import ContentStrategy
from app.models.publishing_slot import PublishingSlot

AGENT_ID = "calendar_planner"
VERSION = "v1"


def _build_user_prompt(
    *,
    strategy: ContentStrategy,
    publishing_slots: list[PublishingSlot],
    candidates: list[tuple[ContentOpportunity, ContentIdea]],
    existing_calendar_items: list[CalendarItem],
) -> str:
    payload = {
        "active_strategy": {
            "objective": strategy.objective,
            "shorts_ratio": strategy.shorts_ratio,
            "long_form_ratio": strategy.long_form_ratio,
            "recommended_frequency": strategy.recommended_frequency_json,
        },
        "publishing_slots": [
            {
                "day_of_week": slot.day_of_week.value,
                "local_time": slot.local_time.isoformat(),
                "content_type": slot.content_type.value,
                "priority": slot.priority,
            }
            for slot in publishing_slots
        ],
        "approved_opportunities": [
            {
                "opportunity_id": str(opportunity.id),
                "idea_title": idea.title,
                "recommended_format": idea.recommended_format,
                "content_pillar": idea.idea_type,
                "opportunity_score": opportunity.opportunity_score,
            }
            for opportunity, idea in candidates
        ],
        "existing_calendar": [
            {
                "planned_at": item.planned_at.isoformat(),
                "content_type": item.content_type.value,
                "status": item.status.value,
            }
            for item in existing_calendar_items
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_calendar_planner(
    gateway: LLMGateway,
    *,
    strategy: ContentStrategy,
    publishing_slots: list[PublishingSlot],
    candidates: list[tuple[ContentOpportunity, ContentIdea]],
    existing_calendar_items: list[CalendarItem],
    session: Session,
    organization_id: uuid.UUID,
    channel_id: uuid.UUID | None = None,
    workflow_run_id: uuid.UUID | None = None,
    workflow_step_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
) -> CalendarPlannerOutput:
    user_prompt = _build_user_prompt(
        strategy=strategy,
        publishing_slots=publishing_slots,
        candidates=candidates,
        existing_calendar_items=existing_calendar_items,
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=CalendarPlannerOutput,
        session=session,
        organization_id=organization_id,
        channel_id=channel_id,
        workflow_run_id=workflow_run_id,
        workflow_step_id=workflow_step_id,
        correlation_id=correlation_id,
    )

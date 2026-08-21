from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.agents.calendar_planner import run_calendar_planner
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.calendar_item import CalendarItem
from app.models.calendar_recommendation import CalendarRecommendation
from app.models.content_idea import ContentIdea
from app.models.content_opportunity import ContentOpportunity
from app.models.enums import (
    AuditActorType,
    CalendarItemSource,
    CalendarItemStatus,
    IdeaStatus,
    SourceVideoType,
)
from app.repositories.calendar_item import CalendarItemRepository
from app.repositories.calendar_recommendation import CalendarRecommendationRepository
from app.repositories.channel import ChannelRepository
from app.repositories.content_idea import ContentIdeaRepository
from app.repositories.content_opportunity import ContentOpportunityRepository
from app.repositories.content_pillar import ContentPillarRepository
from app.repositories.content_strategy import ContentStrategyRepository
from app.repositories.publishing_slot import PublishingSlotRepository
from app.services.audit import AuditService
from app.services.calendar_balance import (
    PlannedItem,
    build_format_balance,
    build_pillar_balance,
    detect_conflicts,
)

_VALID_CONTENT_TYPES = {content_type.value for content_type in SourceVideoType}


class CalendarPlanningService:
    """Documento 05, secao 12 (Calendar Planner); Documento 10 Fase 10.
    Transforms already human-approved ideas (Fase 09's ``ContentIdea.
    APPROVED``, this project's closest match to Documento 05's "Approved
    Opportunities") into suggested calendar items."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.strategies = ContentStrategyRepository(session)
        self.pillars = ContentPillarRepository(session)
        self.slots = PublishingSlotRepository(session)
        self.ideas = ContentIdeaRepository(session)
        self.opportunities = ContentOpportunityRepository(session)
        self.calendar_items = CalendarItemRepository(session)
        self.recommendations = CalendarRecommendationRepository(session)
        self.audit = AuditService(session)

    async def generate_recommendations(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        correlation_id: uuid.UUID | None = None,
    ) -> CalendarRecommendation:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        active_strategy = self.strategies.get_active(channel_id, organization_id=organization_id)
        if active_strategy is None:
            raise DomainError(
                "Channel has no active content strategy yet - approve one first",
                code="CHANNEL_STRATEGY_NOT_READY",
            )

        active_slots = self.slots.list_by_channel(
            channel_id=channel_id, organization_id=organization_id, active_only=True
        )
        strategy_pillars = self.pillars.list_by_strategy(
            active_strategy.id, organization_id=organization_id
        )
        existing_items = self.calendar_items.list_active_by_channel(
            channel_id=channel_id, organization_id=organization_id
        )

        candidates = self._load_candidates(channel_id=channel_id, organization_id=organization_id)
        if not candidates:
            raise DomainError(
                "No approved ideas without a calendar item yet - approve an idea first",
                code="NO_CALENDAR_CANDIDATES",
            )

        output = await run_calendar_planner(
            self.llm_gateway,
            strategy=active_strategy,
            publishing_slots=active_slots,
            candidates=candidates,
            existing_calendar_items=existing_items,
        )

        idea_by_opportunity_id = {str(opportunity.id): idea for opportunity, idea in candidates}
        created_items: list[CalendarItem] = []
        batch_planned: list[PlannedItem] = []
        for recommended in output.recommended_items:
            idea = idea_by_opportunity_id.get(recommended.opportunity_id)
            if idea is None:
                # Agent referenced an unknown/stale opportunity_id - skip
                # rather than fail the whole batch over one bad entry.
                continue
            try:
                planned_at = datetime.fromisoformat(recommended.planned_at)
            except ValueError:
                continue

            content_type = (
                recommended.format
                if recommended.format in _VALID_CONTENT_TYPES
                else (idea.recommended_format or SourceVideoType.SHORT.value)
            )
            if content_type not in _VALID_CONTENT_TYPES:
                content_type = SourceVideoType.SHORT.value

            item = CalendarItem(
                organization_id=organization_id,
                channel_id=channel_id,
                idea_id=idea.id,
                content_type=SourceVideoType(content_type),
                planned_at=planned_at,
                status=CalendarItemStatus.SUGGESTED,
                source=CalendarItemSource.AI,
            )
            self.calendar_items.add(item)
            created_items.append(item)
            batch_planned.append(
                PlannedItem(
                    content_type=content_type, planned_at=planned_at, content_pillar=idea.idea_type
                )
            )

        balance_report = {
            "format_balance": build_format_balance(batch_planned, active_strategy),
            "pillar_balance": build_pillar_balance(batch_planned, strategy_pillars),
        }
        existing_planned = [
            PlannedItem(content_type=item.content_type.value, planned_at=item.planned_at)
            for item in existing_items
        ]
        conflicts = detect_conflicts(batch_planned, existing_planned)

        recommendation = CalendarRecommendation(
            organization_id=organization_id,
            channel_id=channel_id,
            balance_report_json=balance_report,
            conflicts_json=conflicts,
            generated_by_agent_run_id=correlation_id,
        )
        self.recommendations.add(recommendation)

        for item in created_items:
            item.calendar_recommendation_id = recommendation.id
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="calendar.recommendation.created",
            resource_type="channel",
            resource_id=channel_id,
            metadata={"items_created": len(created_items), "conflicts": len(conflicts)},
        )
        return recommendation

    def _load_candidates(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[tuple[ContentOpportunity, ContentIdea]]:
        approved_ideas = [
            idea
            for idea in self.ideas.list_by_channel(
                channel_id=channel_id, organization_id=organization_id, limit=200
            )
            if idea.status == IdeaStatus.APPROVED
        ]
        candidates: list[tuple[ContentOpportunity, ContentIdea]] = []
        for idea in approved_ideas:
            if (
                self.calendar_items.get_active_by_idea(idea.id, organization_id=organization_id)
                is not None
            ):
                continue
            opportunity = self.opportunities.get_latest_for_idea(
                idea.id, organization_id=organization_id
            )
            if opportunity is None:
                continue
            candidates.append((opportunity, idea))
        return candidates

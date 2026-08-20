from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.agents.opportunity_evaluator import run_opportunity_evaluator
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.content_opportunity import ContentOpportunity
from app.models.enums import AuditActorType, IdeaStatus, OpportunityStatus
from app.models.opportunity_score import OpportunityScore
from app.repositories.audience_profile import AudienceProfileRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.content_idea import ContentIdeaRepository
from app.repositories.content_opportunity import ContentOpportunityRepository
from app.repositories.content_strategy import ContentStrategyRepository
from app.repositories.opportunity_score import OpportunityScoreRepository
from app.repositories.source_video_metric import SourceVideoMetricRepository
from app.services.audit import AuditService
from app.services.opportunity_scoring import score_opportunity


class OpportunityEvaluationService:
    """Documento 05, secao 11 (Opportunity Evaluator); Documento 10 Fase
    09. The agent proposes raw component scores; this service (via
    ``opportunity_scoring.score_opportunity``) computes the weighted
    final score and the recommend/reject outcome in code - never trusts
    an LLM-provided final verdict (CLAUDE.md: agente propoe, service
    valida)."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.ideas = ContentIdeaRepository(session)
        self.dna_versions = ChannelDNAVersionRepository(session)
        self.strategies = ContentStrategyRepository(session)
        self.audience_profiles = AudienceProfileRepository(session)
        self.metrics = SourceVideoMetricRepository(session)
        self.opportunities = ContentOpportunityRepository(session)
        self.scores = OpportunityScoreRepository(session)
        self.audit = AuditService(session)

    async def evaluate_idea(
        self, *, idea_id: uuid.UUID, organization_id: uuid.UUID
    ) -> ContentOpportunity:
        idea = self.ideas.get_by_id(idea_id, organization_id=organization_id)
        if idea is None:
            raise NotFoundError("Idea not found", code="IDEA_NOT_FOUND")

        active_dna = self.dna_versions.get_active(idea.channel_id, organization_id=organization_id)
        if active_dna is None:
            raise DomainError("Channel has no active Channel DNA yet", code="CHANNEL_DNA_NOT_READY")
        active_strategy = self.strategies.get_active(
            idea.channel_id, organization_id=organization_id
        )
        if active_strategy is None:
            raise DomainError(
                "Channel has no active content strategy yet", code="CHANNEL_STRATEGY_NOT_READY"
            )
        audience_profile = self.audience_profiles.get_current(
            idea.channel_id, organization_id=organization_id
        )
        latest_metrics = self.metrics.list_latest_by_channel(
            channel_id=idea.channel_id, organization_id=organization_id
        )
        latest_metrics_by_video_id = {metric.source_video_id: metric for metric in latest_metrics}

        idea.status = IdeaStatus.EVALUATING
        self.session.flush()

        evaluation = await run_opportunity_evaluator(
            self.llm_gateway,
            idea=idea,
            dna=active_dna,
            strategy=active_strategy,
            audience_profile_json=audience_profile.profile_json if audience_profile else None,
            latest_metrics_by_video_id=latest_metrics_by_video_id,
        )
        result = score_opportunity(evaluation)

        opportunity = ContentOpportunity(
            organization_id=organization_id,
            channel_id=idea.channel_id,
            idea_id=idea.id,
            opportunity_score=result.final_score,
            recommended_format=idea.recommended_format,
            reasoning_summary=evaluation.reasoning_summary or None,
            status=(
                OpportunityStatus.RECOMMENDED if result.recommended else OpportunityStatus.REJECTED
            ),
        )
        self.opportunities.add(opportunity)

        for component in result.components:
            self.scores.add(
                OpportunityScore(
                    organization_id=organization_id,
                    opportunity_id=opportunity.id,
                    score_type=component.score_type,
                    score=component.score,
                    weight=component.weight,
                    weighted_score=component.weighted_score,
                    confidence=evaluation.confidence,
                    evidence_json={},
                )
            )

        idea.status = IdeaStatus.RECOMMENDED if result.recommended else IdeaStatus.REJECTED
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="opportunity.evaluated",
            resource_type="content_idea",
            resource_id=idea.id,
            metadata={
                "opportunity_score": result.final_score,
                "recommended": result.recommended,
            },
        )
        return opportunity

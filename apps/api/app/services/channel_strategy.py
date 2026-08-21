from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.strategy_agent import run_strategy_agent
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.content_pillar import ContentPillar
from app.models.content_strategy import ContentStrategy
from app.models.enums import AuditActorType, ContentStrategyStatus
from app.models.strategy_rule import StrategyRule
from app.repositories.audience_profile import AudienceProfileRepository
from app.repositories.channel import ChannelRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.content_pillar import ContentPillarRepository
from app.repositories.content_strategy import ContentStrategyRepository
from app.repositories.strategy_rule import StrategyRuleRepository
from app.services.audit import AuditService


class ChannelStrategyService:
    """Documento 05, secao 8 (Strategy Agent); Documento 10 Fase 08. Unlike
    ChannelDNAService (Fase 07), a generated strategy is never
    auto-activated - Documento 05 sec. 8 is explicit that the agent "nao
    pode ativar estrategia sozinho sem policy". ``approve`` is the only
    path from draft to active, and it is a human action."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.dna_versions = ChannelDNAVersionRepository(session)
        self.audience_profiles = AudienceProfileRepository(session)
        self.strategies = ContentStrategyRepository(session)
        self.pillars = ContentPillarRepository(session)
        self.rules = StrategyRuleRepository(session)
        self.audit = AuditService(session)

    async def generate_new_version(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        correlation_id: uuid.UUID | None = None,
    ) -> ContentStrategy:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        active_dna = self.dna_versions.get_active(channel_id, organization_id=organization_id)
        if active_dna is None:
            raise DomainError(
                "Channel has no active Channel DNA yet - generate one first",
                code="CHANNEL_DNA_NOT_READY",
            )
        audience_profile = self.audience_profiles.get_current(
            channel_id, organization_id=organization_id
        )
        existing_strategy = self.strategies.get_active(channel_id, organization_id=organization_id)
        active_rules = (
            self.rules.list_active_by_strategy(
                existing_strategy.id, organization_id=organization_id
            )
            if existing_strategy
            else []
        )

        output = await run_strategy_agent(
            self.llm_gateway,
            dna=active_dna,
            audience_profile_json=audience_profile.profile_json if audience_profile else None,
            existing_strategy=existing_strategy,
            active_rules=active_rules,
            session=self.session,
            organization_id=organization_id,
            channel_id=channel_id,
            correlation_id=correlation_id,
        )

        next_version = (
            self.strategies.get_latest_version_number(channel_id, organization_id=organization_id)
            + 1
        )
        new_strategy = ContentStrategy(
            organization_id=organization_id,
            channel_id=channel_id,
            name=f"Estrategia v{next_version}",
            version=next_version,
            status=ContentStrategyStatus.DRAFT,
            objective="; ".join(output.objectives)[:1000] or "Sem objetivo definido",
            shorts_ratio=output.content_mix.get("shorts_ratio", 0.0),
            long_form_ratio=output.content_mix.get("long_form_ratio", 0.0),
            experimental_ratio=output.experimental_ratio,
            recommended_frequency_json=output.publishing_frequency,
            strategy_json={
                "format_strategy": output.format_strategy,
                "recommendations": output.recommendations,
                "risks": output.risks,
                "confidence": output.confidence,
            },
            generated_by_agent_run_id=correlation_id,
        )
        self.strategies.add(new_strategy)

        for pillar in output.content_pillars:
            self.pillars.add(
                ContentPillar(
                    organization_id=organization_id,
                    channel_id=channel_id,
                    strategy_id=new_strategy.id,
                    name=pillar.name,
                    description=pillar.description or None,
                    target_ratio=pillar.target_ratio,
                    priority=pillar.priority,
                )
            )

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="strategy.candidate.created",
            resource_type="channel",
            resource_id=channel_id,
            metadata={"strategy_id": str(new_strategy.id), "version": next_version},
        )
        return new_strategy

    def approve(
        self,
        *,
        channel_id: uuid.UUID,
        strategy_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ContentStrategy:
        strategy = self.strategies.get_by_id(strategy_id, organization_id=organization_id)
        if strategy is None or strategy.channel_id != channel_id:
            raise NotFoundError("Strategy not found", code="STRATEGY_NOT_FOUND")
        if strategy.status != ContentStrategyStatus.DRAFT:
            raise DomainError(
                f"Strategy is already {strategy.status.value}, not draft",
                code="STRATEGY_NOT_DRAFT",
            )

        previous_active = self.strategies.get_active(channel_id, organization_id=organization_id)
        if previous_active is not None:
            previous_active.status = ContentStrategyStatus.ARCHIVED
            # Same reasoning as ChannelDNAService: both rows compete for the
            # "one active per channel" partial unique index, so the demotion
            # must be flushed before the promotion below.
            self.session.flush()

        strategy.status = ContentStrategyStatus.ACTIVE
        strategy.activated_at = datetime.now(UTC)
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="strategy.activated",
            resource_type="channel",
            resource_id=channel_id,
            metadata={"strategy_id": str(strategy.id), "version": strategy.version},
        )
        return strategy

    def add_rule(
        self,
        *,
        channel_id: uuid.UUID,
        strategy_id: uuid.UUID,
        organization_id: uuid.UUID,
        rule_type: str,
        rule_json: dict,
        priority: int = 0,
    ) -> StrategyRule:
        strategy = self.strategies.get_by_id(strategy_id, organization_id=organization_id)
        if strategy is None or strategy.channel_id != channel_id:
            raise NotFoundError("Strategy not found", code="STRATEGY_NOT_FOUND")

        rule = StrategyRule(
            organization_id=organization_id,
            strategy_id=strategy_id,
            rule_type=rule_type,
            rule_json=rule_json,
            priority=priority,
        )
        return self.rules.add(rule)

    def list_rules(
        self, *, strategy_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[StrategyRule]:
        return self.rules.list_by_strategy(strategy_id, organization_id=organization_id)

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.audience_analyst import run_audience_analyst
from app.agents.channel_analyst import run_channel_analyst
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.channel_dna_version import ChannelDNAVersion
from app.models.enums import AuditActorType, ChannelDNAStatus
from app.repositories.brand_profile import BrandProfileRepository
from app.repositories.channel import ChannelRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.source_playlist import SourcePlaylistRepository
from app.repositories.source_video import SourceVideoRepository
from app.repositories.source_video_metric import SourceVideoMetricRepository
from app.services.audit import AuditService


class ChannelDNAService:
    """Documento 03, secao 16; Documento 10 Fase 07. Synthesizes a new,
    immutable, versioned "editorial memory" snapshot from a fresh
    Channel Analyst + Audience Analyst run (the same agents from Fase 06,
    re-run here to capture their full structured output - Fase 06's
    ChannelProfile/AudienceProfile only persist a distilled summary, not
    enough to populate DNA's richer fields). Only the transition between
    versions (draft -> active -> superseded) is service-owned state;
    agents never write directly (CLAUDE.md: "agentes propoem, services
    validam")."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.videos = SourceVideoRepository(session)
        self.playlists = SourcePlaylistRepository(session)
        self.metrics = SourceVideoMetricRepository(session)
        self.dna_versions = ChannelDNAVersionRepository(session)
        self.brand_profiles = BrandProfileRepository(session)
        self.audit = AuditService(session)

    async def generate_new_version(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        correlation_id: uuid.UUID | None = None,
        workflow_run_id: uuid.UUID | None = None,
    ) -> ChannelDNAVersion:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        videos = self.videos.list_by_channel(
            channel_id=channel_id, organization_id=organization_id, limit=200
        )
        if not videos:
            raise DomainError(
                "Channel has no imported videos yet - run a sync first",
                code="CHANNEL_NOT_IMPORTED_YET",
            )
        playlists = self.playlists.list_by_channel(
            channel_id=channel_id, organization_id=organization_id, limit=200
        )
        latest_metrics = self.metrics.list_latest_by_channel(
            channel_id=channel_id, organization_id=organization_id
        )
        latest_metrics_by_video_id = {metric.source_video_id: metric for metric in latest_metrics}
        brand_profile = self.brand_profiles.get_by_channel(
            channel_id, organization_id=organization_id
        )

        channel_analysis = await run_channel_analyst(
            self.llm_gateway,
            channel=channel,
            videos=videos,
            playlists=playlists,
            existing_profile=None,
            session=self.session,
            organization_id=organization_id,
            channel_id=channel_id,
            correlation_id=correlation_id,
            workflow_run_id=workflow_run_id,
        )
        audience_analysis = await run_audience_analyst(
            self.llm_gateway,
            channel=channel,
            videos=videos,
            latest_metrics_by_video_id=latest_metrics_by_video_id,
            existing_profile=None,
            session=self.session,
            organization_id=organization_id,
            channel_id=channel_id,
            correlation_id=correlation_id,
            workflow_run_id=workflow_run_id,
        )

        next_version = (
            self.dna_versions.get_latest_version_number(channel_id, organization_id=organization_id)
            + 1
        )
        now = datetime.now(UTC)

        new_version = ChannelDNAVersion(
            organization_id=organization_id,
            channel_id=channel_id,
            version=next_version,
            status=ChannelDNAStatus.ACTIVE,
            classification_json=channel_analysis.classification,
            audience_json=audience_analysis.model_dump(mode="json", exclude={"confidence"}),
            formats_json={
                "format_patterns": channel_analysis.format_patterns,
                "format_preferences": audience_analysis.format_preferences,
            },
            content_patterns_json={"content_patterns": channel_analysis.content_patterns},
            performance_patterns_json={
                "high_performing_patterns": channel_analysis.high_performing_patterns,
                "low_performing_patterns": channel_analysis.low_performing_patterns,
                "anomalies": channel_analysis.anomalies,
            },
            brand_rules_json=(brand_profile.rules_json if brand_profile else {}),
            publishing_patterns_json={"publishing_patterns": channel_analysis.publishing_patterns},
            restrictions_json={
                "prohibited_elements": (
                    brand_profile.prohibited_elements_json if brand_profile else {}
                )
            },
            # No agent produces strategy recommendations yet - that's the
            # Strategy Agent's job (Fase 08). Left honestly empty rather
            # than fabricated (CLAUDE.md: no misleading placeholders).
            recommendations_json={},
            confidence=round((channel_analysis.confidence + audience_analysis.confidence) / 2, 4),
            generated_by_agent_run_id=correlation_id,
            activated_at=now,
        )

        previous_active = self.dna_versions.get_active(channel_id, organization_id=organization_id)
        if previous_active is not None:
            previous_active.status = ChannelDNAStatus.SUPERSEDED
            # Flushed separately, before inserting the new row: both rows
            # compete for the same "one active per channel" partial unique
            # index, and SQLAlchemy's flush ordering does not guarantee
            # this UPDATE is emitted before the INSERT otherwise.
            self.session.flush()

        self.dna_versions.add(new_version)

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="channel.dna.activated",
            resource_type="channel",
            resource_id=channel_id,
            metadata={"version": next_version, "confidence": new_version.confidence},
        )
        return new_version

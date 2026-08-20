from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.audience_analyst import run_audience_analyst
from app.agents.channel_analyst import run_channel_analyst
from app.agents.schemas import AudienceAnalystOutput, ChannelAnalystOutput
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.audience_profile import AudienceProfile
from app.models.channel_profile import ChannelProfile
from app.models.enums import AudienceProfileSource, AuditActorType
from app.repositories.audience_profile import AudienceProfileRepository
from app.repositories.channel import ChannelRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.channel_profile import ChannelProfileRepository
from app.repositories.source_playlist import SourcePlaylistRepository
from app.repositories.source_video import SourceVideoRepository
from app.repositories.source_video_metric import SourceVideoMetricRepository
from app.services.audit import AuditService
from app.tasks.channel_dna import dispatch_channel_dna


@dataclass
class ChannelIntelligenceResult:
    channel_profile: ChannelProfile
    audience_profile: AudienceProfile
    channel_analysis: ChannelAnalystOutput
    audience_analysis: AudienceAnalystOutput


class ChannelIntelligenceService:
    """Documento 05, secoes 6-7 (Channel Analyst / Audience Analyst);
    Documento 10 Fase 06. Agents propose structured analysis, this service
    validates preconditions and persists it - agents themselves never
    write to the database (CLAUDE.md: "agentes propoem, services
    validam")."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.videos = SourceVideoRepository(session)
        self.playlists = SourcePlaylistRepository(session)
        self.metrics = SourceVideoMetricRepository(session)
        self.channel_profiles = ChannelProfileRepository(session)
        self.audience_profiles = AudienceProfileRepository(session)
        self.dna_versions = ChannelDNAVersionRepository(session)
        self.audit = AuditService(session)

    async def analyze_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> ChannelIntelligenceResult:
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

        existing_channel_profile = self.channel_profiles.get_by_channel(
            channel_id, organization_id=organization_id
        )
        existing_audience_profile = self.audience_profiles.get_current(
            channel_id, organization_id=organization_id
        )

        channel_analysis = await run_channel_analyst(
            self.llm_gateway,
            channel=channel,
            videos=videos,
            playlists=playlists,
            existing_profile=existing_channel_profile,
        )
        audience_analysis = await run_audience_analyst(
            self.llm_gateway,
            channel=channel,
            videos=videos,
            latest_metrics_by_video_id=latest_metrics_by_video_id,
            existing_profile=existing_audience_profile,
        )

        channel_profile = self._persist_channel_profile(
            channel_id=channel_id,
            organization_id=organization_id,
            existing=existing_channel_profile,
            channel_analysis=channel_analysis,
            audience_analysis=audience_analysis,
        )
        audience_profile = self._persist_audience_profile(
            channel_id=channel_id,
            organization_id=organization_id,
            previous_version=existing_audience_profile.version if existing_audience_profile else 0,
            analysis=audience_analysis,
        )

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="channel.analysis.completed",
            resource_type="channel",
            resource_id=channel_id,
            metadata={
                "channel_confidence": channel_analysis.confidence,
                "audience_confidence": audience_analysis.confidence,
                "channel_evidence": channel_analysis.evidence,
                "audience_evidence": audience_analysis.evidence,
            },
        )

        # Documento 04 event chain: channel.connection.created ->
        # channel.sync.completed -> channel.analysis.completed ->
        # channel.dna.activated. Only auto-generate DNA once per channel
        # (first analysis ever) - Documento 04 sec. 20 explicitly warns
        # against recalculating Channel DNA on every small change; later
        # regeneration is a deliberate, manual action instead.
        if (
            self.dna_versions.get_latest_version_number(channel_id, organization_id=organization_id)
            == 0
        ):
            dispatch_channel_dna(
                self.session, channel_id=channel_id, organization_id=organization_id
            )

        return ChannelIntelligenceResult(
            channel_profile=channel_profile,
            audience_profile=audience_profile,
            channel_analysis=channel_analysis,
            audience_analysis=audience_analysis,
        )

    def _persist_channel_profile(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        existing: ChannelProfile | None,
        channel_analysis: ChannelAnalystOutput,
        audience_analysis: AudienceAnalystOutput,
    ) -> ChannelProfile:
        now = datetime.now(UTC)
        profile = existing
        if profile is None:
            profile = ChannelProfile(
                organization_id=organization_id, channel_id=channel_id, confidence=0.0
            )
            self.session.add(profile)

        profile.primary_language = channel_analysis.classification.get("primary_language")
        profile.primary_category = channel_analysis.classification.get("primary_category")
        profile.estimated_audience = ", ".join(audience_analysis.audience_segments[:3]) or None
        profile.content_summary = "; ".join(
            channel_analysis.high_performing_patterns + channel_analysis.content_patterns
        )[:2000]
        profile.confidence = channel_analysis.confidence
        profile.generated_at = now
        self.session.flush()
        return profile

    def _persist_audience_profile(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        previous_version: int,
        analysis: AudienceAnalystOutput,
    ) -> AudienceProfile:
        profile = AudienceProfile(
            organization_id=organization_id,
            channel_id=channel_id,
            version=previous_version + 1,
            profile_json=analysis.model_dump(mode="json", exclude={"confidence"}),
            confidence=analysis.confidence,
            source=AudienceProfileSource.INFERRED,
        )
        self.audience_profiles.add(profile)
        return profile

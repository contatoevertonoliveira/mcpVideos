from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_organization_id, get_current_user, require_permission
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.domain.permissions import Permission
from app.models.channel import Channel
from app.models.content_strategy import ContentStrategy
from app.models.enums import SyncType
from app.models.user import User
from app.repositories.audience_profile import AudienceProfileRepository
from app.repositories.channel import ChannelRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.channel_profile import ChannelProfileRepository
from app.repositories.channel_sync_run import ChannelSyncRunRepository
from app.repositories.content_pillar import ContentPillarRepository
from app.repositories.content_strategy import ContentStrategyRepository
from app.repositories.source_video import SourceVideoRepository
from app.schemas.brand_profile import BrandProfileRead, BrandProfileWrite
from app.schemas.channel import ChannelRead
from app.schemas.channel_connection import ConnectChannelResponse, OAuthCallbackRequest
from app.schemas.channel_dna import ChannelDNAVersionRead, ChannelDNAVersionSummary
from app.schemas.channel_intelligence import (
    AudienceProfileRead,
    ChannelIntelligenceRead,
    ChannelProfileRead,
)
from app.schemas.channel_sync_run import ChannelSyncRunRead, TriggerSyncResponse
from app.schemas.content_strategy import (
    ChannelStrategyStatusRead,
    ContentPillarRead,
    ContentStrategyRead,
    ContentStrategySummary,
    StrategyRuleRead,
    StrategyRuleWrite,
)
from app.schemas.source_video import SourceVideoRead
from app.services.brand_profile import BrandProfileService
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_strategy import ChannelStrategyService
from app.tasks.channel_dna import dispatch_channel_dna
from app.tasks.channel_intelligence import dispatch_channel_intelligence
from app.tasks.channel_strategy import dispatch_channel_strategy
from app.tasks.channel_sync import dispatch_channel_sync

router = APIRouter(prefix="/channels", tags=["channels"])


def _to_read(channel: Channel, db: DbSession, organization_id: uuid.UUID) -> ChannelRead:
    status = ChannelConnectionService(db).get_connection_status(
        channel.id, organization_id=organization_id
    )
    return ChannelRead.model_validate(channel).model_copy(update={"connection_status": status})


@router.get("", response_model=list[ChannelRead])
def list_channels(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[ChannelRead]:
    channels = ChannelRepository(db).list(organization_id=organization_id)
    return [_to_read(channel, db, organization_id) for channel in channels]


@router.post("/connect", response_model=ConnectChannelResponse)
def connect(
    user: User = Depends(get_current_user),
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> ConnectChannelResponse:
    url = ChannelConnectionService(db).start_connection(
        organization_id=organization_id, user_id=user.id
    )
    return ConnectChannelResponse(authorization_url=url)


@router.post("/callback", response_model=ChannelRead)
async def callback(
    payload: OAuthCallbackRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChannelRead:
    channel = await ChannelConnectionService(db).complete_connection(
        code=payload.code, state=payload.state, authenticated_user_id=user.id
    )
    return _to_read(channel, db, channel.organization_id)


@router.post("/{channel_id}/disconnect", response_model=ChannelRead)
async def disconnect(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> ChannelRead:
    channel = await ChannelConnectionService(db).disconnect(
        channel_id=channel_id, organization_id=organization_id
    )
    return _to_read(channel, db, organization_id)


@router.post("/{channel_id}/sync", response_model=TriggerSyncResponse)
def trigger_sync(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> TriggerSyncResponse:
    channel = ChannelRepository(db).get_by_id(channel_id, organization_id=organization_id)
    if channel is None:
        raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

    job = dispatch_channel_sync(
        db, channel_id=channel_id, organization_id=organization_id, sync_type=SyncType.MANUAL
    )
    # dispatch_channel_sync always passes a correlation_id (JobService.create_job
    # defaults to uuid4() when None) - the model column is nullable only because
    # Job is a generic entity shared by other, not-yet-built job types.
    assert job.correlation_id is not None
    return TriggerSyncResponse(job_id=job.id, correlation_id=job.correlation_id)


@router.get("/{channel_id}/videos", response_model=list[SourceVideoRead])
def list_videos(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[SourceVideoRead]:
    videos = SourceVideoRepository(db).list_by_channel(
        channel_id=channel_id, organization_id=organization_id
    )
    return [SourceVideoRead.model_validate(video) for video in videos]


@router.get("/{channel_id}/sync-runs", response_model=list[ChannelSyncRunRead])
def list_sync_runs(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[ChannelSyncRunRead]:
    runs = ChannelSyncRunRepository(db).list_by_channel(
        channel_id=channel_id, organization_id=organization_id
    )
    return [ChannelSyncRunRead.model_validate(run) for run in runs]


@router.post("/{channel_id}/analyze", response_model=TriggerSyncResponse)
def trigger_analysis(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> TriggerSyncResponse:
    channel = ChannelRepository(db).get_by_id(channel_id, organization_id=organization_id)
    if channel is None:
        raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

    job = dispatch_channel_intelligence(db, channel_id=channel_id, organization_id=organization_id)
    assert job.correlation_id is not None
    return TriggerSyncResponse(job_id=job.id, correlation_id=job.correlation_id)


@router.get("/{channel_id}/intelligence", response_model=ChannelIntelligenceRead)
def get_intelligence(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> ChannelIntelligenceRead:
    channel_profile = ChannelProfileRepository(db).get_by_channel(
        channel_id, organization_id=organization_id
    )
    audience_profile = AudienceProfileRepository(db).get_current(
        channel_id, organization_id=organization_id
    )
    return ChannelIntelligenceRead(
        channel_profile=(
            ChannelProfileRead.model_validate(channel_profile) if channel_profile else None
        ),
        audience_profile=(
            AudienceProfileRead.model_validate(audience_profile) if audience_profile else None
        ),
    )


@router.post("/{channel_id}/dna/generate", response_model=TriggerSyncResponse)
def trigger_dna_generation(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> TriggerSyncResponse:
    channel = ChannelRepository(db).get_by_id(channel_id, organization_id=organization_id)
    if channel is None:
        raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

    job = dispatch_channel_dna(db, channel_id=channel_id, organization_id=organization_id)
    assert job.correlation_id is not None
    return TriggerSyncResponse(job_id=job.id, correlation_id=job.correlation_id)


@router.get("/{channel_id}/dna", response_model=ChannelDNAVersionRead | None)
def get_active_dna(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> ChannelDNAVersionRead | None:
    active = ChannelDNAVersionRepository(db).get_active(channel_id, organization_id=organization_id)
    return ChannelDNAVersionRead.model_validate(active) if active else None


@router.get("/{channel_id}/dna/history", response_model=list[ChannelDNAVersionSummary])
def list_dna_history(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[ChannelDNAVersionSummary]:
    versions = ChannelDNAVersionRepository(db).list_by_channel(
        channel_id=channel_id, organization_id=organization_id
    )
    return [ChannelDNAVersionSummary.model_validate(version) for version in versions]


@router.get("/{channel_id}/brand-profile", response_model=BrandProfileRead | None)
def get_brand_profile(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> BrandProfileRead | None:
    profile = BrandProfileService(db).get(channel_id, organization_id=organization_id)
    return BrandProfileRead.model_validate(profile) if profile else None


@router.put("/{channel_id}/brand-profile", response_model=BrandProfileRead)
def upsert_brand_profile(
    channel_id: uuid.UUID,
    payload: BrandProfileWrite,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> BrandProfileRead:
    profile = BrandProfileService(db).upsert(
        channel_id, organization_id=organization_id, payload=payload
    )
    return BrandProfileRead.model_validate(profile)


def _strategy_to_read(
    strategy: ContentStrategy, db: DbSession, organization_id: uuid.UUID
) -> ContentStrategyRead:
    pillars = ContentPillarRepository(db).list_by_strategy(
        strategy.id, organization_id=organization_id
    )
    read = ContentStrategyRead.model_validate(strategy)
    read.pillars = [ContentPillarRead.model_validate(pillar) for pillar in pillars]
    return read


@router.post("/{channel_id}/strategy/generate", response_model=TriggerSyncResponse)
def trigger_strategy_generation(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> TriggerSyncResponse:
    channel = ChannelRepository(db).get_by_id(channel_id, organization_id=organization_id)
    if channel is None:
        raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

    job = dispatch_channel_strategy(db, channel_id=channel_id, organization_id=organization_id)
    assert job.correlation_id is not None
    return TriggerSyncResponse(job_id=job.id, correlation_id=job.correlation_id)


@router.get("/{channel_id}/strategy", response_model=ChannelStrategyStatusRead)
def get_strategy_status(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> ChannelStrategyStatusRead:
    strategies = ContentStrategyRepository(db)
    active = strategies.get_active(channel_id, organization_id=organization_id)
    draft = strategies.get_latest_draft(channel_id, organization_id=organization_id)
    return ChannelStrategyStatusRead(
        active=_strategy_to_read(active, db, organization_id) if active else None,
        pending_draft=_strategy_to_read(draft, db, organization_id) if draft else None,
    )


@router.get("/{channel_id}/strategy/history", response_model=list[ContentStrategySummary])
def list_strategy_history(
    channel_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[ContentStrategySummary]:
    versions = ContentStrategyRepository(db).list_by_channel(
        channel_id=channel_id, organization_id=organization_id
    )
    return [ContentStrategySummary.model_validate(version) for version in versions]


@router.post("/{channel_id}/strategy/{strategy_id}/approve", response_model=ContentStrategyRead)
def approve_strategy(
    channel_id: uuid.UUID,
    strategy_id: uuid.UUID,
    user: User = Depends(get_current_user),
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> ContentStrategyRead:
    strategy = ChannelStrategyService(db).approve(
        channel_id=channel_id,
        strategy_id=strategy_id,
        organization_id=organization_id,
        user_id=user.id,
    )
    return _strategy_to_read(strategy, db, organization_id)


@router.post("/{channel_id}/strategy/{strategy_id}/rules", response_model=StrategyRuleRead)
def add_strategy_rule(
    channel_id: uuid.UUID,
    strategy_id: uuid.UUID,
    payload: StrategyRuleWrite,
    organization_id: uuid.UUID = Depends(require_permission(Permission.CHANNEL_MANAGE)),
    db: DbSession = Depends(get_db),
) -> StrategyRuleRead:
    rule = ChannelStrategyService(db).add_rule(
        channel_id=channel_id,
        strategy_id=strategy_id,
        organization_id=organization_id,
        rule_type=payload.rule_type,
        rule_json=payload.rule_json,
        priority=payload.priority,
    )
    return StrategyRuleRead.model_validate(rule)


@router.get("/{channel_id}/strategy/{strategy_id}/rules", response_model=list[StrategyRuleRead])
def list_strategy_rules(
    channel_id: uuid.UUID,
    strategy_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: DbSession = Depends(get_db),
) -> list[StrategyRuleRead]:
    rules = ChannelStrategyService(db).list_rules(
        strategy_id=strategy_id, organization_id=organization_id
    )
    return [StrategyRuleRead.model_validate(rule) for rule in rules]

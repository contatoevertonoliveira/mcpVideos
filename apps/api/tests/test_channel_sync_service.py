import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.youtube import FakeYouTubeGateway
from app.models.channel import Channel
from app.models.enums import (
    AutomationMode,
    ChannelConnectionStatus,
    SourceVideoType,
    SyncRunStatus,
    SyncType,
)
from app.repositories.channel import ChannelRepository
from app.repositories.source_playlist import SourcePlaylistRepository
from app.repositories.source_video import SourceVideoRepository
from app.repositories.source_video_metric import SourceVideoMetricRepository
from app.security.encryption import decrypt_token
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_sync import ChannelSyncService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


async def _connect_channel(db_session, org, user):
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )
    return channel


def _sync_service(db_session) -> ChannelSyncService:
    return ChannelSyncService(db_session, gateway=FakeYouTubeGateway())


@pytest.mark.anyio
async def test_run_sync_imports_playlists_videos_metrics(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_channel(db_session, org, user)

    run = await _sync_service(db_session).run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )

    assert run.status == SyncRunStatus.COMPLETED
    assert run.items_created == 1 + 5  # 1 playlist + 5 fake videos
    assert run.items_updated == 0

    playlists = SourcePlaylistRepository(db_session).list(organization_id=org.id)
    videos = SourceVideoRepository(db_session).list(organization_id=org.id)
    metrics = SourceVideoMetricRepository(db_session).list(organization_id=org.id)
    assert len(playlists) == 1
    assert len(videos) == 5
    assert len(metrics) == 5

    db_session.refresh(channel)
    assert channel.last_synced_at is not None


@pytest.mark.anyio
async def test_run_sync_classifies_short_and_long_form(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_channel(db_session, org, user)

    await _sync_service(db_session).run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )

    videos = SourceVideoRepository(db_session).list(organization_id=org.id)
    types = {v.video_type for v in videos}
    assert SourceVideoType.SHORT in types
    assert SourceVideoType.LONG_FORM in types


@pytest.mark.anyio
async def test_run_sync_twice_does_not_duplicate_videos_or_playlists(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_channel(db_session, org, user)
    service = _sync_service(db_session)

    await service.run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )
    second_run = await service.run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INCREMENTAL
    )

    assert second_run.items_created == 0
    assert second_run.items_updated == 1 + 5

    playlists = SourcePlaylistRepository(db_session).list(organization_id=org.id)
    videos = SourceVideoRepository(db_session).list(organization_id=org.id)
    assert len(playlists) == 1
    assert len(videos) == 5

    # Metrics are historical - a new snapshot per sync is expected, not a duplicate.
    metrics = SourceVideoMetricRepository(db_session).list(organization_id=org.id, limit=100)
    assert len(metrics) == 10


@pytest.mark.anyio
async def test_run_sync_without_connection_raises(db_session):
    org, user = _org_and_user(db_session)
    channel = ChannelRepository(db_session).add(
        Channel(organization_id=org.id, name="Placeholder", automation_mode=AutomationMode.ASSISTED)
    )

    with pytest.raises(DomainError):
        await _sync_service(db_session).run_sync(
            channel_id=channel.id, organization_id=org.id, sync_type=SyncType.MANUAL
        )


@pytest.mark.anyio
async def test_run_sync_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _sync_service(db_session).run_sync(
            channel_id=uuid.uuid4(), organization_id=org.id, sync_type=SyncType.MANUAL
        )


@pytest.mark.anyio
async def test_run_sync_refreshes_expired_token(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_channel(db_session, org, user)

    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    connection = connection_service.connections.get_by_channel(channel.id, organization_id=org.id)
    connection.token_expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db_session.flush()

    await _sync_service(db_session).run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.MANUAL
    )

    db_session.refresh(connection)
    assert decrypt_token(connection.access_token_encrypted).startswith("fake-access-refreshed-")
    assert connection.token_expires_at > datetime.now(UTC)


@pytest.mark.anyio
async def test_run_sync_marks_run_failed_on_gateway_error(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_channel(db_session, org, user)

    class BrokenGateway(FakeYouTubeGateway):
        async def list_playlists(self, access_token, channel_external_id):
            raise RuntimeError("YouTube is down")

    service = ChannelSyncService(db_session, gateway=BrokenGateway())

    with pytest.raises(RuntimeError):
        await service.run_sync(
            channel_id=channel.id, organization_id=org.id, sync_type=SyncType.MANUAL
        )

    runs = service.sync_runs.list_by_channel(channel_id=channel.id, organization_id=org.id)
    failed_run = next(r for r in runs if r.status == SyncRunStatus.FAILED)
    assert failed_run.error_message == "YouTube is down"

    connection = service.connections.get_by_channel(channel.id, organization_id=org.id)
    assert connection.status == ChannelConnectionStatus.CONNECTED  # reverted, not stuck SYNCING

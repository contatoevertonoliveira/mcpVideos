from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ApplicationError, DomainError, NotFoundError
from app.gateways.youtube import YouTubeGateway, YouTubeVideoInfo, get_youtube_gateway
from app.models.channel_connection import ChannelConnection
from app.models.channel_sync_run import ChannelSyncRun
from app.models.enums import (
    AuditActorType,
    ChannelConnectionStatus,
    SourceVideoType,
    SyncRunStatus,
    SyncType,
)
from app.models.source_playlist import SourcePlaylist
from app.models.source_video import SourceVideo
from app.models.source_video_metric import SourceVideoMetric
from app.observability.logging import get_logger
from app.repositories.channel import ChannelRepository
from app.repositories.channel_connection import ChannelConnectionRepository
from app.repositories.channel_sync_run import ChannelSyncRunRepository
from app.repositories.source_playlist import SourcePlaylistRepository
from app.repositories.source_video import SourceVideoRepository
from app.repositories.source_video_metric import SourceVideoMetricRepository
from app.security.encryption import decrypt_token, encrypt_token
from app.services.audit import AuditService

# A short-form video on YouTube has no dedicated Data API flag - duration is
# the standard heuristic used by the ecosystem (Documento 03 sec. 12 lists
# "short" as a type but does not define the cutoff).
SHORT_VIDEO_MAX_SECONDS = 60

# Refresh proactively rather than waiting for an outright 401, so a sync
# never fails on a token that expires mid-run.
TOKEN_REFRESH_SKEW = timedelta(minutes=5)

logger = get_logger(__name__)


class ChannelSyncService:
    """Documento 04, secao 16-19 (Workflow 02 - channel.sync.v1) and
    Documento 10 Fase 05. Imports a channel's playlists/videos/metrics via
    YouTubeGateway, idempotently (upsert by external id - re-running a sync
    never duplicates videos or playlists)."""

    def __init__(self, session: Session, gateway: YouTubeGateway | None = None) -> None:
        self.session = session
        self.gateway = gateway or get_youtube_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.connections = ChannelConnectionRepository(session)
        self.sync_runs = ChannelSyncRunRepository(session)
        self.videos = SourceVideoRepository(session)
        self.playlists = SourcePlaylistRepository(session)
        self.metrics = SourceVideoMetricRepository(session)
        self.audit = AuditService(session)

    async def run_sync(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        sync_type: SyncType,
        correlation_id: uuid.UUID | None = None,
    ) -> ChannelSyncRun:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        connection = self.connections.get_by_channel(channel_id, organization_id=organization_id)
        if (
            connection is None
            or connection.status == ChannelConnectionStatus.DISCONNECTED
            or connection.external_account_id is None
        ):
            raise DomainError(
                "Channel has no active YouTube connection to sync from",
                code="CHANNEL_NOT_CONNECTED",
            )

        run = self.sync_runs.add(
            ChannelSyncRun(
                organization_id=organization_id,
                channel_id=channel_id,
                sync_type=sync_type,
                status=SyncRunStatus.RUNNING,
                correlation_id=correlation_id or uuid.uuid4(),
            )
        )
        channel_external_id: str = connection.external_account_id
        previous_status = connection.status
        connection.status = ChannelConnectionStatus.SYNCING
        self.session.flush()

        try:
            access_token = await self._ensure_valid_access_token(connection)
            playlist_stats = await self._sync_playlists(
                connection, channel_external_id, access_token
            )
            video_rows, video_stats = await self._sync_videos(
                connection, channel_external_id, access_token
            )
            metrics_created = await self._sync_metrics(connection, access_token, video_rows)

            now = datetime.now(UTC)
            channel.last_synced_at = now
            connection.status = ChannelConnectionStatus.CONNECTED

            run.status = SyncRunStatus.COMPLETED
            run.completed_at = now
            run.items_discovered = (
                playlist_stats[0] + playlist_stats[1] + video_stats[0] + video_stats[1]
            )
            run.items_created = playlist_stats[0] + video_stats[0]
            run.items_updated = playlist_stats[1] + video_stats[1]
            self.session.flush()

            self.audit.record(
                organization_id=organization_id,
                actor_type=AuditActorType.SYSTEM,
                action="channel.sync.completed",
                resource_type="channel",
                resource_id=channel_id,
                metadata={
                    "sync_type": sync_type.value,
                    "videos": len(video_rows),
                    "playlists": playlist_stats[0] + playlist_stats[1],
                    "metrics_captured": metrics_created,
                },
            )
            return run
        except Exception as exc:
            now = datetime.now(UTC)
            run.status = SyncRunStatus.FAILED
            run.completed_at = now
            run.error_code = self._error_code(exc)
            run.error_message = str(exc)[:2000]
            connection.status = (
                ChannelConnectionStatus.NEEDS_REAUTHORIZATION
                if self._is_auth_error(exc)
                else previous_status
            )
            self.session.flush()
            logger.warning(
                "channel_sync_failed",
                channel_id=str(channel_id),
                sync_type=sync_type.value,
                error=str(exc),
            )
            raise

    async def _ensure_valid_access_token(self, connection: ChannelConnection) -> str:
        now = datetime.now(UTC)
        if connection.token_expires_at <= now + TOKEN_REFRESH_SKEW:
            refresh_token = decrypt_token(connection.refresh_token_encrypted)
            token_set = await self.gateway.refresh_access_token(refresh_token)
            connection.access_token_encrypted = encrypt_token(token_set.access_token)
            if token_set.refresh_token:
                connection.refresh_token_encrypted = encrypt_token(token_set.refresh_token)
            connection.token_expires_at = token_set.expires_at
            self.session.flush()
            return token_set.access_token
        return decrypt_token(connection.access_token_encrypted)

    async def _sync_playlists(
        self, connection: ChannelConnection, channel_external_id: str, access_token: str
    ) -> tuple[int, int]:
        playlists = await self.gateway.list_playlists(access_token, channel_external_id)
        created = updated = 0
        for item in playlists:
            existing = self.playlists.get_by_external_id(
                channel_id=connection.channel_id,
                organization_id=connection.organization_id,
                external_playlist_id=item.external_playlist_id,
            )
            if existing is None:
                self.session.add(
                    SourcePlaylist(
                        organization_id=connection.organization_id,
                        channel_id=connection.channel_id,
                        external_playlist_id=item.external_playlist_id,
                        title=item.title,
                        description=item.description,
                        item_count=item.item_count,
                        raw_metadata_json=item.raw,
                    )
                )
                created += 1
            else:
                existing.title = item.title
                existing.description = item.description
                existing.item_count = item.item_count
                existing.raw_metadata_json = item.raw
                updated += 1
        self.session.flush()
        return created, updated

    async def _sync_videos(
        self, connection: ChannelConnection, channel_external_id: str, access_token: str
    ) -> tuple[list[SourceVideo], tuple[int, int]]:
        videos = await self.gateway.list_videos(access_token, channel_external_id)
        rows: list[SourceVideo] = []
        created = updated = 0
        for item in videos:
            existing = self.videos.get_by_external_id(
                channel_id=connection.channel_id,
                organization_id=connection.organization_id,
                external_video_id=item.external_video_id,
            )
            video_type = self._classify(item)
            if existing is None:
                row = SourceVideo(
                    organization_id=connection.organization_id,
                    channel_id=connection.channel_id,
                    external_video_id=item.external_video_id,
                )
                self.session.add(row)
                created += 1
            else:
                row = existing
                updated += 1
            row.title = item.title
            row.description = item.description
            row.video_type = video_type
            row.duration_seconds = item.duration_seconds
            row.published_at = item.published_at
            row.privacy_status = item.privacy_status
            row.thumbnail_url = item.thumbnail_url
            row.raw_metadata_json = item.raw
            rows.append(row)
        self.session.flush()
        return rows, (created, updated)

    async def _sync_metrics(
        self, connection: ChannelConnection, access_token: str, video_rows: list[SourceVideo]
    ) -> int:
        if not video_rows:
            return 0
        metrics = await self.gateway.get_video_metrics(
            access_token, [row.external_video_id for row in video_rows]
        )
        metrics_by_external_id = {item.external_video_id: item for item in metrics}
        captured_at = datetime.now(UTC)
        created = 0
        for row in video_rows:
            item = metrics_by_external_id.get(row.external_video_id)
            if item is None:
                continue
            if self.metrics.exists_for_capture(
                source_video_id=row.id,
                organization_id=connection.organization_id,
                captured_at=captured_at,
            ):
                continue
            self.session.add(
                SourceVideoMetric(
                    organization_id=connection.organization_id,
                    channel_id=connection.channel_id,
                    source_video_id=row.id,
                    captured_at=captured_at,
                    views=item.views,
                    likes=item.likes,
                    comments=item.comments,
                    raw_metrics_json=item.raw,
                )
            )
            created += 1
        self.session.flush()
        return created

    @staticmethod
    def _classify(item: YouTubeVideoInfo) -> SourceVideoType:
        if item.is_live:
            return SourceVideoType.LIVE
        if item.duration_seconds is None:
            return SourceVideoType.UNKNOWN
        if item.duration_seconds <= SHORT_VIDEO_MAX_SECONDS:
            return SourceVideoType.SHORT
        return SourceVideoType.LONG_FORM

    @staticmethod
    def _is_auth_error(exc: Exception) -> bool:
        return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in (401, 403)

    @staticmethod
    def _error_code(exc: Exception) -> str:
        if isinstance(exc, ApplicationError):
            return exc.code
        if isinstance(exc, httpx.HTTPStatusError):
            return f"YOUTUBE_API_ERROR_{exc.response.status_code}"
        return "SYNC_FAILED"

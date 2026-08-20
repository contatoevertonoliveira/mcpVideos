from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AuthorizationError, DomainError, NotFoundError
from app.gateways.youtube import YouTubeGateway, get_youtube_gateway
from app.models.channel import Channel
from app.models.channel_connection import ChannelConnection
from app.models.channel_sync_run import ChannelSyncRun
from app.models.enums import (
    AuditActorType,
    AutomationMode,
    ChannelConnectionProvider,
    ChannelConnectionStatus,
    ChannelPlatform,
    ChannelStatus,
    SyncRunStatus,
    SyncType,
)
from app.observability.logging import get_logger
from app.repositories.channel import ChannelRepository
from app.repositories.channel_connection import ChannelConnectionRepository
from app.repositories.channel_sync_run import ChannelSyncRunRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.security.encryption import decrypt_token, encrypt_token
from app.security.signed_state import InvalidStateError, create_state, verify_state
from app.services.audit import AuditService
from app.tasks.channel_sync import dispatch_channel_sync

STATE_MAX_AGE_SECONDS = 600
logger = get_logger(__name__)


class ChannelConnectionService:
    """Documento 02, secao 47-48; Documento 03, secao 10-11; Documento 09,
    secao 20-27. Orquestra o ciclo de vida da conexao OAuth de um canal
    YouTube - nunca expoe tokens, sempre passa pelo YouTubeGateway."""

    def __init__(self, session: Session, gateway: YouTubeGateway | None = None) -> None:
        self.session = session
        self.gateway = gateway or get_youtube_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.connections = ChannelConnectionRepository(session)
        self.sync_runs = ChannelSyncRunRepository(session)
        self.members = OrganizationMemberRepository(session)
        self.audit = AuditService(session)

    def start_connection(self, *, organization_id: uuid.UUID, user_id: uuid.UUID) -> str:
        member = self.members.get_by_user(organization_id=organization_id, user_id=user_id)
        if member is None:
            raise AuthorizationError(
                "You are not a member of this organization", code="NOT_A_MEMBER"
            )

        state = create_state(
            {"organization_id": str(organization_id), "user_id": str(user_id)},
            max_age_seconds=STATE_MAX_AGE_SECONDS,
        )
        return self.gateway.get_authorization_url(state)

    async def complete_connection(
        self, *, code: str, state: str, authenticated_user_id: uuid.UUID
    ) -> Channel:
        try:
            state_payload = verify_state(state)
        except InvalidStateError as exc:
            raise DomainError(
                "This connection link is invalid or has expired. Please try again.",
                code="INVALID_OAUTH_STATE",
            ) from exc

        organization_id = uuid.UUID(state_payload["organization_id"])
        user_id = uuid.UUID(state_payload["user_id"])
        if user_id != authenticated_user_id:
            raise AuthorizationError(
                "This connection link was not issued for the current user",
                code="STATE_USER_MISMATCH",
            )

        token_set = await self.gateway.exchange_code(code)
        channel_info = await self.gateway.get_channel_info(token_set.access_token)

        channel = self.channels.get_by_external_id(
            organization_id=organization_id,
            platform=ChannelPlatform.YOUTUBE,
            external_channel_id=channel_info.external_channel_id,
        )
        is_new_channel = channel is None
        now = datetime.now(UTC)

        if channel is None:
            # Not using self.channels.add() here on purpose: it flushes
            # immediately, and NOT NULL fields like name/external_channel_id
            # are only set below - flushing now would violate them.
            channel = Channel(
                organization_id=organization_id, automation_mode=AutomationMode.ASSISTED
            )
            self.session.add(channel)

        channel.platform = ChannelPlatform.YOUTUBE
        channel.external_channel_id = channel_info.external_channel_id
        channel.name = channel_info.title
        channel.handle = channel_info.custom_url
        channel.description = channel_info.description
        channel.thumbnail_url = channel_info.thumbnail_url
        channel.status = ChannelStatus.ACTIVE
        channel.connected_at = now
        channel.last_synced_at = now
        self.session.flush()

        connection = self.connections.get_by_channel(channel.id, organization_id=organization_id)
        if connection is None:
            # Same reasoning as above: token_*_encrypted/token_expires_at
            # are NOT NULL and only set below.
            connection = ChannelConnection(
                organization_id=organization_id,
                channel_id=channel.id,
                provider=ChannelConnectionProvider.GOOGLE_YOUTUBE,
            )
            self.session.add(connection)

        connection.external_account_id = channel_info.external_channel_id
        connection.access_token_encrypted = encrypt_token(token_set.access_token)
        connection.refresh_token_encrypted = encrypt_token(token_set.refresh_token)
        connection.token_expires_at = token_set.expires_at
        connection.scopes = token_set.scopes
        connection.status = ChannelConnectionStatus.CONNECTED
        self.session.flush()

        self.sync_runs.add(
            ChannelSyncRun(
                organization_id=organization_id,
                channel_id=channel.id,
                sync_type=SyncType.INITIAL,
                status=SyncRunStatus.COMPLETED,
                completed_at=now,
                items_discovered=1,
                items_created=1 if is_new_channel else 0,
                items_updated=0 if is_new_channel else 1,
            )
        )

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="channel.connected",
            resource_type="channel",
            resource_id=channel.id,
            metadata={
                "platform": "youtube",
                "external_channel_id": channel_info.external_channel_id,
            },
        )

        # Documento 10, Fase 05: "Conectar canal dispara import." First
        # connection imports everything (INITIAL); reconnecting an already
        # imported channel only needs to catch up (INCREMENTAL).
        dispatch_channel_sync(
            self.session,
            channel_id=channel.id,
            organization_id=organization_id,
            sync_type=SyncType.INITIAL if is_new_channel else SyncType.INCREMENTAL,
        )
        return channel

    async def disconnect(self, *, channel_id: uuid.UUID, organization_id: uuid.UUID) -> Channel:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        connection = self.connections.get_by_channel(channel.id, organization_id=organization_id)
        if connection is not None and connection.status != ChannelConnectionStatus.DISCONNECTED:
            try:
                await self.gateway.revoke_token(decrypt_token(connection.access_token_encrypted))
            except Exception as exc:
                # Best-effort: token revocation failing must never block disconnecting
                # the channel on our side (Documento 04 sec. 104 - graceful degradation).
                logger.warning(
                    "youtube_token_revoke_failed", channel_id=str(channel_id), error=str(exc)
                )
            connection.status = ChannelConnectionStatus.DISCONNECTED
            self.session.flush()

        channel.status = ChannelStatus.DISABLED
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            action="channel.disconnected",
            resource_type="channel",
            resource_id=channel.id,
        )
        return channel

    def get_connection_status(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ChannelConnectionStatus | None:
        connection = self.connections.get_by_channel(channel_id, organization_id=organization_id)
        return connection.status if connection else None

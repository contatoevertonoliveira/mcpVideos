from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_organization_id, get_current_user, require_permission
from app.db.session import get_db
from app.domain.permissions import Permission
from app.models.channel import Channel
from app.models.user import User
from app.repositories.channel import ChannelRepository
from app.schemas.channel import ChannelRead
from app.schemas.channel_connection import ConnectChannelResponse, OAuthCallbackRequest
from app.services.channel_connection import ChannelConnectionService

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

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.channel import Channel
from app.models.enums import AutomationMode, ChannelPlatform, ChannelStatus
from app.repositories.channel import ChannelRepository


class ChannelService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.channels = ChannelRepository(session)

    def create_placeholder_channel(
        self,
        *,
        organization_id: uuid.UUID,
        name: str,
        platform: ChannelPlatform = ChannelPlatform.YOUTUBE,
    ) -> Channel:
        """Cria o registro do canal sem conexao OAuth (Fase 04 cuida disso).

        Documento 03, secao 9: todo canal novo comeca em ASSISTED - nunca
        com automacao/auto-publicacao irrestrita.
        """
        channel = Channel(
            organization_id=organization_id,
            name=name,
            platform=platform,
            status=ChannelStatus.PENDING,
            automation_mode=AutomationMode.ASSISTED,
        )
        return self.channels.add(channel)

    def get_channel(self, channel_id: uuid.UUID, *, organization_id: uuid.UUID) -> Channel:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")
        return channel

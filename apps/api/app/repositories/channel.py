from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.channel import Channel
from app.models.enums import ChannelPlatform
from app.repositories.base import TenantScopedRepository


class ChannelRepository(TenantScopedRepository[Channel]):
    model = Channel

    def get_by_external_id(
        self,
        *,
        organization_id: uuid.UUID,
        platform: ChannelPlatform,
        external_channel_id: str,
    ) -> Channel | None:
        stmt = select(Channel).where(
            Channel.organization_id == organization_id,
            Channel.platform == platform,
            Channel.external_channel_id == external_channel_id,
        )
        return self.session.scalars(stmt).first()

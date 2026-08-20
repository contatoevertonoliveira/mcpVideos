from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.channel_connection import ChannelConnection
from app.repositories.base import TenantScopedRepository


class ChannelConnectionRepository(TenantScopedRepository[ChannelConnection]):
    model = ChannelConnection

    def get_by_channel(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ChannelConnection | None:
        stmt = select(ChannelConnection).where(
            ChannelConnection.channel_id == channel_id,
            ChannelConnection.organization_id == organization_id,
        )
        return self.session.scalars(stmt).first()

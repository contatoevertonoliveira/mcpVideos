from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.channel_profile import ChannelProfile
from app.repositories.base import TenantScopedRepository


class ChannelProfileRepository(TenantScopedRepository[ChannelProfile]):
    model = ChannelProfile

    def get_by_channel(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ChannelProfile | None:
        stmt = select(ChannelProfile).where(
            ChannelProfile.organization_id == organization_id,
            ChannelProfile.channel_id == channel_id,
        )
        return self.session.scalars(stmt).first()

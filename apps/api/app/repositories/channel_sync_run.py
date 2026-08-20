from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.channel_sync_run import ChannelSyncRun
from app.repositories.base import TenantScopedRepository


class ChannelSyncRunRepository(TenantScopedRepository[ChannelSyncRun]):
    model = ChannelSyncRun

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 20
    ) -> list[ChannelSyncRun]:
        stmt = (
            select(ChannelSyncRun)
            .where(
                ChannelSyncRun.organization_id == organization_id,
                ChannelSyncRun.channel_id == channel_id,
            )
            .order_by(ChannelSyncRun.started_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

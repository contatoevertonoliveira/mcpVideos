from __future__ import annotations

from app.models.channel_sync_run import ChannelSyncRun
from app.repositories.base import TenantScopedRepository


class ChannelSyncRunRepository(TenantScopedRepository[ChannelSyncRun]):
    model = ChannelSyncRun

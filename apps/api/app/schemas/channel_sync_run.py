from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SyncRunStatus, SyncType


class ChannelSyncRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    sync_type: SyncType
    status: SyncRunStatus
    started_at: datetime
    completed_at: datetime | None
    items_discovered: int
    items_created: int
    items_updated: int
    error_code: str | None
    error_message: str | None
    correlation_id: uuid.UUID


class TriggerSyncResponse(BaseModel):
    job_id: uuid.UUID
    correlation_id: uuid.UUID

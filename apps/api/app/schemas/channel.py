from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AutomationMode, ChannelPlatform, ChannelStatus


class ChannelCreate(BaseModel):
    """Cria um canal "placeholder" - sem conexao OAuth ainda (Fase 04)."""

    name: str = Field(min_length=1, max_length=200)
    platform: ChannelPlatform = ChannelPlatform.YOUTUBE


class ChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    platform: ChannelPlatform
    external_channel_id: str | None
    name: str
    handle: str | None
    status: ChannelStatus
    automation_mode: AutomationMode
    connected_at: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime

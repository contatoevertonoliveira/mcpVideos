from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import AudienceProfileSource


class ChannelProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    primary_language: str | None
    primary_category: str | None
    estimated_audience: str | None
    content_summary: str | None
    confidence: float
    generated_at: datetime
    updated_at: datetime


class AudienceProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    version: int
    profile_json: dict[str, Any]
    confidence: float
    source: AudienceProfileSource
    created_at: datetime


class ChannelIntelligenceRead(BaseModel):
    channel_profile: ChannelProfileRead | None
    audience_profile: AudienceProfileRead | None

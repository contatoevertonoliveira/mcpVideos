from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import ChannelDNAStatus


class ChannelDNAVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    version: int
    status: ChannelDNAStatus
    classification_json: dict[str, Any]
    audience_json: dict[str, Any]
    formats_json: dict[str, Any]
    content_patterns_json: dict[str, Any]
    performance_patterns_json: dict[str, Any]
    brand_rules_json: dict[str, Any]
    publishing_patterns_json: dict[str, Any]
    restrictions_json: dict[str, Any]
    recommendations_json: dict[str, Any]
    confidence: float
    created_at: datetime
    activated_at: datetime | None


class ChannelDNAVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    status: ChannelDNAStatus
    confidence: float
    created_at: datetime
    activated_at: datetime | None

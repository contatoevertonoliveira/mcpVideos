from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContentStrategyStatus


class ContentPillarRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    target_ratio: float
    priority: int
    active: bool


class ContentStrategyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    name: str
    version: int
    status: ContentStrategyStatus
    objective: str
    shorts_ratio: float
    long_form_ratio: float
    experimental_ratio: float
    recommended_frequency_json: dict[str, Any]
    strategy_json: dict[str, Any]
    created_at: datetime
    activated_at: datetime | None
    pillars: list[ContentPillarRead] = Field(default_factory=list)


class ContentStrategySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    status: ContentStrategyStatus
    created_at: datetime
    activated_at: datetime | None


class ChannelStrategyStatusRead(BaseModel):
    active: ContentStrategyRead | None
    pending_draft: ContentStrategyRead | None


class StrategyRuleWrite(BaseModel):
    rule_type: str = Field(min_length=1, max_length=100)
    rule_json: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0


class StrategyRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy_id: uuid.UUID
    rule_type: str
    rule_json: dict[str, Any]
    priority: int
    active: bool

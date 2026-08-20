from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrandProfileWrite(BaseModel):
    name: str | None = None
    colors_json: dict[str, Any] = Field(default_factory=dict)
    typography_json: dict[str, Any] = Field(default_factory=dict)
    visual_style_json: dict[str, Any] = Field(default_factory=dict)
    tone_of_voice_json: dict[str, Any] = Field(default_factory=dict)
    rules_json: dict[str, Any] = Field(default_factory=dict)
    prohibited_elements_json: dict[str, Any] = Field(default_factory=dict)


class BrandProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    name: str | None
    colors_json: dict[str, Any]
    typography_json: dict[str, Any]
    visual_style_json: dict[str, Any]
    tone_of_voice_json: dict[str, Any]
    rules_json: dict[str, Any]
    prohibited_elements_json: dict[str, Any]

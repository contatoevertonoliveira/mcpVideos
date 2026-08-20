from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SourceVideoType


class SourceVideoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    external_video_id: str
    title: str
    description: str | None
    video_type: SourceVideoType
    duration_seconds: int | None
    published_at: datetime | None
    privacy_status: str | None
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime

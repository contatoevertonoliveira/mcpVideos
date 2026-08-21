from __future__ import annotations

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict

from app.models.enums import CalendarItemSource, CalendarItemStatus, DayOfWeek, SourceVideoType


class CalendarItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    idea_id: uuid.UUID | None
    content_type: SourceVideoType
    planned_at: datetime
    status: CalendarItemStatus
    source: CalendarItemSource
    created_at: datetime
    # From the linked ContentIdea, if any (Documento 08 sec. 31: mostrar
    # "horario, formato, titulo, status").
    idea_title: str | None = None


class RescheduleCalendarItemRequest(BaseModel):
    planned_at: datetime


class PublishingSlotWrite(BaseModel):
    day_of_week: DayOfWeek
    local_time: time
    content_type: SourceVideoType
    timezone: str = "UTC"
    priority: int = 0


class PublishingSlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    day_of_week: DayOfWeek
    local_time: time
    timezone: str
    content_type: SourceVideoType
    priority: int
    active: bool

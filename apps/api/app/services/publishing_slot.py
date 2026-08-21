from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.enums import DayOfWeek, SourceVideoType
from app.models.publishing_slot import PublishingSlot
from app.repositories.channel import ChannelRepository
from app.repositories.publishing_slot import PublishingSlotRepository


class PublishingSlotService:
    """Documento 03, secao 28. CRUD simples do usuario - nao gerado por
    agente, mesmo espirito de ``brand_profiles``/``strategy_rules``."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.channels = ChannelRepository(session)
        self.slots = PublishingSlotRepository(session)

    def add(
        self,
        *,
        channel_id: uuid.UUID,
        organization_id: uuid.UUID,
        day_of_week: DayOfWeek,
        local_time: time,
        content_type: SourceVideoType,
        timezone: str = "UTC",
        priority: int = 0,
    ) -> PublishingSlot:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        slot = PublishingSlot(
            organization_id=organization_id,
            channel_id=channel_id,
            day_of_week=day_of_week,
            local_time=local_time,
            timezone=timezone,
            content_type=content_type,
            priority=priority,
        )
        return self.slots.add(slot)

    def list(self, *, channel_id: uuid.UUID, organization_id: uuid.UUID) -> list[PublishingSlot]:
        return self.slots.list_by_channel(channel_id=channel_id, organization_id=organization_id)

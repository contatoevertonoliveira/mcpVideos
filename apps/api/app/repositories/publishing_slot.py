from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.publishing_slot import PublishingSlot
from app.repositories.base import TenantScopedRepository


class PublishingSlotRepository(TenantScopedRepository[PublishingSlot]):
    model = PublishingSlot

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, active_only: bool = False
    ) -> list[PublishingSlot]:
        conditions = [
            PublishingSlot.organization_id == organization_id,
            PublishingSlot.channel_id == channel_id,
        ]
        if active_only:
            conditions.append(PublishingSlot.active.is_(True))
        stmt = select(PublishingSlot).where(*conditions).order_by(PublishingSlot.priority.desc())
        return list(self.session.scalars(stmt).all())

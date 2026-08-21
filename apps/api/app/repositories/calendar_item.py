from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.calendar_item import CalendarItem
from app.models.enums import CalendarItemStatus
from app.repositories.base import TenantScopedRepository


class CalendarItemRepository(TenantScopedRepository[CalendarItem]):
    model = CalendarItem

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[CalendarItem]:
        stmt = (
            select(CalendarItem)
            .where(
                CalendarItem.organization_id == organization_id,
                CalendarItem.channel_id == channel_id,
            )
            .order_by(CalendarItem.planned_at.asc())
        )
        return list(self.session.scalars(stmt).all())

    def list_active_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[CalendarItem]:
        """Everything not cancelled - the pool considered for conflict
        detection when planning a new batch."""
        stmt = (
            select(CalendarItem)
            .where(
                CalendarItem.organization_id == organization_id,
                CalendarItem.channel_id == channel_id,
                CalendarItem.status != CalendarItemStatus.CANCELLED,
            )
            .order_by(CalendarItem.planned_at.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get_active_by_idea(
        self, idea_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> CalendarItem | None:
        """Whether an approved idea already has a (non-cancelled) calendar
        item - used to avoid recommending the same idea twice."""
        stmt = select(CalendarItem).where(
            CalendarItem.organization_id == organization_id,
            CalendarItem.idea_id == idea_id,
            CalendarItem.status != CalendarItemStatus.CANCELLED,
        )
        return self.session.scalars(stmt).first()

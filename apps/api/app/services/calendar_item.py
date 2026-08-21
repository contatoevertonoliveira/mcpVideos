from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, NotFoundError
from app.models.calendar_item import CalendarItem
from app.models.enums import AuditActorType, CalendarItemStatus
from app.repositories.calendar_item import CalendarItemRepository
from app.services.audit import AuditService

_NOT_MOVABLE_STATUSES = (
    CalendarItemStatus.PRODUCING,
    CalendarItemStatus.PUBLISHED,
    CalendarItemStatus.CANCELLED,
)
_NOT_REJECTABLE_STATUSES = (CalendarItemStatus.PUBLISHED, CalendarItemStatus.CANCELLED)
_APPROVABLE_STATUSES = (CalendarItemStatus.SUGGESTED, CalendarItemStatus.PLANNED)


class CalendarItemService:
    """Documento 10 Fase 10 acceptance criteria: "ver calendario sugerido,
    aprovar item, rejeitar, mover". The Calendar Planner only ever creates
    SUGGESTED items (app/services/calendar_planning.py) - every state
    transition here is a human action, same "agents propose, services
    validate" split used throughout the project."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.items = CalendarItemRepository(session)
        self.audit = AuditService(session)

    def list_calendar(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[CalendarItem]:
        return self.items.list_by_channel(channel_id=channel_id, organization_id=organization_id)

    def approve(
        self,
        *,
        channel_id: uuid.UUID,
        item_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CalendarItem:
        item = self._get_owned(item_id, channel_id=channel_id, organization_id=organization_id)
        if item.status not in _APPROVABLE_STATUSES:
            raise DomainError(
                f"Calendar item is {item.status.value}, not suggested or planned",
                code="CALENDAR_ITEM_NOT_APPROVABLE",
            )

        item.status = CalendarItemStatus.APPROVED
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="calendar.item.approved",
            resource_type="calendar_item",
            resource_id=item.id,
        )
        return item

    def reject(
        self,
        *,
        channel_id: uuid.UUID,
        item_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CalendarItem:
        item = self._get_owned(item_id, channel_id=channel_id, organization_id=organization_id)
        if item.status in _NOT_REJECTABLE_STATUSES:
            raise DomainError(
                f"Calendar item is already {item.status.value}, cannot be rejected",
                code="CALENDAR_ITEM_NOT_REJECTABLE",
            )

        item.status = CalendarItemStatus.CANCELLED
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="calendar.item.rejected",
            resource_type="calendar_item",
            resource_id=item.id,
        )
        return item

    def reschedule(
        self,
        *,
        channel_id: uuid.UUID,
        item_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        planned_at: datetime,
    ) -> CalendarItem:
        item = self._get_owned(item_id, channel_id=channel_id, organization_id=organization_id)
        if item.status in _NOT_MOVABLE_STATUSES:
            raise DomainError(
                f"Calendar item is {item.status.value}, cannot be moved",
                code="CALENDAR_ITEM_NOT_MOVABLE",
            )

        previous_planned_at = item.planned_at
        item.planned_at = planned_at
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="calendar.item.moved",
            resource_type="calendar_item",
            resource_id=item.id,
            metadata={
                "from": previous_planned_at.isoformat(),
                "to": planned_at.isoformat(),
            },
        )
        return item

    def _get_owned(
        self, item_id: uuid.UUID, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> CalendarItem:
        item = self.items.get_by_id(item_id, organization_id=organization_id)
        if item is None or item.channel_id != channel_id:
            raise NotFoundError("Calendar item not found", code="CALENDAR_ITEM_NOT_FOUND")
        return item

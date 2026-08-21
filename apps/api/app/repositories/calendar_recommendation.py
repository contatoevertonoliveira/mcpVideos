from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.calendar_recommendation import CalendarRecommendation
from app.repositories.base import TenantScopedRepository


class CalendarRecommendationRepository(TenantScopedRepository[CalendarRecommendation]):
    model = CalendarRecommendation

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[CalendarRecommendation]:
        stmt = (
            select(CalendarRecommendation)
            .where(
                CalendarRecommendation.organization_id == organization_id,
                CalendarRecommendation.channel_id == channel_id,
            )
            .order_by(CalendarRecommendation.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

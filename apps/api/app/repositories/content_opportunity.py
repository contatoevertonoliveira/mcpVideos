from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.content_opportunity import ContentOpportunity
from app.repositories.base import TenantScopedRepository


class ContentOpportunityRepository(TenantScopedRepository[ContentOpportunity]):
    model = ContentOpportunity

    def get_latest_for_idea(
        self, idea_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ContentOpportunity | None:
        stmt = (
            select(ContentOpportunity)
            .where(
                ContentOpportunity.organization_id == organization_id,
                ContentOpportunity.idea_id == idea_id,
            )
            .order_by(ContentOpportunity.created_at.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_latest_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[ContentOpportunity]:
        """One row per idea - its most recently computed evaluation."""
        stmt = (
            select(ContentOpportunity)
            .distinct(ContentOpportunity.idea_id)
            .where(
                ContentOpportunity.organization_id == organization_id,
                ContentOpportunity.channel_id == channel_id,
            )
            .order_by(ContentOpportunity.idea_id, ContentOpportunity.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

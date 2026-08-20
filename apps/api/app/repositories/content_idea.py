from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.content_idea import ContentIdea
from app.models.enums import IdeaStatus
from app.repositories.base import TenantScopedRepository


class ContentIdeaRepository(TenantScopedRepository[ContentIdea]):
    model = ContentIdea

    def list_active_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 100
    ) -> list[ContentIdea]:
        """Ideas not archived/rejected - the pool considered for dedup and
        shown by default on the Ideas screen."""
        stmt = (
            select(ContentIdea)
            .where(
                ContentIdea.organization_id == organization_id,
                ContentIdea.channel_id == channel_id,
                ContentIdea.status.notin_([IdeaStatus.REJECTED, IdeaStatus.ARCHIVED]),
            )
            .order_by(ContentIdea.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 100
    ) -> list[ContentIdea]:
        stmt = (
            select(ContentIdea)
            .where(
                ContentIdea.organization_id == organization_id,
                ContentIdea.channel_id == channel_id,
            )
            .order_by(ContentIdea.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

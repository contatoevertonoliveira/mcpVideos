from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.content_strategy import ContentStrategy
from app.models.enums import ContentStrategyStatus
from app.repositories.base import TenantScopedRepository


class ContentStrategyRepository(TenantScopedRepository[ContentStrategy]):
    model = ContentStrategy

    def get_active(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ContentStrategy | None:
        stmt = select(ContentStrategy).where(
            ContentStrategy.organization_id == organization_id,
            ContentStrategy.channel_id == channel_id,
            ContentStrategy.status == ContentStrategyStatus.ACTIVE,
        )
        return self.session.scalars(stmt).first()

    def get_latest_draft(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ContentStrategy | None:
        stmt = (
            select(ContentStrategy)
            .where(
                ContentStrategy.organization_id == organization_id,
                ContentStrategy.channel_id == channel_id,
                ContentStrategy.status == ContentStrategyStatus.DRAFT,
            )
            .order_by(ContentStrategy.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def get_latest_version_number(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> int:
        stmt = (
            select(ContentStrategy.version)
            .where(
                ContentStrategy.organization_id == organization_id,
                ContentStrategy.channel_id == channel_id,
            )
            .order_by(ContentStrategy.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first() or 0

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 50
    ) -> list[ContentStrategy]:
        stmt = (
            select(ContentStrategy)
            .where(
                ContentStrategy.organization_id == organization_id,
                ContentStrategy.channel_id == channel_id,
            )
            .order_by(ContentStrategy.version.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.content_pillar import ContentPillar
from app.repositories.base import TenantScopedRepository


class ContentPillarRepository(TenantScopedRepository[ContentPillar]):
    model = ContentPillar

    def list_by_strategy(
        self, strategy_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[ContentPillar]:
        stmt = (
            select(ContentPillar)
            .where(
                ContentPillar.organization_id == organization_id,
                ContentPillar.strategy_id == strategy_id,
            )
            .order_by(ContentPillar.priority.desc())
        )
        return list(self.session.scalars(stmt).all())

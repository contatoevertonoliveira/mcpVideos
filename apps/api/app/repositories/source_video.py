from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.source_video import SourceVideo
from app.repositories.base import TenantScopedRepository


class SourceVideoRepository(TenantScopedRepository[SourceVideo]):
    model = SourceVideo

    def get_by_external_id(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, external_video_id: str
    ) -> SourceVideo | None:
        stmt = select(SourceVideo).where(
            SourceVideo.organization_id == organization_id,
            SourceVideo.channel_id == channel_id,
            SourceVideo.external_video_id == external_video_id,
        )
        return self.session.scalars(stmt).first()

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[SourceVideo]:
        stmt = (
            select(SourceVideo)
            .where(
                SourceVideo.organization_id == organization_id, SourceVideo.channel_id == channel_id
            )
            .order_by(SourceVideo.published_at.desc().nulls_last())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt).all())

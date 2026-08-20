from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select

from app.models.source_video_metric import SourceVideoMetric
from app.repositories.base import TenantScopedRepository


class SourceVideoMetricRepository(TenantScopedRepository[SourceVideoMetric]):
    model = SourceVideoMetric

    def exists_for_capture(
        self, *, source_video_id: uuid.UUID, organization_id: uuid.UUID, captured_at: datetime
    ) -> bool:
        stmt = select(SourceVideoMetric.id).where(
            SourceVideoMetric.organization_id == organization_id,
            SourceVideoMetric.source_video_id == source_video_id,
            SourceVideoMetric.captured_at == captured_at,
        )
        return self.session.scalars(stmt).first() is not None

    def list_latest_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[SourceVideoMetric]:
        """One row per video - its most recently captured snapshot."""
        stmt = (
            select(SourceVideoMetric)
            .distinct(SourceVideoMetric.source_video_id)
            .where(
                SourceVideoMetric.organization_id == organization_id,
                SourceVideoMetric.channel_id == channel_id,
            )
            .order_by(SourceVideoMetric.source_video_id, SourceVideoMetric.captured_at.desc())
        )
        return list(self.session.scalars(stmt).all())

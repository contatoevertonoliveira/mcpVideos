from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.audience_profile import AudienceProfile
from app.repositories.base import TenantScopedRepository


class AudienceProfileRepository(TenantScopedRepository[AudienceProfile]):
    model = AudienceProfile

    def get_current(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> AudienceProfile | None:
        stmt = (
            select(AudienceProfile)
            .where(
                AudienceProfile.organization_id == organization_id,
                AudienceProfile.channel_id == channel_id,
            )
            .order_by(AudienceProfile.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

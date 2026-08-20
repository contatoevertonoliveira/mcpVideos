from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.brand_profile import BrandProfile
from app.repositories.base import TenantScopedRepository


class BrandProfileRepository(TenantScopedRepository[BrandProfile]):
    model = BrandProfile

    def get_by_channel(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> BrandProfile | None:
        stmt = select(BrandProfile).where(
            BrandProfile.organization_id == organization_id,
            BrandProfile.channel_id == channel_id,
        )
        return self.session.scalars(stmt).first()

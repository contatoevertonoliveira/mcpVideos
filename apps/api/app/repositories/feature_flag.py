from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.enums import FeatureFlagScope
from app.models.feature_flag import FeatureFlag
from app.repositories.base import BaseRepository


class FeatureFlagRepository(BaseRepository[FeatureFlag]):
    model = FeatureFlag

    def get_by_key_and_scope(
        self, key: str, scope_type: FeatureFlagScope, scope_id: uuid.UUID | None
    ) -> FeatureFlag | None:
        stmt = select(FeatureFlag).where(
            FeatureFlag.key == key,
            FeatureFlag.scope_type == scope_type,
            FeatureFlag.scope_id == scope_id,
        )
        return self.session.scalars(stmt).first()

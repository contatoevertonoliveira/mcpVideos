from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.opportunity_score import OpportunityScore
from app.repositories.base import TenantScopedRepository


class OpportunityScoreRepository(TenantScopedRepository[OpportunityScore]):
    model = OpportunityScore

    def list_by_opportunity(
        self, opportunity_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[OpportunityScore]:
        stmt = select(OpportunityScore).where(
            OpportunityScore.organization_id == organization_id,
            OpportunityScore.opportunity_id == opportunity_id,
        )
        return list(self.session.scalars(stmt).all())

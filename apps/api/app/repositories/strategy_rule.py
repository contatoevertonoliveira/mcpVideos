from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.strategy_rule import StrategyRule
from app.repositories.base import TenantScopedRepository


class StrategyRuleRepository(TenantScopedRepository[StrategyRule]):
    model = StrategyRule

    def list_active_by_strategy(
        self, strategy_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[StrategyRule]:
        stmt = select(StrategyRule).where(
            StrategyRule.organization_id == organization_id,
            StrategyRule.strategy_id == strategy_id,
            StrategyRule.active.is_(True),
        )
        return list(self.session.scalars(stmt).all())

    def list_by_strategy(
        self, strategy_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[StrategyRule]:
        stmt = select(StrategyRule).where(
            StrategyRule.organization_id == organization_id,
            StrategyRule.strategy_id == strategy_id,
        )
        return list(self.session.scalars(stmt).all())

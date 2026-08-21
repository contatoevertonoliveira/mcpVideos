from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.agent_run import AgentRun
from app.repositories.base import TenantScopedRepository


class AgentRunRepository(TenantScopedRepository[AgentRun]):
    model = AgentRun

    def list_by_correlation_id(
        self, correlation_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[AgentRun]:
        stmt = (
            select(AgentRun)
            .where(
                AgentRun.organization_id == organization_id,
                AgentRun.correlation_id == correlation_id,
            )
            .order_by(AgentRun.started_at.asc())
        )
        return list(self.session.scalars(stmt).all())

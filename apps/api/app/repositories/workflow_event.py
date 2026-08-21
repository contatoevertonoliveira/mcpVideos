from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.workflow_event import WorkflowEvent
from app.repositories.base import TenantScopedRepository


class WorkflowEventRepository(TenantScopedRepository[WorkflowEvent]):
    model = WorkflowEvent

    def list_by_run(
        self, workflow_run_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[WorkflowEvent]:
        stmt = (
            select(WorkflowEvent)
            .where(
                WorkflowEvent.organization_id == organization_id,
                WorkflowEvent.workflow_run_id == workflow_run_id,
            )
            .order_by(WorkflowEvent.created_at.asc())
        )
        return list(self.session.scalars(stmt).all())

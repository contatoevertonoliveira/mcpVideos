from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.workflow_step import WorkflowStep
from app.repositories.base import TenantScopedRepository


class WorkflowStepRepository(TenantScopedRepository[WorkflowStep]):
    model = WorkflowStep

    def get_by_key(
        self, *, workflow_run_id: uuid.UUID, step_key: str, organization_id: uuid.UUID
    ) -> WorkflowStep | None:
        stmt = select(WorkflowStep).where(
            WorkflowStep.organization_id == organization_id,
            WorkflowStep.workflow_run_id == workflow_run_id,
            WorkflowStep.step_key == step_key,
        )
        return self.session.scalars(stmt).first()

    def list_by_run(
        self, workflow_run_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> list[WorkflowStep]:
        stmt = (
            select(WorkflowStep)
            .where(
                WorkflowStep.organization_id == organization_id,
                WorkflowStep.workflow_run_id == workflow_run_id,
            )
            .order_by(WorkflowStep.sequence.asc())
        )
        return list(self.session.scalars(stmt).all())

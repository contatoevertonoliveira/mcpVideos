from __future__ import annotations

from app.models.workflow_run import WorkflowRun
from app.repositories.base import TenantScopedRepository


class WorkflowRunRepository(TenantScopedRepository[WorkflowRun]):
    model = WorkflowRun

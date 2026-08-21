from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.workflow_version import WorkflowVersion
from app.repositories.base import BaseRepository


class WorkflowVersionRepository(BaseRepository[WorkflowVersion]):
    model = WorkflowVersion

    def get_latest(self, workflow_definition_id: uuid.UUID) -> WorkflowVersion | None:
        stmt = (
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_definition_id == workflow_definition_id)
            .order_by(WorkflowVersion.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

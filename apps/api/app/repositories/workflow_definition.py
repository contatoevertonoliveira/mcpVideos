from __future__ import annotations

from sqlalchemy import select

from app.models.workflow_definition import WorkflowDefinition
from app.repositories.base import BaseRepository


class WorkflowDefinitionRepository(BaseRepository[WorkflowDefinition]):
    model = WorkflowDefinition

    def get_by_slug(self, slug: str) -> WorkflowDefinition | None:
        stmt = select(WorkflowDefinition).where(WorkflowDefinition.slug == slug)
        return self.session.scalars(stmt).first()

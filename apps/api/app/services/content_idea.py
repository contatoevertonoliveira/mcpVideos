from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, NotFoundError
from app.models.content_idea import ContentIdea
from app.models.enums import AuditActorType, IdeaStatus
from app.repositories.content_idea import ContentIdeaRepository
from app.services.audit import AuditService


class ContentIdeaService:
    """Documento 03, secao 22. Plain lifecycle actions on an idea that
    don't belong to generation or evaluation - today just the human
    "approve" action (Documento 08A sec. 35's Opportunity Card
    "[Adicionar]" concept)."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.ideas = ContentIdeaRepository(session)
        self.audit = AuditService(session)

    def approve(
        self,
        *,
        channel_id: uuid.UUID,
        idea_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ContentIdea:
        idea = self.ideas.get_by_id(idea_id, organization_id=organization_id)
        if idea is None or idea.channel_id != channel_id:
            raise NotFoundError("Idea not found", code="IDEA_NOT_FOUND")
        if idea.status not in (IdeaStatus.DRAFT, IdeaStatus.RECOMMENDED):
            raise DomainError(
                f"Idea is {idea.status.value}, not draft or recommended", code="IDEA_NOT_APPROVABLE"
            )

        idea.status = IdeaStatus.APPROVED
        self.session.flush()

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            action="idea.approved",
            resource_type="content_idea",
            resource_id=idea.id,
        )
        return idea

from __future__ import annotations

from app.models.idea_relationship import IdeaRelationship
from app.repositories.base import TenantScopedRepository


class IdeaRelationshipRepository(TenantScopedRepository[IdeaRelationship]):
    model = IdeaRelationship

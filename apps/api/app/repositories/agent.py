from __future__ import annotations

from sqlalchemy import select

from app.models.agent import Agent
from app.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    model = Agent

    def get_by_slug(self, slug: str) -> Agent | None:
        stmt = select(Agent).where(Agent.slug == slug)
        return self.session.scalars(stmt).first()

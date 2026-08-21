from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.agent_prompt import AgentPrompt
from app.repositories.base import BaseRepository


class AgentPromptRepository(BaseRepository[AgentPrompt]):
    model = AgentPrompt

    def get_by_checksum(self, agent_id: uuid.UUID, checksum: str) -> AgentPrompt | None:
        stmt = select(AgentPrompt).where(
            AgentPrompt.agent_id == agent_id, AgentPrompt.checksum == checksum
        )
        return self.session.scalars(stmt).first()

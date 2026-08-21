from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.agent_version import AgentVersion
from app.models.enums import AgentVersionStatus
from app.repositories.base import BaseRepository


class AgentVersionRepository(BaseRepository[AgentVersion]):
    model = AgentVersion

    def get_active(self, agent_id: uuid.UUID) -> AgentVersion | None:
        stmt = select(AgentVersion).where(
            AgentVersion.agent_id == agent_id, AgentVersion.status == AgentVersionStatus.ACTIVE
        )
        return self.session.scalars(stmt).first()

    def get_latest_version_number(self, agent_id: uuid.UUID) -> int:
        stmt = (
            select(AgentVersion.version)
            .where(AgentVersion.agent_id == agent_id)
            .order_by(AgentVersion.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first() or 0

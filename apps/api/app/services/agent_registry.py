"""Agent Registry (Documento 02, secao 28; Documento 03, secoes 42-44;
Documento 10 Fase 11).

Bridges the file-based prompts already used since Fase 06
(``app/agents/prompts/<agent_id>/v<N>.md``) into a DB-backed, versioned
catalog: Agent (the catalog entry) -> AgentVersion (provider/model
pinned at a point in time) -> AgentPrompt (the actual text, content-
addressed by checksum).

``ensure_current_version`` is deliberately idempotent and self-seeding:
the first time any agent runs, it registers itself; every subsequent run
reuses the same AgentVersion unless the prompt file's content actually
changed, in which case a new version is minted automatically - never
mutating the existing one (CLAUDE.md: "nunca alterar versao existente
silenciosamente"). There is no separate manual seed script to remember
to run.
"""

from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_prompt import AgentPrompt
from app.models.agent_version import AgentVersion
from app.models.enums import AgentVersionStatus
from app.repositories.agent import AgentRepository
from app.repositories.agent_prompt import AgentPromptRepository
from app.repositories.agent_version import AgentVersionRepository


class AgentRegistryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.agents = AgentRepository(session)
        self.agent_versions = AgentVersionRepository(session)
        self.agent_prompts = AgentPromptRepository(session)

    def ensure_current_version(
        self,
        *,
        slug: str,
        name: str,
        category: str,
        provider: str,
        model: str,
        system_prompt: str,
    ) -> AgentVersion:
        agent = self.agents.get_by_slug(slug)
        if agent is None:
            agent = Agent(name=name, slug=slug, category=category, active=True)
            self.agents.add(agent)

        checksum = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
        active_version = self.agent_versions.get_active(agent.id)
        if active_version is not None and active_version.prompt_id is not None:
            active_prompt = self.session.get(AgentPrompt, active_version.prompt_id)
            if active_prompt is not None and active_prompt.checksum == checksum:
                return active_version

        next_version = self.agent_versions.get_latest_version_number(agent.id) + 1
        prompt = AgentPrompt(
            agent_id=agent.id, version=next_version, system_prompt=system_prompt, checksum=checksum
        )
        self.agent_prompts.add(prompt)

        if active_version is not None:
            active_version.status = AgentVersionStatus.DEPRECATED
            # Same reasoning as ChannelDNAVersion/ContentStrategy: both rows
            # would otherwise compete for "the" active version transiently.
            self.session.flush()

        new_version = AgentVersion(
            agent_id=agent.id,
            version=next_version,
            provider=provider,
            model=model,
            prompt_id=prompt.id,
            status=AgentVersionStatus.ACTIVE,
        )
        return self.agent_versions.add(new_version)

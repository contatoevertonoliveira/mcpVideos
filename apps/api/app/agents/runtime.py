"""AgentRuntime (Documento 10 Fase 11: "AgentRuntime, structured outputs,
prompt registry"). Every structured-agent call goes through the Agent
Registry (versioned prompt/model catalog, ``app/services/agent_registry.py``)
and records an ``AgentRun`` row - the "execute versioned agent", "record
run" and "trace operation" acceptance criteria.

Prompt files under ``agents/prompts/<agent_id>/v<N>.md`` remain the
canonical source of prompt text (Documento 02 sec. 29) - this module only
adds a persistence layer on top, it does not replace the file-based
authoring workflow.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.gateways.llm import LLMGateway
from app.models.agent_run import AgentRun
from app.models.enums import AgentRunStatus
from app.repositories.agent_run import AgentRunRepository
from app.services.agent_registry import AgentRegistryService

_PROMPTS_DIR = Path(__file__).parent / "prompts"

T = TypeVar("T", bound=BaseModel)


@lru_cache
def load_prompt(agent_id: str, version: str) -> str:
    path = _PROMPTS_DIR / agent_id / f"{version}.md"
    return path.read_text(encoding="utf-8").strip()


async def run_structured_agent(
    gateway: LLMGateway,
    *,
    agent_id: str,
    version: str,
    user_prompt: str,
    response_model: type[T],
    session: Session,
    organization_id: uuid.UUID,
    channel_id: uuid.UUID | None = None,
    workflow_run_id: uuid.UUID | None = None,
    workflow_step_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
    category: str = "intelligence",
) -> T:
    system_prompt = load_prompt(agent_id, version)
    settings = get_settings()
    agent_version = AgentRegistryService(session).ensure_current_version(
        slug=agent_id,
        name=agent_id.replace("_", " ").title(),
        category=category,
        provider="anthropic",
        model=settings.llm_model,
        system_prompt=system_prompt,
    )

    run = AgentRunRepository(session).add(
        AgentRun(
            organization_id=organization_id,
            agent_version_id=agent_version.id,
            channel_id=channel_id,
            workflow_run_id=workflow_run_id,
            workflow_step_id=workflow_step_id,
            status=AgentRunStatus.RUNNING,
            input_json={"user_prompt": user_prompt},
            correlation_id=correlation_id,
        )
    )

    try:
        result = await gateway.generate_structured(
            prompt_id=f"{agent_id}.{version}",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=response_model,
        )
    except Exception as exc:
        run.status = AgentRunStatus.FAILED
        run.error_message = str(exc)[:2000]
        run.completed_at = datetime.now(UTC)
        session.flush()
        raise

    run.status = AgentRunStatus.COMPLETED
    run.output_json = result.model_dump(mode="json")
    run.completed_at = datetime.now(UTC)
    session.flush()
    return result

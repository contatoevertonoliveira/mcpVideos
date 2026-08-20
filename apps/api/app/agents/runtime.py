"""AgentRuntime foundation (Documento 10 Fase 06: "versao minima... somente
o necessario. A arquitetura completa chega na Fase 11").

Two small pieces of shared plumbing every agent needs: loading a
versioned prompt file (Documento 02 sec. 29, Documento 05 sec. 51 -
``agents/prompts/<agent_id>/v<N>.md``) and calling the LLMGateway with
that prompt. No agent registry, no DB-backed prompt/version tracking, no
run persistence yet - that is Fase 11's job.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.gateways.llm import LLMGateway

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
) -> T:
    system_prompt = load_prompt(agent_id, version)
    return await gateway.generate_structured(
        prompt_id=f"{agent_id}.{version}",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=response_model,
    )

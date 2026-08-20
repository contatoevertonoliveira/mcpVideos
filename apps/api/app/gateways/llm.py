"""LLMGateway (Documento 02, secao 31; Documento 06 gateway pattern).

Agents never call an LLM API directly - only through this abstraction
(Documento 02, secao 30-31: "toda comunicacao com LLM devera ocorrer
atraves de LLMGateway"). Two implementations, same pattern as
YouTubeGateway (Fase 04): a real one (Anthropic Messages API, called
directly via httpx - no SDK dependency, matching GoogleYouTubeGateway's
style) and a deterministic fake for local dev/tests without an API key
(Documento 02, secao 71 - "FakeLLMGateway").

This is deliberately the *minimal* version the Fase 06 plan allows
("Pode criar versao minima de LLMGateway, AgentRuntime foundation -
somente o necessario. A arquitetura completa chega na Fase 11"): no
provider/model registry, no routing, no cost tracking - those arrive
with the Model Router (Fase 14).
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import Settings

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"

T = TypeVar("T", bound=BaseModel)


class LLMGenerationError(Exception):
    """Raised when the LLM response could not be parsed into the expected
    structured schema, even after a retry."""


class LLMGateway(ABC):
    @abstractmethod
    async def generate(self, *, system_prompt: str, user_prompt: str) -> str: ...

    @abstractmethod
    async def generate_structured(
        self, *, prompt_id: str, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T: ...

    async def stream(self, *args: Any, **kwargs: Any) -> Any:
        # No real-time UI consumes token streams yet - wiring this up now
        # would be an untested, unused code path (CLAUDE.md: no misleading
        # placeholders).
        raise NotImplementedError("LLMGateway.stream is not needed by any caller yet")


class AnthropicLLMGateway(LLMGateway):
    """Talks to the real Anthropic Messages API."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.anthropic_api_key
        self._model = settings.llm_model

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                ANTHROPIC_MESSAGES_URL,
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "content-type": "application/json",
                },
                json={
                    "model": self._model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        return "".join(block["text"] for block in payload["content"] if block["type"] == "text")

    async def generate_structured(
        self, *, prompt_id: str, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        schema_instructions = (
            "\n\nRespond with ONLY a single JSON object matching this schema, "
            "no prose, no markdown fences:\n"
            f"{json.dumps(response_model.model_json_schema())}"
        )
        raw = await self.generate(
            system_prompt=system_prompt + schema_instructions, user_prompt=user_prompt
        )
        try:
            return response_model.model_validate_json(raw)
        except (ValidationError, ValueError):
            # One controlled retry, asking the model to fix its own output
            # (Documento 02 sec. 23: retries controlados, nunca infinitos).
            retry_raw = await self.generate(
                system_prompt=system_prompt + schema_instructions,
                user_prompt=(
                    f"{user_prompt}\n\nYour previous response was not valid JSON matching the "
                    f"schema. Previous response:\n{raw}\n\nReturn only the corrected JSON object."
                ),
            )
            try:
                return response_model.model_validate_json(retry_raw)
            except (ValidationError, ValueError) as exc:
                raise LLMGenerationError(
                    f"prompt_id={prompt_id!r} did not produce valid structured output "
                    f"after retry: {exc}"
                ) from exc


class FakeLLMGateway(LLMGateway):
    """Deterministic, network-free double for local dev and tests
    (Documento 02, secao 71). Enabled while LLM_FAKE_GATEWAY=true.

    Returns a fixed, realistic canned response per known ``prompt_id`` -
    same spirit as FakeYouTubeGateway returning one fixed channel, not a
    generic "fill in blanks" reflection trick.
    """

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return "Fake LLM response - see FakeLLMGateway.generate_structured for structured output."

    async def generate_structured(
        self, *, prompt_id: str, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        canned = _CANNED_RESPONSES.get(prompt_id)
        if canned is None:
            raise LLMGenerationError(
                f"FakeLLMGateway has no canned response for prompt_id={prompt_id!r}"
            )
        return response_model.model_validate(canned)


_CANNED_RESPONSES: dict[str, dict[str, Any]] = {
    "channel_analyst.v1": {
        "classification": {
            "primary_language": "pt-BR",
            "primary_category": "Tecnologia e Reviews",
        },
        "content_patterns": [
            "Videos curtos (Shorts) usados como teasers de videos longos",
            "Titulos com perguntas diretas ao espectador",
        ],
        "format_patterns": ["short", "long_form"],
        "publishing_patterns": ["Publicacoes concentradas no inicio do mes"],
        "high_performing_patterns": ["Videos long_form acima de 5 minutos com mais visualizacoes"],
        "low_performing_patterns": ["Shorts sem thumbnail customizada"],
        "anomalies": [],
        "confidence": 0.62,
        "evidence": [
            "5 videos analisados (2 shorts, 3 long_form)",
            "1 playlist de uploads identificada",
        ],
    },
    "audience_analyst.v1": {
        "audience_segments": ["Entusiastas de tecnologia", "Early adopters"],
        "estimated_age_ranges": ["18-24", "25-34"],
        "language": "pt-BR",
        "interests": ["tecnologia", "reviews de produtos", "tutoriais"],
        "content_preferences": ["Videos comparativos", "Reviews em profundidade"],
        "format_preferences": ["long_form"],
        "confidence": 0.55,
        "evidence": ["Inferido a partir de titulos/descricoes - sem YouTube Analytics real ainda"],
    },
    "strategy_agent.v1": {
        "objectives": [
            "Crescer inscritos qualificados no nicho de tecnologia",
            "Aumentar retencao media dos videos long_form",
        ],
        "content_mix": {"shorts_ratio": 0.35, "long_form_ratio": 0.55},
        "content_pillars": [
            {
                "name": "Reviews em profundidade",
                "description": "Analises completas de produtos de tecnologia",
                "target_ratio": 0.4,
                "priority": 3,
            },
            {
                "name": "Comparativos",
                "description": "Comparacoes diretas entre produtos concorrentes",
                "target_ratio": 0.3,
                "priority": 2,
            },
            {
                "name": "Bastidores/Shorts",
                "description": "Teasers curtos dos videos longos",
                "target_ratio": 0.3,
                "priority": 1,
            },
        ],
        "publishing_frequency": {"long_form": "2x por semana", "short": "5x por semana"},
        "format_strategy": {"primary": "long_form", "secondary": "short"},
        "experimental_ratio": 0.1,
        "recommendations": [
            "Testar thumbnails customizadas em todos os Shorts",
            "Concentrar publicacoes long_form no inicio do mes, como no historico",
        ],
        "risks": ["Amostra de apenas 5 videos - confianca limitada ate mais dados"],
        "confidence": 0.58,
    },
}


def get_llm_gateway(settings: Settings) -> LLMGateway:
    if settings.llm_fake_gateway:
        return FakeLLMGateway()
    return AnthropicLLMGateway(settings)

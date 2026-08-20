"""Structured output contracts for the project's agents (Documento 05).

Exact shape of the JSON each agent must return - kept separate from the
DB models on purpose: the agent output is richer than what the
lightweight profile tables persist (Documento 03 secoes 15/17). The full
structured output (patterns, anomalies, evidence) is the raw material
Channel DNA versions (Fase 07); Fase 06's ChannelProfile/AudienceProfile
only distill it into a short summary.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChannelAnalystOutput(BaseModel):
    classification: dict[str, str] = Field(default_factory=dict)
    content_patterns: list[str] = Field(default_factory=list)
    format_patterns: list[str] = Field(default_factory=list)
    publishing_patterns: list[str] = Field(default_factory=list)
    high_performing_patterns: list[str] = Field(default_factory=list)
    low_performing_patterns: list[str] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
    confidence: float
    evidence: list[str] = Field(default_factory=list)


class AudienceAnalystOutput(BaseModel):
    audience_segments: list[str] = Field(default_factory=list)
    estimated_age_ranges: list[str] = Field(default_factory=list)
    language: str = ""
    interests: list[str] = Field(default_factory=list)
    content_preferences: list[str] = Field(default_factory=list)
    format_preferences: list[str] = Field(default_factory=list)
    confidence: float
    evidence: list[str] = Field(default_factory=list)


class ContentPillarSuggestion(BaseModel):
    name: str
    description: str = ""
    target_ratio: float
    priority: int = 0


class StrategyAgentOutput(BaseModel):
    """Documento 05, secao 8. ``content_mix`` carries the shorts/long-form
    split (keys ``shorts_ratio``/``long_form_ratio``) - kept as a generic
    dict here as the doc specifies, mapped to ContentStrategy's dedicated
    columns by the service."""

    objectives: list[str] = Field(default_factory=list)
    content_mix: dict[str, float] = Field(default_factory=dict)
    content_pillars: list[ContentPillarSuggestion] = Field(default_factory=list)
    publishing_frequency: dict[str, str] = Field(default_factory=dict)
    format_strategy: dict[str, str] = Field(default_factory=dict)
    experimental_ratio: float = 0.0
    recommendations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float


class IdeaSuggestion(BaseModel):
    """Documento 05, secao 10."""

    title: str
    summary: str = ""
    recommended_format: str = ""
    content_pillar: str = ""
    hook_concept: str = ""
    reason: str = ""
    source_type: str = "ai"
    novelty: float = 0.0
    confidence: float = 0.0


class IdeaAgentOutput(BaseModel):
    ideas: list[IdeaSuggestion] = Field(default_factory=list)


class OpportunityEvaluatorOutput(BaseModel):
    """Documento 05, secao 11. Deliberately does NOT include the agent's
    own ``final_score``/``recommendation`` fields from the doc's example -
    Documento 10 Fase 09 requires the final weighted score and the
    approve/reject outcome to be computed in code from these raw
    components, never trusted directly from the LLM."""

    channel_fit: float
    audience_fit: float
    trend: float
    novelty: float
    retention_potential: float
    search_potential: float
    competition: float
    brand_fit: float
    strategic_fit: float
    confidence: float
    reasoning_summary: str = ""

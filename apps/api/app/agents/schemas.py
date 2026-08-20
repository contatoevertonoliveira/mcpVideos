"""Structured output contracts for Fase 06 agents (Documento 05, secoes 6-7).

Exact shape of the JSON each agent must return - kept separate from the
DB models (``ChannelProfile``/``AudienceProfile``) on purpose: the agent
output is richer than what Fase 06's lightweight profile tables persist
(Documento 03 secoes 15/17). The full structured output (patterns,
anomalies, evidence) is the raw material Channel DNA will version in
Fase 07 - Fase 06 only distills it into a short summary.
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

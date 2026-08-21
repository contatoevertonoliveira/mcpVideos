"""Pure, agent-independent calendar balance/conflict checks.

The Calendar Planner agent (Documento 05, secao 12) only proposes which
approved ideas to schedule when. Whether the resulting batch is actually
balanced against the active strategy, and whether it collides with what
is already on the calendar, is computed here in code - never trusted
from the agent's own opinion (Documento 07 secoes 58-59; Documento 10
Fase 10 Definition of Done: "pillar balance checked", "format mix
checked", "conflicts detected"). Same principle as
``app/services/opportunity_scoring.py`` in Fase 09.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.models.content_pillar import ContentPillar
from app.models.content_strategy import ContentStrategy


@dataclass
class PlannedItem:
    content_type: str
    planned_at: datetime
    content_pillar: str | None = None


def build_format_balance(batch: list[PlannedItem], strategy: ContentStrategy) -> dict[str, float]:
    if not batch:
        return {}
    total = len(batch)
    shorts = sum(1 for item in batch if item.content_type == "short")
    long_form = sum(1 for item in batch if item.content_type == "long_form")
    return {
        "shorts_ratio_actual": round(shorts / total, 4),
        "shorts_ratio_target": strategy.shorts_ratio,
        "long_form_ratio_actual": round(long_form / total, 4),
        "long_form_ratio_target": strategy.long_form_ratio,
    }


def build_pillar_balance(
    batch: list[PlannedItem], pillars: list[ContentPillar]
) -> dict[str, dict[str, float]]:
    if not batch or not pillars:
        return {}
    total = len(batch)
    return {
        pillar.name: {
            "actual_ratio": round(
                sum(1 for item in batch if item.content_pillar == pillar.name) / total, 4
            ),
            "target_ratio": pillar.target_ratio,
        }
        for pillar in pillars
    }


def detect_conflicts(batch: list[PlannedItem], existing: list[PlannedItem]) -> list[str]:
    """Two items landing on the same calendar day is flagged as a
    conflict (Documento 08 sec. 34 example: "Este horario ja possui outra
    publicacao") - informational, not blocking. Auto-resolution via
    drag-and-drop is explicitly deferred (Documento 08 sec. 32: "pode ser
    adicionado quando estavel")."""
    occupied: dict[date, int] = {}
    for item in existing:
        day = item.planned_at.date()
        occupied[day] = occupied.get(day, 0) + 1

    conflicts: list[str] = []
    for item in batch:
        day = item.planned_at.date()
        count = occupied.get(day, 0)
        if count > 0:
            conflicts.append(f"{day.isoformat()} ja possui {count} publicacao(oes) planejada(s)")
        occupied[day] = count + 1
    return conflicts

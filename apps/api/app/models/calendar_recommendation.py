from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin


class CalendarRecommendation(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 27 (listada, sem lista de campos propria);
    Documento 05, secao 12 (Calendar Planner). Metadados de uma rodada do
    Calendar Planner - o "batch" que produziu um conjunto de CalendarItem.
    ``balance_report_json``/``conflicts_json`` sao calculados em codigo
    por ``app/services/calendar_balance.py`` (Documento 10 Fase 10 DoD:
    "pillar balance checked", "format mix checked", "conflicts detected"),
    nunca copiados diretamente da opiniao do agente - mesmo principio do
    ``opportunity_score`` na Fase 09."""

    __tablename__ = "calendar_recommendations"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    balance_report_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    conflicts_json: Mapped[list[Any]] = mapped_column(JSONB, default=list, nullable=False)

    # Mesmo padrao de ChannelDNAVersion/ContentStrategy/ContentIdea: sem FK
    # de verdade ate agent_runs existir (Fase 11).
    generated_by_agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

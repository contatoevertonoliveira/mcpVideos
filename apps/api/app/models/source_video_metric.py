from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin


class SourceVideoMetric(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 14. Tabela historica - nunca sobrescrever, cada
    sync insere uma nova linha por video em ``captured_at``. Sem
    TimestampMixin de proposito: nao ha "updated_at" para um snapshot
    imutavel, so o momento em que foi capturado.

    Campos vindos da YouTube Analytics API (subscribers_gained/lost,
    watch_time_minutes, average_view_duration/percentage, impressions,
    impressions_ctr) ficam NULL por enquanto - essa API exige escopo/fluxo
    proprio e fica para a Fase 19 (Analytics & Learning Engine), conforme
    Documento 03 sec. 14: "campos especificos podem permanecer nulos caso
    a API nao os forneca". A Fase 05 preenche apenas as estatisticas
    publicas (views/likes/comments) do YouTube Data API v3.
    """

    __tablename__ = "source_video_metrics"
    __table_args__ = (
        UniqueConstraint(
            "source_video_id", "captured_at", name="uq_source_video_metrics_video_captured_at"
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    source_video_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="CASCADE"), nullable=False
    )

    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    views: Mapped[int | None] = mapped_column(BigInteger, default=None)
    likes: Mapped[int | None] = mapped_column(BigInteger, default=None)
    comments: Mapped[int | None] = mapped_column(BigInteger, default=None)
    watch_time_minutes: Mapped[float | None] = mapped_column(Float, default=None)
    average_view_duration: Mapped[float | None] = mapped_column(Float, default=None)
    average_view_percentage: Mapped[float | None] = mapped_column(Float, default=None)

    subscribers_gained: Mapped[int | None] = mapped_column(Integer, default=None)
    subscribers_lost: Mapped[int | None] = mapped_column(Integer, default=None)

    impressions: Mapped[int | None] = mapped_column(BigInteger, default=None)
    impressions_ctr: Mapped[float | None] = mapped_column(Float, default=None)

    raw_metrics_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

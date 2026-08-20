from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import ContentStrategyStatus


class ContentStrategy(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 19; Documento 05, secao 8 (Strategy Agent).
    Como ChannelDNAVersion, cada geracao cria uma NOVA versao imutavel -
    mas ao contrario do DNA, a transicao draft->active exige aprovacao
    explicita do usuario (o agente "nao pode ativar estrategia sozinho
    sem policy")."""

    __tablename__ = "content_strategies"
    __table_args__ = (
        UniqueConstraint("channel_id", "version", name="uq_content_strategies_channel_version"),
        Index(
            "uq_content_strategies_one_active_per_channel",
            "channel_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ContentStrategyStatus] = mapped_column(
        Enum(ContentStrategyStatus, name="content_strategy_status", native_enum=False),
        default=ContentStrategyStatus.DRAFT,
        nullable=False,
    )

    objective: Mapped[str] = mapped_column(String(1000), nullable=False)
    shorts_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    long_form_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    experimental_ratio: Mapped[float] = mapped_column(Float, nullable=False)

    recommended_frequency_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    strategy_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Mesmo padrao de ChannelDNAVersion.generated_by_agent_run_id: sem FK de
    # verdade ate agent_runs existir (Fase 11), guarda o correlation_id da
    # task Celery que gerou esta versao.
    generated_by_agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

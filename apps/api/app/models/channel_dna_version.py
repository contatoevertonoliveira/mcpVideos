from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChannelDNAStatus


class ChannelDNAVersion(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 16. Memoria editorial estruturada e versionada -
    "tabela critica". Ao contrario de ChannelProfile (resumo leve,
    sobrescrito), cada geracao aqui cria uma NOVA versao imutavel; apenas
    o status de uma delas transita (draft -> active -> superseded)."""

    __tablename__ = "channel_dna_versions"
    __table_args__ = (
        UniqueConstraint("channel_id", "version", name="uq_channel_dna_versions_channel_version"),
        Index(
            "uq_channel_dna_versions_one_active_per_channel",
            "channel_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ChannelDNAStatus] = mapped_column(
        Enum(ChannelDNAStatus, name="channel_dna_status", native_enum=False),
        default=ChannelDNAStatus.DRAFT,
        nullable=False,
    )

    classification_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    audience_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    formats_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_patterns_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    performance_patterns_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    brand_rules_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    publishing_patterns_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    restrictions_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    recommendations_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Nao e uma FK de verdade: agent_runs (Fase 11) ainda nao existe. Guarda
    # o correlation_id da task Celery que gerou esta versao - ja rastreavel
    # via logs/audit_logs hoje, e passa a poder virar FK real quando
    # agent_runs existir, sem precisar de backfill (o valor ja e o mesmo
    # run_id conceitual).
    generated_by_agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

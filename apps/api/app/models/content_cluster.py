from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import ContentClusterStatus


class ContentCluster(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 25. Agrupa conteudos relacionados (ex.: video
    principal + Shorts derivados). Criada nesta fase por exigencia do
    Documento 10 F09, mas sem atribuicao automatica ainda - nenhum
    contrato de agente (Documento 05) desta fase produz clusterizacao;
    isso fica para quando houver um algoritmo/agente real dedicado a
    isso. CRUD basico, sem endpoints de API ainda (ver docs/ui.md)."""

    __tablename__ = "content_clusters"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(200), default=None)
    status: Mapped[ContentClusterStatus] = mapped_column(
        Enum(ContentClusterStatus, name="content_cluster_status", native_enum=False),
        default=ContentClusterStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

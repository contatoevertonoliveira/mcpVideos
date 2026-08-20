from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin


class ChannelProfile(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 15. "Visao resumida atual" do canal - uma linha
    por canal, sobrescrita a cada nova analise (diferente de Channel DNA,
    que sera versionado e chega na Fase 07)."""

    __tablename__ = "channel_profiles"
    __table_args__ = (UniqueConstraint("channel_id", name="uq_channel_profiles_channel_id"),)

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    primary_language: Mapped[str | None] = mapped_column(String(16), default=None)
    primary_category: Mapped[str | None] = mapped_column(String(200), default=None)
    estimated_audience: Mapped[str | None] = mapped_column(String(500), default=None)
    content_summary: Mapped[str | None] = mapped_column(Text, default=None)

    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

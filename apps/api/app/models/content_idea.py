from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import IdeaOrigin, IdeaStatus


class ContentIdea(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 22; Documento 05, secao 10 (Idea Agent).
    Representa uma pauta ainda nao necessariamente aprovada."""

    __tablename__ = "content_ideas"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, default=None)

    idea_type: Mapped[str | None] = mapped_column(String(100), default=None)
    origin: Mapped[IdeaOrigin] = mapped_column(
        Enum(IdeaOrigin, name="idea_origin", native_enum=False),
        default=IdeaOrigin.AI,
        nullable=False,
    )
    status: Mapped[IdeaStatus] = mapped_column(
        Enum(IdeaStatus, name="idea_status", native_enum=False),
        default=IdeaStatus.DRAFT,
        nullable=False,
    )
    recommended_format: Mapped[str | None] = mapped_column(String(50), default=None)

    # Mesmo padrao de ChannelDNAVersion/ContentStrategy: sem FK de verdade
    # ate agent_runs existir (Fase 11).
    generated_by_agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

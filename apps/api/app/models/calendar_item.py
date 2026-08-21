from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import CalendarItemSource, CalendarItemStatus, SourceVideoType


class CalendarItem(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 27; Documento 05, secao 12 (Calendar Planner);
    Documento 10 Fase 10. Um slot de publicacao sugerido ou planejado para
    o canal - transforma oportunidades aprovadas em plano editorial."""

    __tablename__ = "calendar_items"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    idea_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("content_ideas.id", ondelete="SET NULL"), default=None
    )
    # Sem FK de verdade - content_projects so chega numa fase futura
    # (Documento 03 sec. 119 atribui calendar_items a Fase 10; content_
    # projects nao esta nessa lista). Mesmo padrao de "sem FK prematura"
    # ja usado em generated_by_agent_run_id em fases anteriores.
    project_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)
    calendar_recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("calendar_recommendations.id", ondelete="SET NULL"),
        default=None,
    )

    content_type: Mapped[SourceVideoType] = mapped_column(
        Enum(SourceVideoType, name="source_video_type", native_enum=False), nullable=False
    )
    planned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[CalendarItemStatus] = mapped_column(
        Enum(CalendarItemStatus, name="calendar_item_status", native_enum=False),
        default=CalendarItemStatus.SUGGESTED,
        nullable=False,
    )
    source: Mapped[CalendarItemSource] = mapped_column(
        Enum(CalendarItemSource, name="calendar_item_source", native_enum=False),
        default=CalendarItemSource.AI,
        nullable=False,
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

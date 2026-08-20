from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import OpportunityStatus


class ContentOpportunity(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 23. Uma ideia ja contextualizada e avaliada -
    ``opportunity_score`` e o resultado do calculo em codigo (Documento 10
    Fase 09), nunca o "final_score" opinativo do agente."""

    __tablename__ = "content_opportunities"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    idea_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("content_ideas.id", ondelete="CASCADE"), nullable=False
    )

    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)

    recommended_format: Mapped[str | None] = mapped_column(String(50), default=None)
    recommended_duration: Mapped[int | None] = mapped_column(Integer, default=None)
    recommended_publish_window: Mapped[str | None] = mapped_column(String(100), default=None)

    reasoning_summary: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status", native_enum=False), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

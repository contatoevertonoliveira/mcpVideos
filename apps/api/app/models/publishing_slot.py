from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import DayOfWeek, SourceVideoType


class PublishingSlot(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 28. Janela recomendada recorrente de
    publicacao (ex.: "segunda, 10:00, short") - CRUD simples do usuario,
    nao gerado por agente. Usada pelo Calendar Planner como contexto ao
    espacar itens sugeridos, mesmo espirito de ``brand_profiles``/
    ``strategy_rules`` em fases anteriores."""

    __tablename__ = "publishing_slots"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    day_of_week: Mapped[DayOfWeek] = mapped_column(
        Enum(DayOfWeek, name="day_of_week", native_enum=False), nullable=False
    )
    local_time: Mapped[time] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    content_type: Mapped[SourceVideoType] = mapped_column(
        Enum(SourceVideoType, name="source_video_type", native_enum=False), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

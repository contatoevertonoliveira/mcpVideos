from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class BrandProfile(UUIDPrimaryKeyMixin, OrganizationScopedMixin, TimestampMixin, Base):
    """Documento 03, secao 18. Diferente de Channel/Audience profile, este
    e definido pelo usuario (identidade visual/tom de voz), nao inferido
    por agente - por isso uma linha por canal, sem versionamento."""

    __tablename__ = "brand_profiles"
    __table_args__ = (UniqueConstraint("channel_id", name="uq_brand_profiles_channel_id"),)

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str | None] = mapped_column(String(200), default=None)

    colors_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    typography_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    visual_style_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    tone_of_voice_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    rules_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    prohibited_elements_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

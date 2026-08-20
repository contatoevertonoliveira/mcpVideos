from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import AudienceProfileSource


class AudienceProfile(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 17. Versionada e imutavel (append-only) - cada
    analise insere uma nova linha em vez de sobrescrever a anterior, ao
    contrario de ChannelProfile. A versao mais recente por canal e a
    corrente."""

    __tablename__ = "audience_profiles"
    __table_args__ = (
        UniqueConstraint("channel_id", "version", name="uq_audience_profiles_channel_version"),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    profile_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[AudienceProfileSource] = mapped_column(
        Enum(AudienceProfileSource, name="audience_profile_source", native_enum=False),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

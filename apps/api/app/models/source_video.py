from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import SourceVideoType


class SourceVideo(UUIDPrimaryKeyMixin, OrganizationScopedMixin, TimestampMixin, Base):
    """Documento 03, secao 12. Video existente no canal, importado via
    ChannelSyncService - inclui conteudo anterior a conexao com a
    plataforma."""

    __tablename__ = "source_videos"
    __table_args__ = (
        UniqueConstraint(
            "channel_id", "external_video_id", name="uq_source_videos_channel_external_id"
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    external_video_id: Mapped[str] = mapped_column(String(64), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    video_type: Mapped[SourceVideoType] = mapped_column(
        Enum(SourceVideoType, name="source_video_type", native_enum=False),
        default=SourceVideoType.UNKNOWN,
        nullable=False,
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, default=None)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    privacy_status: Mapped[str | None] = mapped_column(String(50), default=None)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), default=None)

    raw_metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

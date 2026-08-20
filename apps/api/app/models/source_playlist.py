from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class SourcePlaylist(UUIDPrimaryKeyMixin, OrganizationScopedMixin, TimestampMixin, Base):
    """Documento 03, secao 13.

    ``created_at``/``updated_at`` nao estao nos "campos" listados no
    documento, mas foram adicionados aqui por consistencia com o resto do
    schema e porque o upsert idempotente do ChannelSyncService precisa
    distinguir criacao de atualizacao (mesma logica de source_videos).
    """

    __tablename__ = "source_playlists"
    __table_args__ = (
        UniqueConstraint(
            "channel_id", "external_playlist_id", name="uq_source_playlists_channel_external_id"
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    external_playlist_id: Mapped[str] = mapped_column(String(64), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    raw_metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChannelConnectionProvider, ChannelConnectionStatus


class ChannelConnection(UUIDPrimaryKeyMixin, OrganizationScopedMixin, TimestampMixin, Base):
    """Documento 03, secao 10. Tokens sempre criptografados
    (``app/security/encryption.py``) - nunca devolvidos pela API
    (Documento 09, secao 20-27)."""

    __tablename__ = "channel_connections"
    __table_args__ = (
        UniqueConstraint(
            "channel_id", "provider", name="uq_channel_connections_channel_provider"
        ),
    )

    channel_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[ChannelConnectionProvider] = mapped_column(
        Enum(ChannelConnectionProvider, name="channel_connection_provider", native_enum=False),
        default=ChannelConnectionProvider.GOOGLE_YOUTUBE,
        nullable=False,
    )
    external_account_id: Mapped[str | None] = mapped_column(String(128), default=None)

    access_token_encrypted: Mapped[str] = mapped_column(String(2000), nullable=False)
    refresh_token_encrypted: Mapped[str] = mapped_column(String(2000), nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    status: Mapped[ChannelConnectionStatus] = mapped_column(
        Enum(ChannelConnectionStatus, name="channel_connection_status", native_enum=False),
        default=ChannelConnectionStatus.CONNECTED,
        nullable=False,
    )

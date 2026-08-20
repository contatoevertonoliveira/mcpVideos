from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import (
    OrganizationScopedMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from app.models.enums import AutomationMode, ChannelPlatform, ChannelStatus


class Channel(UUIDPrimaryKeyMixin, OrganizationScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "channels"
    __table_args__ = (
        # external_channel_id so nulo ate a conexao OAuth real (Fase 04) - o
        # unique constraint do Documento 03 sec. 98 so faz sentido quando
        # ambos os lados existem.
        Index(
            "uq_channels_org_platform_external_id",
            "organization_id",
            "platform",
            "external_channel_id",
            unique=True,
            postgresql_where="external_channel_id IS NOT NULL",
        ),
    )

    platform: Mapped[ChannelPlatform] = mapped_column(
        Enum(ChannelPlatform, name="channel_platform", native_enum=False),
        default=ChannelPlatform.YOUTUBE,
        nullable=False,
    )
    external_channel_id: Mapped[str | None] = mapped_column(String(128), default=None)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    handle: Mapped[str | None] = mapped_column(String(200), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    language: Mapped[str | None] = mapped_column(String(16), default=None)
    country: Mapped[str | None] = mapped_column(String(8), default=None)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), default=None)

    status: Mapped[ChannelStatus] = mapped_column(
        Enum(ChannelStatus, name="channel_status", native_enum=False),
        default=ChannelStatus.PENDING,
        nullable=False,
    )
    automation_mode: Mapped[AutomationMode] = mapped_column(
        Enum(AutomationMode, name="automation_mode", native_enum=False),
        default=AutomationMode.ASSISTED,
        nullable=False,
    )

    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

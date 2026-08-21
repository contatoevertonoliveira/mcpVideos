from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin
from app.models.enums import AgentVersionStatus


class AgentVersion(UUIDPrimaryKeyMixin, Base):
    """Documento 03, secao 43; Documento 02, secao 28. Only one ACTIVE
    version per agent (enforced in AgentRegistryService, not a DB
    constraint - deprecating the old version and activating the new one
    happen in the same transaction, same pattern as ChannelDNAVersion's
    "one active per channel")."""

    __tablename__ = "agent_versions"
    __table_args__ = (
        UniqueConstraint("agent_id", "version", name="uq_agent_versions_agent_version"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    temperature: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    settings_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    input_schema_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    output_schema_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    prompt_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agent_prompts.id", ondelete="SET NULL"), default=None
    )

    status: Mapped[AgentVersionStatus] = mapped_column(
        Enum(AgentVersionStatus, name="agent_version_status", native_enum=False),
        default=AgentVersionStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import AgentRunStatus


class AgentRun(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 45 ("tabela critica"); Documento 10 Fase 11.
    One row per structured-agent invocation - the "record run" and
    "trace operation" acceptance criteria live here."""

    __tablename__ = "agent_runs"

    agent_version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agent_versions.id", ondelete="RESTRICT"), nullable=False
    )

    channel_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="SET NULL"), default=None
    )
    # No FK yet - content_projects/scenes don't exist until later phases
    # (Fase 12+), same "no premature FK" pattern used since Fase 07.
    project_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)
    scene_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)

    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), default=None
    )
    workflow_step_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="SET NULL"), default=None
    )

    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agent_run_status", native_enum=False),
        default=AgentRunStatus.PENDING,
        nullable=False,
    )

    input_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    # Real token/cost accounting arrives with the Model Router (Fase 14) -
    # FakeLLMGateway never reports usage, and AnthropicLLMGateway's real
    # response usage isn't wired through yet. Left NULL rather than
    # fabricated (CLAUDE.md: no misleading placeholders).
    tokens_input: Mapped[int | None] = mapped_column(Integer, default=None)
    tokens_output: Mapped[int | None] = mapped_column(Integer, default=None)
    estimated_cost: Mapped[float | None] = mapped_column(Float, default=None)
    actual_cost: Mapped[float | None] = mapped_column(Float, default=None)

    provider_request_id: Mapped[str | None] = mapped_column(String(200), default=None)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)

    error_code: Mapped[str | None] = mapped_column(String(100), default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)

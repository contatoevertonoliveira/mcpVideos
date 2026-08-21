from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import WorkflowRunStatus


class WorkflowRun(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 48. ``correlation_id`` ties every WorkflowStep,
    WorkflowEvent and AgentRun spawned by this run together for tracing
    (Documento 10 Fase 11 acceptance criterion: "trace operation")."""

    __tablename__ = "workflow_runs"

    workflow_version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    channel_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("channels.id", ondelete="SET NULL"), default=None
    )
    # No FK yet - content_projects doesn't exist until Fase 12.
    project_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)

    status: Mapped[WorkflowRunStatus] = mapped_column(
        Enum(WorkflowRunStatus, name="workflow_run_status", native_enum=False),
        default=WorkflowRunStatus.PENDING,
        nullable=False,
    )
    current_step: Mapped[str | None] = mapped_column(String(100), default=None)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    correlation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), default=uuid.uuid4, nullable=False
    )

    input_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

    error_code: Mapped[str | None] = mapped_column(String(100), default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)

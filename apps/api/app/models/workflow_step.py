from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import WorkflowStepStatus


class WorkflowStep(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 49. ``attempt_count`` backs the "retry"
    acceptance criterion; ``sequence`` is the step's position in its
    WorkflowVersion's ordered step list."""

    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint("workflow_run_id", "step_key", name="uq_workflow_steps_run_key"),
    )

    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )

    step_key: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[WorkflowStepStatus] = mapped_column(
        Enum(WorkflowStepStatus, name="workflow_step_status", native_enum=False),
        default=WorkflowStepStatus.PENDING,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    input_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=None)

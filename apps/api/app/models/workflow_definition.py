from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class WorkflowDefinition(UUIDPrimaryKeyMixin, Base):
    """Documento 03, secao 46; Documento 02, secao 25-26. Global to the
    platform, e.g. "channel.onboarding" - versioned separately via
    WorkflowVersion so an existing WorkflowRun always stays pinned to the
    version it started with (CLAUDE.md: "nunca alterar versao existente
    silenciosamente")."""

    __tablename__ = "workflow_definitions"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

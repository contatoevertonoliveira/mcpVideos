from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class Agent(UUIDPrimaryKeyMixin, Base):
    """Documento 03, secao 42; Documento 02, secao 28 (Agent Registry).
    Agents are global to the platform (no organization_id) - the same
    catalog entry (e.g. "channel_analyst") is shared by every tenant."""

    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

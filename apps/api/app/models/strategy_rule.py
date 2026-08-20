from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin


class StrategyRule(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 21. Diferente de ContentPillar, nao e gerado
    pelo Strategy Agent (o contrato de output do agente, Documento 05
    sec. 8, nao tem um campo de "regras explicitas") - e uma regra de
    negocio que o usuario declara ("nunca publicar dois videos longos no
    mesmo dia"), plana como BrandProfile."""

    __tablename__ = "strategy_rules"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("content_strategies.id", ondelete="CASCADE"),
        nullable=False,
    )

    rule_type: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

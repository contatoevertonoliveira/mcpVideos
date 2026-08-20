from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import ScoreType


class OpportunityScore(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 24. Um componente do calculo do opportunity
    score - nunca guardar so o score final, preservar cada componente
    (channel_fit, audience_fit, etc.) com seu peso e evidencia."""

    __tablename__ = "opportunity_scores"

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("content_opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )

    score_type: Mapped[ScoreType] = mapped_column(
        Enum(ScoreType, name="score_type", native_enum=False), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

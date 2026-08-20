from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FeatureFlagScope


class FeatureFlag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Escopo polimorfico (global/organization/channel) - Documento 03,
    secao 85. scope_id nao tem FK fixa porque aponta para tabelas
    diferentes conforme scope_type."""

    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint("key", "scope_type", "scope_id", name="uq_feature_flags_key_scope"),
    )

    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope_type: Mapped[FeatureFlagScope] = mapped_column(
        Enum(FeatureFlagScope, name="feature_flag_scope", native_enum=False),
        default=FeatureFlagScope.GLOBAL,
        nullable=False,
    )
    scope_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), default=None)

    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

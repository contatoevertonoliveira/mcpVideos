from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import OrganizationScopedMixin, UUIDPrimaryKeyMixin
from app.models.enums import IdeaRelationshipType


class IdeaRelationship(UUIDPrimaryKeyMixin, OrganizationScopedMixin, Base):
    """Documento 03, secao 26. Relaciona duas ideias - o Documento 03 nao
    detalha os campos exatos (so os tipos), modelado seguindo a convencao
    do resto do schema. Usado nesta fase especificamente pela
    deduplicacao do IdeaGenerationService (tipo RELATED, em vez de
    silenciosamente descartar uma sugestao quase-duplicada)."""

    __tablename__ = "idea_relationships"
    __table_args__ = (
        UniqueConstraint(
            "idea_id", "related_idea_id", "relationship_type", name="uq_idea_relationships_pair"
        ),
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("content_ideas.id", ondelete="CASCADE"), nullable=False
    )
    related_idea_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("content_ideas.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[IdeaRelationshipType] = mapped_column(
        Enum(IdeaRelationshipType, name="idea_relationship_type", native_enum=False),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

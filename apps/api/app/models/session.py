from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class UserSession(UUIDPrimaryKeyMixin, Base):
    """Sessao de autenticacao da plataforma (Documento 09, secao 6).

    Nomeada ``UserSession`` (nao ``Session``) para nao colidir com
    ``sqlalchemy.orm.Session``, usado em todo o codebase como o tipo do
    parametro de conexao com o banco.

    Nao usa TenantScopedRepository/OrganizationScopedMixin: uma sessao
    pertence a um usuario, nao a uma organizacao fixa - o usuario pode
    alternar `active_organization_id` entre as organizacoes das quais e
    membro (Documento 08, secao 18 - Organization Selector).
    """

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    active_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), default=None
    )

    user_agent: Mapped[str | None] = mapped_column(String(500), default=None)
    ip_address: Mapped[str | None] = mapped_column(INET, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

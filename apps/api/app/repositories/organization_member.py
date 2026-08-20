from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.organization_member import OrganizationMember
from app.repositories.base import TenantScopedRepository


class OrganizationMemberRepository(TenantScopedRepository[OrganizationMember]):
    model = OrganizationMember

    def get_by_user(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember | None:
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        return self.session.scalars(stmt).first()

    def list_for_user(self, *, user_id: uuid.UUID) -> list[OrganizationMember]:
        """Memberships de um usuario atraves de organizacoes.

        Escopado por ``user_id`` (o proprio usuario autenticado), nao por
        ``organization_id`` - e a consulta legitima de "em quais
        organizacoes eu estou" usada apos login.
        """
        stmt = select(OrganizationMember).where(OrganizationMember.user_id == user_id)
        return list(self.session.scalars(stmt).all())

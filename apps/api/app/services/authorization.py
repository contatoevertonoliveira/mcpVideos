from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError
from app.domain.permissions import Permission, role_has_permission
from app.models.enums import MembershipStatus
from app.models.organization_member import OrganizationMember
from app.repositories.organization_member import OrganizationMemberRepository


class AuthorizationService:
    """Documento 09, secao 11 e 18: camada dedicada de autorizacao.

    Nunca confiar apenas na UI escondendo botoes (secao 18) - toda
    permissao relevante deve ser validada aqui, no backend.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.members = OrganizationMemberRepository(session)

    def get_active_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember:
        member = self.members.get_by_user(organization_id=organization_id, user_id=user_id)
        if member is None or member.status != MembershipStatus.ACTIVE:
            raise AuthorizationError(
                "You are not a member of this organization", code="NOT_A_MEMBER"
            )
        return member

    def require_permission(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, permission: Permission
    ) -> OrganizationMember:
        member = self.get_active_membership(organization_id=organization_id, user_id=user_id)
        if not role_has_permission(member.role, permission):
            raise AuthorizationError(
                "You don't have permission to do this", code="PERMISSION_DENIED"
            )
        return member

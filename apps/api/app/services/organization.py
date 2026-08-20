from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, NotFoundError
from app.models.enums import OrganizationRole
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.utils.slug import slugify, unique_suffix


class OrganizationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.organizations = OrganizationRepository(session)
        self.members = OrganizationMemberRepository(session)

    def create_organization(self, *, name: str, timezone: str = "UTC") -> Organization:
        slug = slugify(name)
        if self.organizations.get_by_slug(slug) is not None:
            slug = f"{slug}-{unique_suffix()}"

        organization = Organization(name=name, slug=slug, timezone=timezone)
        return self.organizations.add(organization)

    def get_organization(self, organization_id: uuid.UUID) -> Organization:
        organization = self.organizations.get_by_id(organization_id)
        if organization is None:
            raise NotFoundError("Organization not found", code="ORGANIZATION_NOT_FOUND")
        return organization

    def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        role: OrganizationRole = OrganizationRole.VIEWER,
    ) -> OrganizationMember:
        self.get_organization(organization_id)  # validates it exists

        existing = self.members.get_by_user(organization_id=organization_id, user_id=user_id)
        if existing is not None:
            raise DomainError(
                "User is already a member of this organization", code="ALREADY_MEMBER"
            )

        member = OrganizationMember(organization_id=organization_id, user_id=user_id, role=role)
        return self.members.add(member)

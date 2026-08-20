import uuid

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.models.enums import OrganizationRole
from app.services.organization import OrganizationService
from app.services.user import UserService


def test_create_organization_generates_slug(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme Studios")

    assert org.slug == "acme-studios"
    assert org.status == "active"
    assert org.timezone == "UTC"


def test_create_organization_deduplicates_slug(db_session):
    service = OrganizationService(db_session)

    first = service.create_organization(name="Acme Studios")
    second = service.create_organization(name="Acme Studios")

    assert first.slug != second.slug
    assert second.slug.startswith("acme-studios-")


def test_get_organization_not_found_raises(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(NotFoundError):
        service.get_organization(uuid.uuid4())


def test_add_member_creates_membership(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="ana@example.com", name="Ana", password="supersecret1"
    )

    member = OrganizationService(db_session).add_member(
        organization_id=org.id, user_id=user.id, role=OrganizationRole.OWNER
    )

    assert member.organization_id == org.id
    assert member.user_id == user.id
    assert member.role == "owner"


def test_add_member_twice_raises_domain_error(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="ana2@example.com", name="Ana", password="supersecret1"
    )
    service = OrganizationService(db_session)
    service.add_member(organization_id=org.id, user_id=user.id)

    with pytest.raises(DomainError):
        service.add_member(organization_id=org.id, user_id=user.id)

"""Documento 10, Fase 02 - criterio de aceite obrigatorio:
"Teste deve provar que Org A nao acessa recurso da Org B."
"""

import pytest

from app.core.exceptions import NotFoundError
from app.repositories.channel import ChannelRepository
from app.repositories.job import JobRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.services.channel import ChannelService
from app.services.job import JobService
from app.services.organization import OrganizationService
from app.services.user import UserService


@pytest.fixture
def two_organizations(db_session):
    org_a = OrganizationService(db_session).create_organization(name="Org A")
    org_b = OrganizationService(db_session).create_organization(name="Org B")
    return org_a, org_b


def test_channel_repository_scopes_by_organization(db_session, two_organizations):
    org_a, org_b = two_organizations
    channel_a = ChannelService(db_session).create_placeholder_channel(
        organization_id=org_a.id, name="Canal da Org A"
    )

    channel_repo = ChannelRepository(db_session)
    assert channel_repo.get_by_id(channel_a.id, organization_id=org_a.id) is not None
    assert channel_repo.get_by_id(channel_a.id, organization_id=org_b.id) is None


def test_channel_service_raises_not_found_across_orgs(db_session, two_organizations):
    org_a, org_b = two_organizations
    service = ChannelService(db_session)
    channel_a = service.create_placeholder_channel(organization_id=org_a.id, name="Canal A")

    with pytest.raises(NotFoundError):
        service.get_channel(channel_a.id, organization_id=org_b.id)


def test_job_repository_scopes_by_organization(db_session, two_organizations):
    org_a, org_b = two_organizations
    job_a = JobService(db_session).create_job(organization_id=org_a.id, job_type="channel_import")

    assert JobRepository(db_session).get_by_id(job_a.id, organization_id=org_a.id) is not None
    assert JobRepository(db_session).get_by_id(job_a.id, organization_id=org_b.id) is None


def test_channel_list_never_leaks_across_organizations(db_session, two_organizations):
    org_a, org_b = two_organizations
    channel_service = ChannelService(db_session)
    channel_service.create_placeholder_channel(organization_id=org_a.id, name="A1")
    channel_service.create_placeholder_channel(organization_id=org_a.id, name="A2")
    channel_service.create_placeholder_channel(organization_id=org_b.id, name="B1")

    channels_a = ChannelRepository(db_session).list(organization_id=org_a.id)
    channels_b = ChannelRepository(db_session).list(organization_id=org_b.id)

    assert {c.name for c in channels_a} == {"A1", "A2"}
    assert {c.name for c in channels_b} == {"B1"}


def test_organization_membership_does_not_leak_across_organizations(db_session, two_organizations):
    org_a, org_b = two_organizations
    user = UserService(db_session).create_user(
        email="user@example.com", name="User", password="supersecret1"
    )
    org_service = OrganizationService(db_session)
    org_service.add_member(organization_id=org_a.id, user_id=user.id)

    members_repo = OrganizationMemberRepository(db_session)
    assert members_repo.get_by_user(organization_id=org_a.id, user_id=user.id) is not None
    assert members_repo.get_by_user(organization_id=org_b.id, user_id=user.id) is None

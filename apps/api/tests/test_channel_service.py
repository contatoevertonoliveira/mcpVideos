import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.services.channel import ChannelService
from app.services.organization import OrganizationService


def test_create_placeholder_channel_defaults(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")

    channel = ChannelService(db_session).create_placeholder_channel(
        organization_id=org.id, name="Meu Canal"
    )

    assert channel.organization_id == org.id
    assert channel.platform == "youtube"
    assert channel.external_channel_id is None
    assert channel.status == "pending"
    # Documento 03 sec. 9: nunca iniciar com automacao irrestrita.
    assert channel.automation_mode == "assisted"


def test_get_channel_not_found_for_wrong_org(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    other_org = OrganizationService(db_session).create_organization(name="Other")
    service = ChannelService(db_session)
    channel = service.create_placeholder_channel(organization_id=org.id, name="Meu Canal")

    with pytest.raises(NotFoundError):
        service.get_channel(channel.id, organization_id=other_org.id)


def test_get_channel_unknown_id_not_found(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")

    with pytest.raises(NotFoundError):
        ChannelService(db_session).get_channel(uuid.uuid4(), organization_id=org.id)

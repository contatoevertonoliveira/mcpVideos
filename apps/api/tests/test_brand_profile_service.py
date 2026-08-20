import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.brand_profile import BrandProfileWrite
from app.services.brand_profile import BrandProfileService
from app.services.channel import ChannelService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _org_channel(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    channel = ChannelService(db_session).create_placeholder_channel(
        organization_id=org.id, name="My Channel"
    )
    return org, channel


def test_get_returns_none_before_upsert(db_session):
    org, channel = _org_channel(db_session)

    assert BrandProfileService(db_session).get(channel.id, organization_id=org.id) is None


def test_upsert_creates_then_updates_in_place(db_session):
    org, channel = _org_channel(db_session)
    service = BrandProfileService(db_session)

    first = service.upsert(
        channel.id,
        organization_id=org.id,
        payload=BrandProfileWrite(name="Acme Brand", colors_json={"primary": "#000"}),
    )
    second = service.upsert(
        channel.id,
        organization_id=org.id,
        payload=BrandProfileWrite(name="Acme Brand v2", colors_json={"primary": "#111"}),
    )

    assert first.id == second.id
    assert second.name == "Acme Brand v2"
    assert second.colors_json == {"primary": "#111"}


def test_upsert_unknown_channel_raises(db_session):
    org, _channel = _org_channel(db_session)

    with pytest.raises(NotFoundError):
        BrandProfileService(db_session).upsert(
            uuid.uuid4(), organization_id=org.id, payload=BrandProfileWrite()
        )

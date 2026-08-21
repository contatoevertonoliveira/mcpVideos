import uuid
from datetime import time

import pytest

from app.core.exceptions import NotFoundError
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import DayOfWeek, SourceVideoType
from app.services.channel_connection import ChannelConnectionService
from app.services.organization import OrganizationService
from app.services.publishing_slot import PublishingSlotService
from app.services.user import UserService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


async def _channel(db_session, org, user):
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    return await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )


@pytest.mark.anyio
async def test_add_and_list_slots(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel(db_session, org, user)
    service = PublishingSlotService(db_session)

    service.add(
        channel_id=channel.id,
        organization_id=org.id,
        day_of_week=DayOfWeek.MONDAY,
        local_time=time(10, 0),
        content_type=SourceVideoType.SHORT,
    )
    service.add(
        channel_id=channel.id,
        organization_id=org.id,
        day_of_week=DayOfWeek.THURSDAY,
        local_time=time(18, 0),
        content_type=SourceVideoType.LONG_FORM,
        priority=2,
    )

    slots = service.list(channel_id=channel.id, organization_id=org.id)

    assert len(slots) == 2
    assert {slot.day_of_week for slot in slots} == {DayOfWeek.MONDAY, DayOfWeek.THURSDAY}
    assert all(slot.active for slot in slots)


@pytest.mark.anyio
async def test_add_slot_to_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        PublishingSlotService(db_session).add(
            channel_id=uuid.uuid4(),
            organization_id=org.id,
            day_of_week=DayOfWeek.MONDAY,
            local_time=time(10, 0),
            content_type=SourceVideoType.SHORT,
        )

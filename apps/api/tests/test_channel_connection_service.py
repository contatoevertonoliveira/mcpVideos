import uuid

import pytest

from app.core.exceptions import AuthorizationError, DomainError
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import ChannelConnectionStatus
from app.repositories.channel_sync_run import ChannelSyncRunRepository
from app.services.channel_connection import ChannelConnectionService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


def _service(db_session) -> ChannelConnectionService:
    return ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())


def test_start_connection_returns_authorization_url(db_session):
    org, user = _org_and_user(db_session)

    url = _service(db_session).start_connection(organization_id=org.id, user_id=user.id)

    assert url.startswith("http://localhost:3000/oauth/youtube/callback?code=")
    assert "&state=" in url


def test_start_connection_denies_non_member(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="outsider@example.com", name="Outsider", password="supersecret1"
    )

    with pytest.raises(AuthorizationError):
        _service(db_session).start_connection(organization_id=org.id, user_id=user.id)


@pytest.mark.anyio
async def test_complete_connection_creates_channel_and_connection(db_session):
    org, user = _org_and_user(db_session)
    service = _service(db_session)
    url = service.start_connection(organization_id=org.id, user_id=user.id)
    state = url.split("state=")[1]

    channel = await service.complete_connection(
        code="fake-code-123", state=state, authenticated_user_id=user.id
    )

    assert channel.organization_id == org.id
    assert channel.name == "Canal de Teste (Fake Gateway)"
    assert channel.status == "active"
    assert channel.automation_mode == "assisted"

    connection = service.connections.get_by_channel(channel.id, organization_id=org.id)
    assert connection is not None
    assert connection.status == ChannelConnectionStatus.CONNECTED
    # Tokens are encrypted at rest and never equal the fake plaintext values.
    assert "fake-access" not in connection.access_token_encrypted
    assert "fake-refresh" not in connection.refresh_token_encrypted

    sync_runs = ChannelSyncRunRepository(db_session).list(organization_id=org.id)
    assert len(sync_runs) == 1
    assert sync_runs[0].sync_type == "initial"
    assert sync_runs[0].items_created == 1


@pytest.mark.anyio
async def test_complete_connection_rejects_state_for_different_user(db_session):
    org, user = _org_and_user(db_session)
    other_user = UserService(db_session).create_user(
        email="other@example.com", name="Other", password="supersecret1"
    )
    service = _service(db_session)
    url = service.start_connection(organization_id=org.id, user_id=user.id)
    state = url.split("state=")[1]

    with pytest.raises(AuthorizationError):
        await service.complete_connection(
            code="fake-code", state=state, authenticated_user_id=other_user.id
        )


@pytest.mark.anyio
async def test_complete_connection_rejects_invalid_state(db_session):
    org, user = _org_and_user(db_session)

    with pytest.raises(DomainError):
        await _service(db_session).complete_connection(
            code="fake-code", state="garbage", authenticated_user_id=user.id
        )


@pytest.mark.anyio
async def test_reconnecting_same_channel_updates_instead_of_duplicating(db_session):
    org, user = _org_and_user(db_session)
    service = _service(db_session)

    url1 = service.start_connection(organization_id=org.id, user_id=user.id)
    channel1 = await service.complete_connection(
        code="same-code", state=url1.split("state=")[1], authenticated_user_id=user.id
    )

    url2 = service.start_connection(organization_id=org.id, user_id=user.id)
    channel2 = await service.complete_connection(
        code="same-code", state=url2.split("state=")[1], authenticated_user_id=user.id
    )

    assert channel1.id == channel2.id
    sync_runs = ChannelSyncRunRepository(db_session).list(organization_id=org.id)
    assert len(sync_runs) == 2
    assert sync_runs[1].items_created == 0
    assert sync_runs[1].items_updated == 1


@pytest.mark.anyio
async def test_disconnect_marks_channel_and_connection(db_session):
    org, user = _org_and_user(db_session)
    service = _service(db_session)
    url = service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    disconnected = await service.disconnect(channel_id=channel.id, organization_id=org.id)

    assert disconnected.status == "disabled"
    connection = service.connections.get_by_channel(channel.id, organization_id=org.id)
    assert connection.status == ChannelConnectionStatus.DISCONNECTED


@pytest.mark.anyio
async def test_disconnect_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    from app.core.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await _service(db_session).disconnect(channel_id=uuid.uuid4(), organization_id=org.id)

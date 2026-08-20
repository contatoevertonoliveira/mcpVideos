import uuid

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import IdeaStatus, SyncType
from app.services.channel import ChannelService
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_strategy import ChannelStrategyService
from app.services.channel_sync import ChannelSyncService
from app.services.content_idea import ContentIdeaService
from app.services.idea_generation import IdeaGenerationService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


async def _channel_with_ideas(db_session, org, user):
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )
    await ChannelSyncService(db_session, gateway=FakeYouTubeGateway()).run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )
    await ChannelDNAService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )
    strategy_service = ChannelStrategyService(db_session, llm_gateway=FakeLLMGateway())
    strategy = await strategy_service.generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )
    strategy_service.approve(
        channel_id=channel.id, strategy_id=strategy.id, organization_id=org.id, user_id=user.id
    )
    ideas = await IdeaGenerationService(db_session, llm_gateway=FakeLLMGateway()).generate_ideas(
        channel_id=channel.id, organization_id=org.id
    )
    return channel, ideas


@pytest.mark.anyio
async def test_approve_draft_idea(db_session):
    org, user = _org_and_user(db_session)
    channel, ideas = await _channel_with_ideas(db_session, org, user)
    idea = ideas[0]

    approved = ContentIdeaService(db_session).approve(
        channel_id=channel.id, idea_id=idea.id, organization_id=org.id, user_id=user.id
    )

    assert approved.status == IdeaStatus.APPROVED


@pytest.mark.anyio
async def test_approve_already_approved_idea_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, ideas = await _channel_with_ideas(db_session, org, user)
    idea = ideas[0]
    service = ContentIdeaService(db_session)
    service.approve(channel_id=channel.id, idea_id=idea.id, organization_id=org.id, user_id=user.id)

    with pytest.raises(DomainError):
        service.approve(
            channel_id=channel.id, idea_id=idea.id, organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_approve_unknown_idea_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, _ideas = await _channel_with_ideas(db_session, org, user)

    with pytest.raises(NotFoundError):
        ContentIdeaService(db_session).approve(
            channel_id=channel.id, idea_id=uuid.uuid4(), organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_approve_idea_from_different_channel_raises(db_session):
    org, user = _org_and_user(db_session)
    _channel_a, ideas_a = await _channel_with_ideas(db_session, org, user)
    # A second, unrelated channel in the same org - FakeYouTubeGateway
    # always resolves to the same fake account, so a real OAuth connect
    # can't produce two distinct channels; a placeholder is enough here
    # since the test only needs a genuinely different channel_id.
    channel_b = ChannelService(db_session).create_placeholder_channel(
        organization_id=org.id, name="Other Channel"
    )

    with pytest.raises(NotFoundError):
        ContentIdeaService(db_session).approve(
            channel_id=channel_b.id, idea_id=ideas_a[0].id, organization_id=org.id, user_id=user.id
        )

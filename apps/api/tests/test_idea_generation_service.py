import uuid

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import IdeaRelationshipType, IdeaStatus, SyncType
from app.repositories.idea_relationship import IdeaRelationshipRepository
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_strategy import ChannelStrategyService
from app.services.channel_sync import ChannelSyncService
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


async def _channel_with_active_strategy(db_session, org, user):
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
    return channel


def _idea_service(db_session) -> IdeaGenerationService:
    return IdeaGenerationService(db_session, llm_gateway=FakeLLMGateway())


@pytest.mark.anyio
async def test_generate_ideas_creates_drafts_and_archives_none_first_time(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_strategy(db_session, org, user)

    created = await _idea_service(db_session).generate_ideas(
        channel_id=channel.id, organization_id=org.id
    )

    assert len(created) == 3
    assert all(idea.status == IdeaStatus.DRAFT for idea in created)


@pytest.mark.anyio
async def test_generate_ideas_twice_deduplicates_and_links_relationship(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_strategy(db_session, org, user)
    service = _idea_service(db_session)

    first_batch = await service.generate_ideas(channel_id=channel.id, organization_id=org.id)
    second_batch = await service.generate_ideas(channel_id=channel.id, organization_id=org.id)

    # The fake gateway proposes the same 3 ideas every time - the second
    # run should treat all of them as near-duplicates of the first batch.
    assert len(first_batch) == 3
    assert len(second_batch) == 0

    all_ideas = service.ideas.list_by_channel(channel_id=channel.id, organization_id=org.id)
    assert len(all_ideas) == 6
    archived = [idea for idea in all_ideas if idea.status == IdeaStatus.ARCHIVED]
    assert len(archived) == 3

    relationships = IdeaRelationshipRepository(db_session).list(organization_id=org.id, limit=50)
    assert len(relationships) == 3
    assert all(r.relationship_type == IdeaRelationshipType.RELATED for r in relationships)


@pytest.mark.anyio
async def test_generate_ideas_without_dna_raises(db_session):
    org, user = _org_and_user(db_session)
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    with pytest.raises(DomainError):
        await _idea_service(db_session).generate_ideas(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_ideas_without_active_strategy_raises(db_session):
    org, user = _org_and_user(db_session)
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

    with pytest.raises(DomainError):
        await _idea_service(db_session).generate_ideas(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_ideas_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _idea_service(db_session).generate_ideas(
            channel_id=uuid.uuid4(), organization_id=org.id
        )

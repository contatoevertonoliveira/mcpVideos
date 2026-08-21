import uuid

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import AgentRunStatus, ChannelDNAStatus, SyncType
from app.repositories.agent_run import AgentRunRepository
from app.schemas.brand_profile import BrandProfileWrite
from app.services.brand_profile import BrandProfileService
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_sync import ChannelSyncService
from app.services.organization import OrganizationService
from app.services.user import UserService
from app.services.workflow_engine import WorkflowEngineService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


async def _connect_and_sync_channel(db_session, org, user):
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )
    sync_service = ChannelSyncService(db_session, gateway=FakeYouTubeGateway())
    await sync_service.run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )
    return channel


def _dna_service(db_session) -> ChannelDNAService:
    return ChannelDNAService(db_session, llm_gateway=FakeLLMGateway())


@pytest.mark.anyio
async def test_generate_new_version_creates_active_dna(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)

    dna = await _dna_service(db_session).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )

    assert dna.version == 1
    assert dna.status == ChannelDNAStatus.ACTIVE
    assert dna.activated_at is not None
    assert dna.classification_json["primary_language"] == "pt-BR"
    assert dna.content_patterns_json["content_patterns"]
    assert dna.recommendations_json == {}
    assert 0.0 <= dna.confidence <= 1.0


@pytest.mark.anyio
async def test_generate_new_version_threads_workflow_run_id_into_agent_runs(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    engine = WorkflowEngineService(db_session)
    version = engine.ensure_definition(
        slug="test.dna", name="Test DNA", description="desc", steps=["only"]
    )
    workflow_run = engine.start_run(
        workflow_version=version, organization_id=org.id, channel_id=channel.id
    )

    await _dna_service(db_session).generate_new_version(
        channel_id=channel.id, organization_id=org.id, workflow_run_id=workflow_run.id
    )

    runs = AgentRunRepository(db_session).list(organization_id=org.id)
    channel_and_audience_runs = [run for run in runs if run.channel_id == channel.id]
    assert len(channel_and_audience_runs) == 2
    assert all(run.workflow_run_id == workflow_run.id for run in channel_and_audience_runs)
    assert all(run.status == AgentRunStatus.COMPLETED for run in channel_and_audience_runs)


@pytest.mark.anyio
async def test_generate_new_version_twice_supersedes_previous(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    service = _dna_service(db_session)

    first = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)
    second = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)

    db_session.refresh(first)
    assert first.status == ChannelDNAStatus.SUPERSEDED
    assert second.status == ChannelDNAStatus.ACTIVE
    assert second.version == 2

    active = service.dna_versions.get_active(channel.id, organization_id=org.id)
    assert active.id == second.id

    history = service.dna_versions.list_by_channel(channel_id=channel.id, organization_id=org.id)
    assert len(history) == 2


@pytest.mark.anyio
async def test_generate_new_version_without_videos_raises(db_session):
    org, user = _org_and_user(db_session)
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    with pytest.raises(DomainError):
        await _dna_service(db_session).generate_new_version(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_new_version_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _dna_service(db_session).generate_new_version(
            channel_id=uuid.uuid4(), organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_new_version_uses_brand_profile(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    BrandProfileService(db_session).upsert(
        channel.id,
        organization_id=org.id,
        payload=BrandProfileWrite(
            rules_json={"tone": "casual"}, prohibited_elements_json={"words": ["spam"]}
        ),
    )

    dna = await _dna_service(db_session).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )

    assert dna.brand_rules_json == {"tone": "casual"}
    assert dna.restrictions_json == {"prohibited_elements": {"words": ["spam"]}}

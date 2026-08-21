import uuid

import pytest

from app.agents.schemas import ChannelAnalystOutput
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway, LLMGenerationError
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import AgentRunStatus, AudienceProfileSource, SyncType
from app.repositories.agent_run import AgentRunRepository
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_intelligence import ChannelIntelligenceService
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


def _intelligence_service(db_session) -> ChannelIntelligenceService:
    return ChannelIntelligenceService(db_session, llm_gateway=FakeLLMGateway())


@pytest.mark.anyio
async def test_analyze_channel_creates_profiles(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)

    result = await _intelligence_service(db_session).analyze_channel(
        channel_id=channel.id, organization_id=org.id
    )

    assert result.channel_profile.channel_id == channel.id
    assert result.channel_profile.primary_language == "pt-BR"
    assert result.channel_profile.confidence == pytest.approx(0.62)
    assert result.channel_profile.content_summary

    assert result.audience_profile.channel_id == channel.id
    assert result.audience_profile.version == 1
    assert result.audience_profile.source == AudienceProfileSource.INFERRED
    assert result.audience_profile.profile_json["language"] == "pt-BR"
    assert "confidence" not in result.audience_profile.profile_json


@pytest.mark.anyio
async def test_analyze_channel_threads_workflow_run_id_into_agent_runs(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    engine = WorkflowEngineService(db_session)
    version = engine.ensure_definition(
        slug="test.intelligence", name="Test Intelligence", description="desc", steps=["only"]
    )
    workflow_run = engine.start_run(
        workflow_version=version, organization_id=org.id, channel_id=channel.id
    )

    await _intelligence_service(db_session).analyze_channel(
        channel_id=channel.id, organization_id=org.id, workflow_run_id=workflow_run.id
    )

    runs = AgentRunRepository(db_session).list(organization_id=org.id)
    channel_and_audience_runs = [run for run in runs if run.channel_id == channel.id]
    assert len(channel_and_audience_runs) == 2
    assert all(run.workflow_run_id == workflow_run.id for run in channel_and_audience_runs)
    assert all(run.status == AgentRunStatus.COMPLETED for run in channel_and_audience_runs)


@pytest.mark.anyio
async def test_analyze_channel_twice_updates_profile_and_versions_audience(db_session):
    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    service = _intelligence_service(db_session)

    await service.analyze_channel(channel_id=channel.id, organization_id=org.id)
    second = await service.analyze_channel(channel_id=channel.id, organization_id=org.id)

    channel_profiles = service.channel_profiles.list(organization_id=org.id)
    audience_profiles = service.audience_profiles.list(organization_id=org.id, limit=10)
    assert len(channel_profiles) == 1  # upserted in place, not duplicated
    assert len(audience_profiles) == 2  # versioned, both kept
    assert second.audience_profile.version == 2


@pytest.mark.anyio
async def test_analyze_channel_without_videos_raises(db_session):
    org, user = _org_and_user(db_session)
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    with pytest.raises(DomainError):
        await _intelligence_service(db_session).analyze_channel(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_analyze_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _intelligence_service(db_session).analyze_channel(
            channel_id=uuid.uuid4(), organization_id=org.id
        )


@pytest.mark.anyio
async def test_analyze_channel_dispatches_dna_generation_only_when_no_dna_exists_yet(db_session):
    """Dispatch is gated on "no DNA version exists for this channel yet",
    not on which sync triggered the analysis - simulate the (mocked)
    first dispatch actually completing (as the real Celery task would)
    before re-analyzing, since re-dispatching purely because analysis ran
    again would spam LLM calls on every re-sync."""
    from app.services.channel_dna import ChannelDNAService
    from app.tasks import channel_dna as channel_dna_tasks

    org, user = _org_and_user(db_session)
    channel = await _connect_and_sync_channel(db_session, org, user)
    service = _intelligence_service(db_session)

    await service.analyze_channel(channel_id=channel.id, organization_id=org.id)
    assert channel_dna_tasks.run_channel_dna_task.delay.call_count == 1

    await ChannelDNAService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )

    await service.analyze_channel(channel_id=channel.id, organization_id=org.id)
    assert channel_dna_tasks.run_channel_dna_task.delay.call_count == 1


@pytest.mark.anyio
async def test_fake_llm_gateway_raises_for_unknown_prompt():
    with pytest.raises(LLMGenerationError):
        await FakeLLMGateway().generate_structured(
            prompt_id="unknown_agent.v1",
            system_prompt="",
            user_prompt="",
            response_model=ChannelAnalystOutput,
        )

import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import IdeaStatus, OpportunityStatus, SyncType
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_strategy import ChannelStrategyService
from app.services.channel_sync import ChannelSyncService
from app.services.idea_generation import IdeaGenerationService
from app.services.opportunity_evaluation import OpportunityEvaluationService
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


def _evaluation_service(db_session) -> OpportunityEvaluationService:
    return OpportunityEvaluationService(db_session, llm_gateway=FakeLLMGateway())


@pytest.mark.anyio
async def test_evaluate_idea_persists_all_nine_score_components(db_session):
    org, user = _org_and_user(db_session)
    channel, ideas = await _channel_with_ideas(db_session, org, user)
    good_idea = next(i for i in ideas if "smartphone" in i.title)

    opportunity = await _evaluation_service(db_session).evaluate_idea(
        idea_id=good_idea.id, organization_id=org.id
    )

    scores = _evaluation_service(db_session).scores.list_by_opportunity(
        opportunity.id, organization_id=org.id
    )
    assert len(scores) == 9
    assert opportunity.status == OpportunityStatus.RECOMMENDED

    db_session.refresh(good_idea)
    assert good_idea.status == IdeaStatus.RECOMMENDED


@pytest.mark.anyio
async def test_evaluate_trend_chasing_idea_is_rejected(db_session):
    """The Documento 10 F09 acceptance criterion, exercised through the
    full service (agent -> code scoring -> persistence), not just the
    pure scoring unit."""
    org, user = _org_and_user(db_session)
    channel, ideas = await _channel_with_ideas(db_session, org, user)
    trend_idea = next(i for i in ideas if "Dança viral" in i.title)

    opportunity = await _evaluation_service(db_session).evaluate_idea(
        idea_id=trend_idea.id, organization_id=org.id
    )

    assert opportunity.status == OpportunityStatus.REJECTED
    db_session.refresh(trend_idea)
    assert trend_idea.status == IdeaStatus.REJECTED


@pytest.mark.anyio
async def test_evaluate_unknown_idea_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _evaluation_service(db_session).evaluate_idea(
            idea_id=uuid.uuid4(), organization_id=org.id
        )

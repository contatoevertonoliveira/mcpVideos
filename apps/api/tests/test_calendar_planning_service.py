import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.calendar_item import CalendarItem
from app.models.enums import (
    CalendarItemSource,
    CalendarItemStatus,
    IdeaStatus,
    SourceVideoType,
    SyncType,
)
from app.repositories.calendar_item import CalendarItemRepository
from app.services.calendar_item import CalendarItemService
from app.services.calendar_planning import CalendarPlanningService
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_strategy import ChannelStrategyService
from app.services.channel_sync import ChannelSyncService
from app.services.content_idea import ContentIdeaService
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


async def _channel_with_approved_ideas(db_session, org, user):
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
    evaluation_service = OpportunityEvaluationService(db_session, llm_gateway=FakeLLMGateway())
    for idea in ideas:
        await evaluation_service.evaluate_idea(idea_id=idea.id, organization_id=org.id)

    idea_service = ContentIdeaService(db_session)
    approved = [
        idea_service.approve(
            channel_id=channel.id, idea_id=idea.id, organization_id=org.id, user_id=user.id
        )
        for idea in ideas
        if idea.status == IdeaStatus.RECOMMENDED
    ]
    return channel, approved


@pytest.mark.anyio
async def test_generate_recommendations_creates_suggested_items(db_session):
    org, user = _org_and_user(db_session)
    channel, approved_ideas = await _channel_with_approved_ideas(db_session, org, user)
    assert approved_ideas, "fixture expects at least one RECOMMENDED idea to approve"

    recommendation = await CalendarPlanningService(
        db_session, llm_gateway=FakeLLMGateway()
    ).generate_recommendations(channel_id=channel.id, organization_id=org.id)

    items = CalendarItemService(db_session).list_calendar(
        channel_id=channel.id, organization_id=org.id
    )
    assert len(items) == len(approved_ideas)
    for item in items:
        assert item.status == CalendarItemStatus.SUGGESTED
        assert item.source == CalendarItemSource.AI
        assert item.calendar_recommendation_id == recommendation.id
        assert item.idea_id in {idea.id for idea in approved_ideas}
        assert item.planned_at > datetime.now(UTC)

    assert "format_balance" in recommendation.balance_report_json
    assert "pillar_balance" in recommendation.balance_report_json


@pytest.mark.anyio
async def test_generate_recommendations_skips_ideas_already_on_calendar(db_session):
    org, user = _org_and_user(db_session)
    channel, approved_ideas = await _channel_with_approved_ideas(db_session, org, user)
    planning_service = CalendarPlanningService(db_session, llm_gateway=FakeLLMGateway())
    await planning_service.generate_recommendations(channel_id=channel.id, organization_id=org.id)

    with pytest.raises(DomainError):
        await planning_service.generate_recommendations(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_recommendations_without_approved_ideas_raises(db_session):
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
    strategy_service = ChannelStrategyService(db_session, llm_gateway=FakeLLMGateway())
    strategy = await strategy_service.generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )
    strategy_service.approve(
        channel_id=channel.id, strategy_id=strategy.id, organization_id=org.id, user_id=user.id
    )

    with pytest.raises(DomainError):
        await CalendarPlanningService(
            db_session, llm_gateway=FakeLLMGateway()
        ).generate_recommendations(channel_id=channel.id, organization_id=org.id)


@pytest.mark.anyio
async def test_generate_recommendations_without_strategy_raises(db_session):
    org, user = _org_and_user(db_session)
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    with pytest.raises(DomainError):
        await CalendarPlanningService(
            db_session, llm_gateway=FakeLLMGateway()
        ).generate_recommendations(channel_id=channel.id, organization_id=org.id)


@pytest.mark.anyio
async def test_generate_recommendations_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await CalendarPlanningService(
            db_session, llm_gateway=FakeLLMGateway()
        ).generate_recommendations(channel_id=uuid.uuid4(), organization_id=org.id)


@pytest.mark.anyio
async def test_generate_recommendations_detects_conflict_with_existing_item(db_session):
    org, user = _org_and_user(db_session)
    channel, approved_ideas = await _channel_with_approved_ideas(db_session, org, user)

    # FakeLLMGateway's calendar_planner.v1 assigns the first candidate to
    # "tomorrow at 15:00 UTC" (see app/gateways/llm.py) - plant a
    # pre-existing item on that exact day to force a real conflict,
    # instead of asserting only the empty-calendar case.
    same_day_as_first_suggestion = (
        datetime.now(UTC).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    )
    CalendarItemRepository(db_session).add(
        CalendarItem(
            organization_id=org.id,
            channel_id=channel.id,
            content_type=SourceVideoType.LONG_FORM,
            planned_at=same_day_as_first_suggestion,
            status=CalendarItemStatus.APPROVED,
            source=CalendarItemSource.USER,
        )
    )

    recommendation = await CalendarPlanningService(
        db_session, llm_gateway=FakeLLMGateway()
    ).generate_recommendations(channel_id=channel.id, organization_id=org.id)

    assert len(recommendation.conflicts_json) >= 1
    assert same_day_as_first_suggestion.date().isoformat() in recommendation.conflicts_json[0]

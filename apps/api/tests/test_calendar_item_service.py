import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import CalendarItemStatus, IdeaStatus, SyncType
from app.services.calendar_item import CalendarItemService
from app.services.calendar_planning import CalendarPlanningService
from app.services.channel import ChannelService
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


async def _channel_with_suggested_calendar(db_session, org, user):
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
    for idea in ideas:
        if idea.status == IdeaStatus.RECOMMENDED:
            idea_service.approve(
                channel_id=channel.id, idea_id=idea.id, organization_id=org.id, user_id=user.id
            )
    await CalendarPlanningService(
        db_session, llm_gateway=FakeLLMGateway()
    ).generate_recommendations(channel_id=channel.id, organization_id=org.id)
    items = CalendarItemService(db_session).list_calendar(
        channel_id=channel.id, organization_id=org.id
    )
    return channel, items


@pytest.mark.anyio
async def test_approve_suggested_item(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]

    approved = CalendarItemService(db_session).approve(
        channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id
    )

    assert approved.status == CalendarItemStatus.APPROVED


@pytest.mark.anyio
async def test_approve_already_approved_item_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]
    service = CalendarItemService(db_session)
    service.approve(channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id)

    with pytest.raises(DomainError):
        service.approve(
            channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_reject_suggested_item(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]

    rejected = CalendarItemService(db_session).reject(
        channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id
    )

    assert rejected.status == CalendarItemStatus.CANCELLED


@pytest.mark.anyio
async def test_reject_already_cancelled_item_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]
    service = CalendarItemService(db_session)
    service.reject(channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id)

    with pytest.raises(DomainError):
        service.reject(
            channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_reschedule_item_moves_planned_at(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]
    new_planned_at = datetime.now(UTC).replace(microsecond=0) + timedelta(days=14)

    moved = CalendarItemService(db_session).reschedule(
        channel_id=channel.id,
        item_id=item.id,
        organization_id=org.id,
        user_id=user.id,
        planned_at=new_planned_at,
    )

    assert moved.planned_at == new_planned_at


@pytest.mark.anyio
async def test_reschedule_cancelled_item_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    item = items[0]
    service = CalendarItemService(db_session)
    service.reject(channel_id=channel.id, item_id=item.id, organization_id=org.id, user_id=user.id)

    with pytest.raises(DomainError):
        service.reschedule(
            channel_id=channel.id,
            item_id=item.id,
            organization_id=org.id,
            user_id=user.id,
            planned_at=datetime.now(UTC) + timedelta(days=1),
        )


@pytest.mark.anyio
async def test_approve_unknown_item_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, _items = await _channel_with_suggested_calendar(db_session, org, user)

    with pytest.raises(NotFoundError):
        CalendarItemService(db_session).approve(
            channel_id=channel.id, item_id=uuid.uuid4(), organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_approve_item_from_different_channel_raises(db_session):
    org, user = _org_and_user(db_session)
    channel, items = await _channel_with_suggested_calendar(db_session, org, user)
    other_channel = ChannelService(db_session).create_placeholder_channel(
        organization_id=org.id, name="Other Channel"
    )

    with pytest.raises(NotFoundError):
        CalendarItemService(db_session).approve(
            channel_id=other_channel.id,
            item_id=items[0].id,
            organization_id=org.id,
            user_id=user.id,
        )

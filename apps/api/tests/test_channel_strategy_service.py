import uuid

import pytest

from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import FakeLLMGateway
from app.gateways.youtube import FakeYouTubeGateway
from app.models.enums import ContentStrategyStatus, SyncType
from app.services.channel_connection import ChannelConnectionService
from app.services.channel_dna import ChannelDNAService
from app.services.channel_strategy import ChannelStrategyService
from app.services.channel_sync import ChannelSyncService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _org_and_user(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="owner@example.com", name="Owner", password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id)
    return org, user


async def _channel_with_active_dna(db_session, org, user):
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )
    sync_service = ChannelSyncService(db_session, gateway=FakeYouTubeGateway())
    await sync_service.run_sync(
        channel_id=channel.id, organization_id=org.id, sync_type=SyncType.INITIAL
    )
    await ChannelDNAService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )
    return channel


def _strategy_service(db_session) -> ChannelStrategyService:
    return ChannelStrategyService(db_session, llm_gateway=FakeLLMGateway())


@pytest.mark.anyio
async def test_generate_new_version_creates_draft_strategy_with_pillars(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)

    strategy = await _strategy_service(db_session).generate_new_version(
        channel_id=channel.id, organization_id=org.id
    )

    assert strategy.version == 1
    assert strategy.status == ContentStrategyStatus.DRAFT
    assert strategy.activated_at is None
    assert strategy.shorts_ratio == pytest.approx(0.35)
    assert strategy.long_form_ratio == pytest.approx(0.55)
    assert strategy.objective

    pillars = _strategy_service(db_session).pillars.list_by_strategy(
        strategy.id, organization_id=org.id
    )
    assert len(pillars) == 3
    assert all(pillar.active for pillar in pillars)


@pytest.mark.anyio
async def test_generate_new_version_without_dna_raises(db_session):
    org, user = _org_and_user(db_session)
    connection_service = ChannelConnectionService(db_session, gateway=FakeYouTubeGateway())
    url = connection_service.start_connection(organization_id=org.id, user_id=user.id)
    channel = await connection_service.complete_connection(
        code="fake-code", state=url.split("state=")[1], authenticated_user_id=user.id
    )

    with pytest.raises(DomainError):
        await _strategy_service(db_session).generate_new_version(
            channel_id=channel.id, organization_id=org.id
        )


@pytest.mark.anyio
async def test_generate_new_version_unknown_channel_raises(db_session):
    org, _user = _org_and_user(db_session)

    with pytest.raises(NotFoundError):
        await _strategy_service(db_session).generate_new_version(
            channel_id=uuid.uuid4(), organization_id=org.id
        )


@pytest.mark.anyio
async def test_approve_activates_draft_and_archives_previous(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)
    service = _strategy_service(db_session)

    first = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)
    approved_first = service.approve(
        channel_id=channel.id, strategy_id=first.id, organization_id=org.id, user_id=user.id
    )
    assert approved_first.status == ContentStrategyStatus.ACTIVE
    assert approved_first.activated_at is not None

    second = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)
    approved_second = service.approve(
        channel_id=channel.id, strategy_id=second.id, organization_id=org.id, user_id=user.id
    )

    db_session.refresh(first)
    assert first.status == ContentStrategyStatus.ARCHIVED
    assert approved_second.status == ContentStrategyStatus.ACTIVE

    active = service.strategies.get_active(channel.id, organization_id=org.id)
    assert active.id == approved_second.id


@pytest.mark.anyio
async def test_approve_unknown_strategy_raises(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)

    with pytest.raises(NotFoundError):
        _strategy_service(db_session).approve(
            channel_id=channel.id,
            strategy_id=uuid.uuid4(),
            organization_id=org.id,
            user_id=user.id,
        )


@pytest.mark.anyio
async def test_approve_already_active_strategy_raises(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)
    service = _strategy_service(db_session)

    strategy = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)
    service.approve(
        channel_id=channel.id, strategy_id=strategy.id, organization_id=org.id, user_id=user.id
    )

    with pytest.raises(DomainError):
        service.approve(
            channel_id=channel.id, strategy_id=strategy.id, organization_id=org.id, user_id=user.id
        )


@pytest.mark.anyio
async def test_add_and_list_rules(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)
    service = _strategy_service(db_session)
    strategy = await service.generate_new_version(channel_id=channel.id, organization_id=org.id)

    rule = service.add_rule(
        channel_id=channel.id,
        strategy_id=strategy.id,
        organization_id=org.id,
        rule_type="publishing_constraint",
        rule_json={"description": "Nunca publicar dois videos longos no mesmo dia"},
        priority=1,
    )

    rules = service.list_rules(strategy_id=strategy.id, organization_id=org.id)
    assert len(rules) == 1
    assert rules[0].id == rule.id
    assert rules[0].active is True


@pytest.mark.anyio
async def test_add_rule_to_unknown_strategy_raises(db_session):
    org, user = _org_and_user(db_session)
    channel = await _channel_with_active_dna(db_session, org, user)

    with pytest.raises(NotFoundError):
        _strategy_service(db_session).add_rule(
            channel_id=channel.id,
            strategy_id=uuid.uuid4(),
            organization_id=org.id,
            rule_type="x",
            rule_json={},
        )

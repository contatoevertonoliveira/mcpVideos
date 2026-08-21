from app.models.enums import AgentVersionStatus
from app.repositories.agent import AgentRepository
from app.repositories.agent_prompt import AgentPromptRepository
from app.services.agent_registry import AgentRegistryService


def _service(db_session) -> AgentRegistryService:
    return AgentRegistryService(db_session)


def test_ensure_current_version_creates_agent_and_version(db_session):
    version = _service(db_session).ensure_current_version(
        slug="test_agent",
        name="Test Agent",
        category="intelligence",
        provider="anthropic",
        model="claude-test",
        system_prompt="You are a helpful test agent.",
    )

    assert version.version == 1
    assert version.status == AgentVersionStatus.ACTIVE
    agent = AgentRepository(db_session).get_by_id(version.agent_id)
    assert agent is not None
    assert agent.slug == "test_agent"

    prompt = AgentPromptRepository(db_session).get_by_id(version.prompt_id)
    assert prompt is not None
    assert prompt.system_prompt == "You are a helpful test agent."


def test_ensure_current_version_reuses_when_prompt_unchanged(db_session):
    service = _service(db_session)
    kwargs = dict(
        slug="test_agent",
        name="Test Agent",
        category="intelligence",
        provider="anthropic",
        model="claude-test",
        system_prompt="You are a helpful test agent.",
    )

    first = service.ensure_current_version(**kwargs)
    second = service.ensure_current_version(**kwargs)

    assert first.id == second.id
    assert second.version == 1


def test_ensure_current_version_mints_new_version_on_prompt_change(db_session):
    service = _service(db_session)
    first = service.ensure_current_version(
        slug="test_agent",
        name="Test Agent",
        category="intelligence",
        provider="anthropic",
        model="claude-test",
        system_prompt="Version one prompt text.",
    )

    second = service.ensure_current_version(
        slug="test_agent",
        name="Test Agent",
        category="intelligence",
        provider="anthropic",
        model="claude-test",
        system_prompt="Version two prompt text - content changed.",
    )

    assert second.id != first.id
    assert second.version == 2
    assert second.status == AgentVersionStatus.ACTIVE

    db_session.refresh(first)
    assert first.status == AgentVersionStatus.DEPRECATED

    active = service.agent_versions.get_active(first.agent_id)
    assert active.id == second.id

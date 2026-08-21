import uuid

import pytest

from app.agents.runtime import run_structured_agent
from app.agents.schemas import ChannelAnalystOutput
from app.gateways.llm import FakeLLMGateway, LLMGateway, LLMGenerationError
from app.models.enums import AgentRunStatus
from app.repositories.agent_run import AgentRunRepository
from app.services.organization import OrganizationService


class _FailingLLMGateway(LLMGateway):
    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        raise LLMGenerationError("boom")

    async def generate_structured(self, *, prompt_id, system_prompt, user_prompt, response_model):
        raise LLMGenerationError("boom")


def _org(db_session):
    return OrganizationService(db_session).create_organization(name="Acme")


@pytest.mark.anyio
async def test_run_structured_agent_records_completed_run(db_session):
    org = _org(db_session)
    correlation_id = uuid.uuid4()

    result = await run_structured_agent(
        FakeLLMGateway(),
        agent_id="channel_analyst",
        version="v1",
        user_prompt="Analyze this channel.",
        response_model=ChannelAnalystOutput,
        session=db_session,
        organization_id=org.id,
        correlation_id=correlation_id,
    )

    assert isinstance(result, ChannelAnalystOutput)

    runs = AgentRunRepository(db_session).list_by_correlation_id(
        correlation_id, organization_id=org.id
    )
    assert len(runs) == 1
    assert runs[0].status == AgentRunStatus.COMPLETED
    assert runs[0].output_json is not None
    assert runs[0].completed_at is not None


@pytest.mark.anyio
async def test_run_structured_agent_records_failed_run_and_reraises(db_session):
    org = _org(db_session)
    correlation_id = uuid.uuid4()

    with pytest.raises(LLMGenerationError):
        await run_structured_agent(
            _FailingLLMGateway(),
            agent_id="channel_analyst",
            version="v1",
            user_prompt="Analyze this channel.",
            response_model=ChannelAnalystOutput,
            session=db_session,
            organization_id=org.id,
            correlation_id=correlation_id,
        )

    runs = AgentRunRepository(db_session).list_by_correlation_id(
        correlation_id, organization_id=org.id
    )
    assert len(runs) == 1
    assert runs[0].status == AgentRunStatus.FAILED
    assert runs[0].error_message == "boom"


@pytest.mark.anyio
async def test_run_structured_agent_reuses_agent_version_across_calls(db_session):
    org = _org(db_session)

    await run_structured_agent(
        FakeLLMGateway(),
        agent_id="channel_analyst",
        version="v1",
        user_prompt="First call.",
        response_model=ChannelAnalystOutput,
        session=db_session,
        organization_id=org.id,
    )
    await run_structured_agent(
        FakeLLMGateway(),
        agent_id="channel_analyst",
        version="v1",
        user_prompt="Second call.",
        response_model=ChannelAnalystOutput,
        session=db_session,
        organization_id=org.id,
    )

    runs = AgentRunRepository(db_session).list(organization_id=org.id)
    assert len({run.agent_version_id for run in runs}) == 1

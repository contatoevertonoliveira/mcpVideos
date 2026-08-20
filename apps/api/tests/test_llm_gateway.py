import pytest

from app.agents.schemas import AudienceAnalystOutput, ChannelAnalystOutput
from app.gateways.llm import FakeLLMGateway, LLMGenerationError


@pytest.mark.anyio
async def test_fake_gateway_returns_canned_channel_analyst_output():
    gateway = FakeLLMGateway()

    output = await gateway.generate_structured(
        prompt_id="channel_analyst.v1",
        system_prompt="",
        user_prompt="",
        response_model=ChannelAnalystOutput,
    )

    assert 0.0 <= output.confidence <= 1.0
    assert output.evidence


@pytest.mark.anyio
async def test_fake_gateway_returns_canned_audience_analyst_output():
    gateway = FakeLLMGateway()

    output = await gateway.generate_structured(
        prompt_id="audience_analyst.v1",
        system_prompt="",
        user_prompt="",
        response_model=AudienceAnalystOutput,
    )

    assert 0.0 <= output.confidence <= 1.0
    assert output.language


@pytest.mark.anyio
async def test_fake_gateway_is_deterministic():
    gateway = FakeLLMGateway()

    first = await gateway.generate_structured(
        prompt_id="channel_analyst.v1",
        system_prompt="",
        user_prompt="",
        response_model=ChannelAnalystOutput,
    )
    second = await gateway.generate_structured(
        prompt_id="channel_analyst.v1",
        system_prompt="",
        user_prompt="",
        response_model=ChannelAnalystOutput,
    )

    assert first == second


@pytest.mark.anyio
async def test_fake_gateway_raises_for_unknown_prompt_id():
    gateway = FakeLLMGateway()

    with pytest.raises(LLMGenerationError):
        await gateway.generate_structured(
            prompt_id="does_not_exist.v1",
            system_prompt="",
            user_prompt="",
            response_model=ChannelAnalystOutput,
        )

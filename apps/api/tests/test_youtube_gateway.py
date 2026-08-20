import pytest

from app.gateways.youtube import FakeYouTubeGateway


@pytest.mark.anyio
async def test_fake_gateway_full_flow_is_deterministic():
    gateway = FakeYouTubeGateway()

    url = gateway.get_authorization_url("some-state")
    assert "state=some-state" in url

    tokens = await gateway.exchange_code("code-abc")
    assert tokens.access_token == "fake-access-code-abc"
    assert tokens.refresh_token == "fake-refresh-code-abc"

    info = await gateway.get_channel_info(tokens.access_token)
    assert info.external_channel_id.startswith("UC")

    info_again = await gateway.get_channel_info(tokens.access_token)
    assert info.external_channel_id == info_again.external_channel_id

    refreshed = await gateway.refresh_access_token(tokens.refresh_token)
    assert refreshed.refresh_token == tokens.refresh_token

    await gateway.revoke_token(tokens.access_token)  # never raises

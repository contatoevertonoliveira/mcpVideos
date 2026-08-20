import pytest

from app.gateways.youtube import FakeYouTubeGateway, parse_iso8601_duration


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


@pytest.mark.anyio
async def test_fake_gateway_content_is_deterministic_across_calls():
    """Same reasoning as get_channel_info: a re-sync must see the exact
    same playlists/videos, or the upsert-not-duplicate logic can't work."""
    gateway = FakeYouTubeGateway()
    channel_id = "UCfakegateway00000000001"

    playlists_1 = await gateway.list_playlists("token", channel_id)
    playlists_2 = await gateway.list_playlists("token", channel_id)
    assert [p.external_playlist_id for p in playlists_1] == [
        p.external_playlist_id for p in playlists_2
    ]

    videos_1 = await gateway.list_videos("token", channel_id)
    videos_2 = await gateway.list_videos("token", channel_id)
    assert [v.external_video_id for v in videos_1] == [v.external_video_id for v in videos_2]
    assert len(videos_1) > 0
    assert any(v.duration_seconds <= 60 for v in videos_1)
    assert any(v.duration_seconds > 60 for v in videos_1)

    metrics = await gateway.get_video_metrics("token", [v.external_video_id for v in videos_1])
    assert len(metrics) == len(videos_1)
    assert all(m.views is not None for m in metrics)


def test_parse_iso8601_duration():
    assert parse_iso8601_duration("PT4M13S") == 4 * 60 + 13
    assert parse_iso8601_duration("PT1H2M3S") == 3723
    assert parse_iso8601_duration("PT45S") == 45
    assert parse_iso8601_duration("P0D") is None
    assert parse_iso8601_duration("not-a-duration") is None

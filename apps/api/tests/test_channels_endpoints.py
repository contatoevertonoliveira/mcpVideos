import json
import uuid

from app.models.enums import OrganizationRole
from app.services.auth import AuthService
from app.services.organization import OrganizationService

REGISTER_PAYLOAD = {
    "email": "owner@example.com",
    "name": "Owner",
    "password": "supersecret1",
    "organization_name": "Acme",
}


def _register_and_get_token(client) -> str:
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    return response.json()["token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_list_channels_starts_empty(client):
    token = _register_and_get_token(client)

    response = client.get("/api/v1/channels", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json() == []


def test_connect_returns_fake_authorization_url(client):
    token = _register_and_get_token(client)

    response = client.post("/api/v1/channels/connect", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json()["authorization_url"].startswith(
        "http://localhost:3000/oauth/youtube/callback?code="
    )


def test_full_connect_flow(client):
    token = _register_and_get_token(client)
    connect_response = client.post("/api/v1/channels/connect", headers=_auth_headers(token))
    auth_url = connect_response.json()["authorization_url"]
    state = auth_url.split("state=")[1]

    callback_response = client.post(
        "/api/v1/channels/callback",
        json={"code": "code-xyz", "state": state},
        headers=_auth_headers(token),
    )

    assert callback_response.status_code == 200
    body = callback_response.json()
    assert body["name"] == "Canal de Teste (Fake Gateway)"
    assert body["status"] == "active"
    assert body["connection_status"] == "connected"

    # Never expose tokens over the API (Documento 09 sec. 20).
    raw_body = json.dumps(body)
    assert "access_token" not in raw_body
    assert "refresh_token" not in raw_body
    assert "fake-access" not in raw_body

    list_response = client.get("/api/v1/channels", headers=_auth_headers(token))
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == body["id"]


def test_callback_with_invalid_state_fails(client):
    token = _register_and_get_token(client)

    response = client.post(
        "/api/v1/channels/callback",
        json={"code": "code-xyz", "state": "garbage"},
        headers=_auth_headers(token),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OAUTH_STATE"


def test_connect_requires_authentication(client):
    response = client.post("/api/v1/channels/connect")

    assert response.status_code == 401


def test_disconnect_flow(client):
    token = _register_and_get_token(client)
    auth_url = client.post("/api/v1/channels/connect", headers=_auth_headers(token)).json()[
        "authorization_url"
    ]
    state = auth_url.split("state=")[1]
    channel = client.post(
        "/api/v1/channels/callback",
        json={"code": "code-xyz", "state": state},
        headers=_auth_headers(token),
    ).json()

    response = client.post(
        f"/api/v1/channels/{channel['id']}/disconnect", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "disabled"
    assert body["connection_status"] == "disconnected"


def test_disconnect_unknown_channel_returns_404(client):
    token = _register_and_get_token(client)

    response = client.post(
        f"/api/v1/channels/{uuid.uuid4()}/disconnect", headers=_auth_headers(token)
    )

    assert response.status_code == 404


def test_viewer_cannot_connect_channel(client, db_session):
    """A VIEWER member is a real member (unlike a stranger) but still
    lacks CHANNEL_MANAGE - exercises require_permission end-to-end."""
    owner_token = _register_and_get_token(client)
    owner_org_id = uuid.UUID(
        client.get("/api/v1/auth/me", headers=_auth_headers(owner_token)).json()[
            "active_organization_id"
        ]
    )

    viewer_token = client.post(
        "/api/v1/auth/register",
        json={
            "email": "viewer@example.com",
            "name": "Viewer",
            "password": "supersecret1",
            "organization_name": "Viewer Personal Org",
        },
    ).json()["token"]
    viewer_user_session = AuthService(db_session).get_valid_session(viewer_token)
    OrganizationService(db_session).add_member(
        organization_id=owner_org_id,
        user_id=viewer_user_session.user_id,
        role=OrganizationRole.VIEWER,
    )
    AuthService(db_session).switch_organization(
        raw_token=viewer_token, organization_id=owner_org_id
    )

    response = client.post("/api/v1/channels/connect", headers=_auth_headers(viewer_token))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def _connect_channel(client, token: str) -> dict:
    auth_url = client.post("/api/v1/channels/connect", headers=_auth_headers(token)).json()[
        "authorization_url"
    ]
    state = auth_url.split("state=")[1]
    return client.post(
        "/api/v1/channels/callback",
        json={"code": "code-xyz", "state": state},
        headers=_auth_headers(token),
    ).json()


def test_connecting_a_channel_dispatches_a_sync_job(client, monkeypatch):
    from app.tasks import channel_sync as channel_sync_tasks

    token = _register_and_get_token(client)
    _connect_channel(client, token)

    channel_sync_tasks.run_channel_sync_task.delay.assert_called_once()
    call_kwargs = channel_sync_tasks.run_channel_sync_task.delay.call_args.kwargs
    assert call_kwargs["sync_type"] == "initial"


def test_trigger_sync_creates_job(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.post(f"/api/v1/channels/{channel['id']}/sync", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    assert "correlation_id" in body


def test_trigger_sync_unknown_channel_returns_404(client):
    token = _register_and_get_token(client)

    response = client.post(f"/api/v1/channels/{uuid.uuid4()}/sync", headers=_auth_headers(token))

    assert response.status_code == 404


def test_list_videos_and_sync_runs_start_empty_for_a_new_channel(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    videos_response = client.get(
        f"/api/v1/channels/{channel['id']}/videos", headers=_auth_headers(token)
    )
    runs_response = client.get(
        f"/api/v1/channels/{channel['id']}/sync-runs", headers=_auth_headers(token)
    )

    # The connect flow only dispatches the Celery task (mocked in tests) -
    # it does not run the import synchronously, so no videos exist yet, but
    # the connection-time INITIAL sync_run row from Fase 04 does.
    assert videos_response.status_code == 200
    assert videos_response.json() == []
    assert runs_response.status_code == 200
    assert len(runs_response.json()) == 1
    assert runs_response.json()[0]["sync_type"] == "initial"


def test_get_intelligence_before_analysis_returns_nulls(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.get(
        f"/api/v1/channels/{channel['id']}/intelligence", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json() == {"channel_profile": None, "audience_profile": None}


def test_trigger_analysis_creates_job(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.post(
        f"/api/v1/channels/{channel['id']}/analyze", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    assert "correlation_id" in body


def test_trigger_analysis_unknown_channel_returns_404(client):
    token = _register_and_get_token(client)

    response = client.post(f"/api/v1/channels/{uuid.uuid4()}/analyze", headers=_auth_headers(token))

    assert response.status_code == 404


def test_get_intelligence_after_analysis_returns_profiles(client, db_session):
    import asyncio

    from app.gateways.llm import FakeLLMGateway
    from app.gateways.youtube import FakeYouTubeGateway
    from app.models.enums import SyncType
    from app.services.channel_intelligence import ChannelIntelligenceService
    from app.services.channel_sync import ChannelSyncService

    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)
    channel_id = uuid.UUID(channel["id"])
    organization_id = uuid.UUID(channel["organization_id"])

    # The endpoints only dispatch (mocked) Celery tasks - run the sync and
    # analysis synchronously here, sharing the same db_session as the
    # client fixture, to seed real data for the GET below.
    async def _seed() -> None:
        await ChannelSyncService(db_session, gateway=FakeYouTubeGateway()).run_sync(
            channel_id=channel_id, organization_id=organization_id, sync_type=SyncType.MANUAL
        )
        await ChannelIntelligenceService(db_session, llm_gateway=FakeLLMGateway()).analyze_channel(
            channel_id=channel_id, organization_id=organization_id
        )

    asyncio.run(_seed())

    response = client.get(
        f"/api/v1/channels/{channel['id']}/intelligence", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["channel_profile"] is not None
    assert body["audience_profile"] is not None
    assert body["channel_profile"]["primary_language"] == "pt-BR"


def test_get_dna_before_generation_returns_null(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.get(f"/api/v1/channels/{channel['id']}/dna", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json() is None


def test_trigger_dna_generation_creates_job(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.post(
        f"/api/v1/channels/{channel['id']}/dna/generate", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    assert "correlation_id" in body


def test_trigger_dna_generation_unknown_channel_returns_404(client):
    token = _register_and_get_token(client)

    response = client.post(
        f"/api/v1/channels/{uuid.uuid4()}/dna/generate", headers=_auth_headers(token)
    )

    assert response.status_code == 404


def test_get_dna_after_generation_returns_active_version(client, db_session):
    import asyncio

    from app.gateways.llm import FakeLLMGateway
    from app.gateways.youtube import FakeYouTubeGateway
    from app.models.enums import SyncType
    from app.services.channel_dna import ChannelDNAService
    from app.services.channel_sync import ChannelSyncService

    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)
    channel_id = uuid.UUID(channel["id"])
    organization_id = uuid.UUID(channel["organization_id"])

    async def _seed() -> None:
        await ChannelSyncService(db_session, gateway=FakeYouTubeGateway()).run_sync(
            channel_id=channel_id, organization_id=organization_id, sync_type=SyncType.MANUAL
        )
        await ChannelDNAService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
            channel_id=channel_id, organization_id=organization_id
        )

    asyncio.run(_seed())

    dna_response = client.get(f"/api/v1/channels/{channel['id']}/dna", headers=_auth_headers(token))
    history_response = client.get(
        f"/api/v1/channels/{channel['id']}/dna/history", headers=_auth_headers(token)
    )

    assert dna_response.status_code == 200
    assert dna_response.json()["status"] == "active"
    assert dna_response.json()["version"] == 1
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1


def test_brand_profile_starts_empty_then_can_be_set(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    before = client.get(
        f"/api/v1/channels/{channel['id']}/brand-profile", headers=_auth_headers(token)
    )
    assert before.status_code == 200
    assert before.json() is None

    put_response = client.put(
        f"/api/v1/channels/{channel['id']}/brand-profile",
        headers=_auth_headers(token),
        json={"name": "Acme Brand", "colors_json": {"primary": "#000000"}},
    )
    assert put_response.status_code == 200
    assert put_response.json()["name"] == "Acme Brand"

    after = client.get(
        f"/api/v1/channels/{channel['id']}/brand-profile", headers=_auth_headers(token)
    )
    assert after.json()["name"] == "Acme Brand"
    assert after.json()["colors_json"] == {"primary": "#000000"}


def _seed_active_dna(db_session, channel_id, organization_id):
    import asyncio

    from app.gateways.llm import FakeLLMGateway
    from app.gateways.youtube import FakeYouTubeGateway
    from app.models.enums import SyncType
    from app.services.channel_dna import ChannelDNAService
    from app.services.channel_sync import ChannelSyncService

    async def _seed() -> None:
        await ChannelSyncService(db_session, gateway=FakeYouTubeGateway()).run_sync(
            channel_id=channel_id, organization_id=organization_id, sync_type=SyncType.MANUAL
        )
        await ChannelDNAService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
            channel_id=channel_id, organization_id=organization_id
        )

    asyncio.run(_seed())


def test_get_strategy_before_generation_returns_nulls(client):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)

    response = client.get(
        f"/api/v1/channels/{channel['id']}/strategy", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json() == {"active": None, "pending_draft": None}


def test_trigger_strategy_generation_unknown_channel_returns_404(client):
    token = _register_and_get_token(client)

    response = client.post(
        f"/api/v1/channels/{uuid.uuid4()}/strategy/generate", headers=_auth_headers(token)
    )

    assert response.status_code == 404


def test_trigger_strategy_generation_creates_job(client, db_session):
    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)
    channel_id = uuid.UUID(channel["id"])
    organization_id = uuid.UUID(channel["organization_id"])
    _seed_active_dna(db_session, channel_id, organization_id)

    response = client.post(
        f"/api/v1/channels/{channel['id']}/strategy/generate", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    assert "correlation_id" in body


def test_strategy_generate_then_approve_flow(client, db_session):
    from app.gateways.llm import FakeLLMGateway
    from app.services.channel_strategy import ChannelStrategyService

    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)
    channel_id = uuid.UUID(channel["id"])
    organization_id = uuid.UUID(channel["organization_id"])
    _seed_active_dna(db_session, channel_id, organization_id)

    import asyncio

    strategy = asyncio.run(
        ChannelStrategyService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
            channel_id=channel_id, organization_id=organization_id
        )
    )

    status_before = client.get(
        f"/api/v1/channels/{channel['id']}/strategy", headers=_auth_headers(token)
    )
    assert status_before.json()["active"] is None
    assert status_before.json()["pending_draft"]["id"] == str(strategy.id)
    assert len(status_before.json()["pending_draft"]["pillars"]) == 3

    approve_response = client.post(
        f"/api/v1/channels/{channel['id']}/strategy/{strategy.id}/approve",
        headers=_auth_headers(token),
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "active"

    status_after = client.get(
        f"/api/v1/channels/{channel['id']}/strategy", headers=_auth_headers(token)
    )
    assert status_after.json()["active"]["id"] == str(strategy.id)
    assert status_after.json()["pending_draft"] is None

    history_response = client.get(
        f"/api/v1/channels/{channel['id']}/strategy/history", headers=_auth_headers(token)
    )
    assert len(history_response.json()) == 1


def test_strategy_rules_endpoints(client, db_session):
    from app.gateways.llm import FakeLLMGateway
    from app.services.channel_strategy import ChannelStrategyService

    token = _register_and_get_token(client)
    channel = _connect_channel(client, token)
    channel_id = uuid.UUID(channel["id"])
    organization_id = uuid.UUID(channel["organization_id"])
    _seed_active_dna(db_session, channel_id, organization_id)

    import asyncio

    strategy = asyncio.run(
        ChannelStrategyService(db_session, llm_gateway=FakeLLMGateway()).generate_new_version(
            channel_id=channel_id, organization_id=organization_id
        )
    )

    create_response = client.post(
        f"/api/v1/channels/{channel['id']}/strategy/{strategy.id}/rules",
        headers=_auth_headers(token),
        json={"rule_type": "publishing_constraint", "rule_json": {"max_long_form_per_day": 1}},
    )
    assert create_response.status_code == 200
    assert create_response.json()["rule_type"] == "publishing_constraint"

    list_response = client.get(
        f"/api/v1/channels/{channel['id']}/strategy/{strategy.id}/rules",
        headers=_auth_headers(token),
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

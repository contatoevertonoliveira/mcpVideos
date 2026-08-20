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

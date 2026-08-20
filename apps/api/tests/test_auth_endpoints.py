from app.security.rate_limit import MAX_ATTEMPTS

REGISTER_PAYLOAD = {
    "email": "ana@example.com",
    "name": "Ana",
    "password": "supersecret1",
    "organization_name": "Ana Co",
}


def _register(client):
    return client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)


def test_register_returns_token_user_and_organization(client):
    response = _register(client)

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "ana@example.com"
    assert body["organization"]["name"] == "Ana Co"
    assert body["token"]


def test_register_duplicate_email_fails(client):
    _register(client)

    response = _register(client)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMAIL_TAKEN"


def test_login_success_returns_memberships(client):
    _register(client)

    response = client.post(
        "/api/v1/auth/login", json={"email": "ana@example.com", "password": "supersecret1"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["memberships"][0]["organization_name"] == "Ana Co"
    assert body["memberships"][0]["role"] == "owner"


def test_login_wrong_password_returns_401(client):
    _register(client)

    response = client.post(
        "/api/v1/auth/login", json={"email": "ana@example.com", "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_without_token_returns_401(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_valid_token_returns_current_user(client):
    token = _register(client).json()["token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "ana@example.com"


def test_logout_revokes_session(client):
    token = _register(client).json()["token"]

    logout_response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert logout_response.status_code == 200
    assert me_response.status_code == 401


def test_switch_organization_denied_for_non_member(client):
    token = _register(client).json()["token"]
    other_org_id = client.post(
        "/api/v1/auth/register",
        json={
            "email": "outra@example.com",
            "name": "Outra",
            "password": "supersecret1",
            "organization_name": "Other Co",
        },
    ).json()["organization"]["id"]

    response = client.post(
        "/api/v1/auth/organization",
        json={"organization_id": other_org_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_login_rate_limited_after_max_attempts(client):
    _register(client)
    wrong_payload = {"email": "ana@example.com", "password": "wrong-password"}

    for _ in range(MAX_ATTEMPTS):
        client.post("/api/v1/auth/login", json=wrong_payload)

    response = client.post("/api/v1/auth/login", json=wrong_payload)

    assert response.status_code == 429

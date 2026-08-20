from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.services.auth import AuthService
from app.services.organization import OrganizationService


def _register(db_session, email="ana@example.com"):
    return AuthService(db_session).register(
        email=email, name="Ana", password="supersecret1", organization_name="Ana Co"
    )


def test_register_creates_user_org_owner_and_session(db_session):
    user, organization, token = _register(db_session)

    assert user.email == "ana@example.com"
    assert organization.name == "Ana Co"
    assert token

    user_session = AuthService(db_session).get_valid_session(token)
    assert user_session.user_id == user.id
    assert user_session.active_organization_id == organization.id


def test_login_success(db_session):
    _register(db_session)

    user, token, user_session = AuthService(db_session).login(
        email="ana@example.com", password="supersecret1"
    )

    assert user.email == "ana@example.com"
    assert user_session.active_organization_id is not None


def test_login_wrong_password_raises(db_session):
    _register(db_session)

    with pytest.raises(AuthenticationError):
        AuthService(db_session).login(email="ana@example.com", password="wrong-password")


def test_login_unknown_email_raises(db_session):
    with pytest.raises(AuthenticationError):
        AuthService(db_session).login(email="nobody@example.com", password="whatever123")


def test_get_valid_session_rejects_unknown_token(db_session):
    with pytest.raises(AuthenticationError):
        AuthService(db_session).get_valid_session("not-a-real-token")


def test_get_valid_session_rejects_revoked_session(db_session):
    _, _, token = _register(db_session)
    auth = AuthService(db_session)
    auth.logout(raw_token=token)

    with pytest.raises(AuthenticationError):
        auth.get_valid_session(token)


def test_get_valid_session_rejects_expired_session(db_session):
    _, _, token = _register(db_session)
    auth = AuthService(db_session)
    user_session = auth.get_valid_session(token)
    user_session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.flush()

    with pytest.raises(AuthenticationError):
        auth.get_valid_session(token)


def test_switch_organization_requires_membership(db_session):
    _, _, token = _register(db_session)
    other_org = OrganizationService(db_session).create_organization(name="Other Org")

    with pytest.raises(AuthorizationError):
        AuthService(db_session).switch_organization(raw_token=token, organization_id=other_org.id)


def test_switch_organization_succeeds_for_member(db_session):
    user, first_org, token = _register(db_session)
    second_org = OrganizationService(db_session).create_organization(name="Second Org")
    OrganizationService(db_session).add_member(organization_id=second_org.id, user_id=user.id)

    user_session = AuthService(db_session).switch_organization(
        raw_token=token, organization_id=second_org.id
    )

    assert user_session.active_organization_id == second_org.id


def test_revoke_all_sessions(db_session):
    user, _, token_a = _register(db_session)
    _, _, user_session_b = AuthService(db_session).login(
        email="ana@example.com", password="supersecret1"
    )

    AuthService(db_session).revoke_all_sessions(user.id)

    with pytest.raises(AuthenticationError):
        AuthService(db_session).get_valid_session(token_a)
    assert user_session_b.revoked_at is not None


def test_login_reuses_registration_organization_as_active_org(db_session):
    _, org, _ = _register(db_session)

    _, _, user_session = AuthService(db_session).login(
        email="ana@example.com", password="supersecret1"
    )

    assert user_session.active_organization_id == org.id

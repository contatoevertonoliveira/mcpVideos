"""Exercises the FastAPI dependency wiring in app/api/deps.py directly
(without going through HTTP), since no business endpoint uses
require_permission() yet - that starts arriving with the content-producing
phases."""

import pytest

from app.api.deps import require_permission
from app.core.exceptions import AuthorizationError
from app.domain.permissions import Permission
from app.models.enums import OrganizationRole
from app.services.auth import AuthService
from app.services.organization import OrganizationService


def test_require_permission_dependency_allows_owner(db_session):
    user, org, token = AuthService(db_session).register(
        email="owner@example.com",
        name="Owner",
        password="supersecret1",
        organization_name="Owner Co",
    )
    user_session = AuthService(db_session).get_valid_session(token)

    dependency = require_permission(Permission.BILLING_MANAGE)
    organization_id = dependency(user_session=user_session, organization_id=org.id, db=db_session)

    assert organization_id == org.id


def test_require_permission_dependency_denies_viewer(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user, _, token = AuthService(db_session).register(
        email="viewer@example.com",
        name="Viewer",
        password="supersecret1",
        organization_name="Viewer Personal Org",
    )
    OrganizationService(db_session).add_member(
        organization_id=org.id, user_id=user.id, role=OrganizationRole.VIEWER
    )
    user_session = AuthService(db_session).switch_organization(
        raw_token=token, organization_id=org.id
    )

    dependency = require_permission(Permission.CONTENT_MANAGE)
    with pytest.raises(AuthorizationError):
        dependency(user_session=user_session, organization_id=org.id, db=db_session)

import pytest

from app.core.exceptions import AuthorizationError
from app.domain.permissions import Permission
from app.models.enums import OrganizationRole
from app.services.authorization import AuthorizationService
from app.services.organization import OrganizationService
from app.services.user import UserService


def _member(db_session, role):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email=f"{role.value}@example.com", name=role.value, password="supersecret1"
    )
    OrganizationService(db_session).add_member(organization_id=org.id, user_id=user.id, role=role)
    return org, user


@pytest.mark.parametrize(
    "role,permission,allowed",
    [
        (OrganizationRole.OWNER, Permission.BILLING_MANAGE, True),
        (OrganizationRole.OWNER, Permission.ORGANIZATION_MANAGE, True),
        (OrganizationRole.ADMIN, Permission.BILLING_MANAGE, False),
        (OrganizationRole.ADMIN, Permission.MEMBER_MANAGE, True),
        (OrganizationRole.EDITOR, Permission.CONTENT_MANAGE, True),
        (OrganizationRole.EDITOR, Permission.MEMBER_MANAGE, False),
        (OrganizationRole.VIEWER, Permission.VIEW, True),
        (OrganizationRole.VIEWER, Permission.CONTENT_MANAGE, False),
    ],
)
def test_require_permission_matrix(db_session, role, permission, allowed):
    org, user = _member(db_session, role)
    service = AuthorizationService(db_session)

    if allowed:
        member = service.require_permission(
            organization_id=org.id, user_id=user.id, permission=permission
        )
        assert member.role == role
    else:
        with pytest.raises(AuthorizationError):
            service.require_permission(
                organization_id=org.id, user_id=user.id, permission=permission
            )


def test_non_member_is_denied(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    user = UserService(db_session).create_user(
        email="outsider@example.com", name="Outsider", password="supersecret1"
    )

    with pytest.raises(AuthorizationError):
        AuthorizationService(db_session).require_permission(
            organization_id=org.id, user_id=user.id, permission=Permission.VIEW
        )

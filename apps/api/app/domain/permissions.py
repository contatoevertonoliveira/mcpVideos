"""Role -> permission mapping (Documento 09, secoes 12-17).

Coarse-grained on purpose for the MVP: a fixed set of permissions per role,
not yet the fully granular per-resource permission model Documento 09
sec. 17 describes as a *future* preparation item.
"""

from enum import StrEnum

from app.models.enums import OrganizationRole


class Permission(StrEnum):
    ORGANIZATION_MANAGE = "organization.manage"
    BILLING_MANAGE = "billing.manage"
    MEMBER_MANAGE = "member.manage"
    CHANNEL_MANAGE = "channel.manage"
    AUTOMATION_MANAGE = "automation.manage"
    CONTENT_MANAGE = "content.manage"
    CONTENT_APPROVE = "content.approve"
    VIEW = "view"


_OWNER_ONLY: frozenset[Permission] = frozenset(
    {Permission.ORGANIZATION_MANAGE, Permission.BILLING_MANAGE}
)
_ALL_PERMISSIONS: frozenset[Permission] = frozenset(Permission)

_ROLE_PERMISSIONS: dict[OrganizationRole, frozenset[Permission]] = {
    OrganizationRole.OWNER: _ALL_PERMISSIONS,
    OrganizationRole.ADMIN: _ALL_PERMISSIONS - _OWNER_ONLY,
    OrganizationRole.EDITOR: frozenset(
        {Permission.CONTENT_MANAGE, Permission.CONTENT_APPROVE, Permission.VIEW}
    ),
    OrganizationRole.VIEWER: frozenset({Permission.VIEW}),
}


def role_has_permission(role: OrganizationRole, permission: Permission) -> bool:
    return permission in _ROLE_PERMISSIONS.get(role, frozenset())

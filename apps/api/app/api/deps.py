"""Shared FastAPI dependencies for authentication and authorization.

Documento 02, secao 18: nunca confiar apenas na UI - toda permissao
relevante e validada aqui, no backend, antes do endpoint executar.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AuthenticationError
from app.db.session import get_db
from app.domain.permissions import Permission
from app.models.session import UserSession
from app.models.user import User
from app.services.auth import AuthService
from app.services.authorization import AuthorizationService


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Missing bearer token", code="MISSING_TOKEN")
    return authorization[len("bearer ") :].strip()


def get_current_session(
    token: str = Depends(get_bearer_token), db: DbSession = Depends(get_db)
) -> UserSession:
    return AuthService(db).get_valid_session(token)


def get_current_user(
    user_session: UserSession = Depends(get_current_session), db: DbSession = Depends(get_db)
) -> User:
    user = db.get(User, user_session.user_id)
    if user is None:
        raise AuthenticationError("User not found", code="USER_NOT_FOUND")
    return user


def get_current_organization_id(
    user_session: UserSession = Depends(get_current_session),
) -> uuid.UUID:
    if user_session.active_organization_id is None:
        raise AuthenticationError(
            "No active organization selected", code="NO_ACTIVE_ORGANIZATION"
        )
    return user_session.active_organization_id


def require_permission(permission: Permission) -> Callable[..., uuid.UUID]:
    """Returns a dependency that enforces ``permission`` in the request's
    active organization, and yields that organization_id for the endpoint
    to use - guaranteeing every scoped query is tenant-checked upstream."""

    def dependency(
        user_session: UserSession = Depends(get_current_session),
        organization_id: uuid.UUID = Depends(get_current_organization_id),
        db: DbSession = Depends(get_db),
    ) -> uuid.UUID:
        AuthorizationService(db).require_permission(
            organization_id=organization_id,
            user_id=user_session.user_id,
            permission=permission,
        )
        return organization_id

    return dependency

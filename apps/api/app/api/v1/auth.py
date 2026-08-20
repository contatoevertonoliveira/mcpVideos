from __future__ import annotations

import ipaddress
import uuid

import redis
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_bearer_token, get_current_session, get_current_user
from app.core.exceptions import AuthenticationError
from app.core.redis import get_redis_client
from app.db.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MembershipSummary,
    RegisterRequest,
    RegisterResponse,
    SwitchOrganizationRequest,
)
from app.schemas.organization import OrganizationRead
from app.schemas.user import UserRead
from app.security.rate_limit import LoginRateLimiter
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_info(request: Request) -> tuple[str | None, str | None]:
    host = request.client.host if request.client else None
    ip_address = None
    if host:
        try:
            ipaddress.ip_address(host)
            ip_address = host
        except ValueError:
            # e.g. Starlette's TestClient reports "testclient", or a proxy
            # in front of the API may not always forward a real IP. This
            # field is best-effort for audit purposes, never critical.
            ip_address = None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


def _memberships_summary(db: DbSession, user_id: uuid.UUID) -> list[MembershipSummary]:
    memberships = OrganizationMemberRepository(db).list_for_user(user_id=user_id)
    org_repo = OrganizationRepository(db)
    summaries = []
    for member in memberships:
        organization = org_repo.get_by_id(member.organization_id)
        if organization is not None:
            summaries.append(
                MembershipSummary(
                    organization_id=member.organization_id,
                    organization_name=organization.name,
                    role=member.role,
                )
            )
    return summaries


@router.post("/register", response_model=RegisterResponse)
def register(
    payload: RegisterRequest, request: Request, db: DbSession = Depends(get_db)
) -> RegisterResponse:
    ip_address, user_agent = _client_info(request)
    user, organization, token = AuthService(db).register(
        email=payload.email,
        name=payload.name,
        password=payload.password,
        organization_name=payload.organization_name,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return RegisterResponse(
        token=token,
        user=UserRead.model_validate(user),
        organization=OrganizationRead.model_validate(organization),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: DbSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> AuthResponse:
    ip_address, user_agent = _client_info(request)
    limiter = LoginRateLimiter(redis_client)
    limiter.check(payload.email)

    try:
        user, token, user_session = AuthService(db).login(
            email=payload.email,
            password=payload.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except AuthenticationError:
        limiter.record_failure(payload.email)
        raise

    limiter.reset(payload.email)
    return AuthResponse(
        token=token,
        user=UserRead.model_validate(user),
        active_organization_id=user_session.active_organization_id,
        memberships=_memberships_summary(db, user.id),
    )


@router.post("/logout")
def logout(token: str = Depends(get_bearer_token), db: DbSession = Depends(get_db)) -> dict:
    AuthService(db).logout(raw_token=token)
    return {"data": {"status": "logged_out"}, "meta": {}}


@router.get("/me", response_model=AuthResponse)
def me(
    user: User = Depends(get_current_user),
    user_session: UserSession = Depends(get_current_session),
    db: DbSession = Depends(get_db),
) -> AuthResponse:
    return AuthResponse(
        token=None,
        user=UserRead.model_validate(user),
        active_organization_id=user_session.active_organization_id,
        memberships=_memberships_summary(db, user.id),
    )


@router.post("/organization")
def switch_organization(
    payload: SwitchOrganizationRequest,
    token: str = Depends(get_bearer_token),
    db: DbSession = Depends(get_db),
) -> dict:
    user_session = AuthService(db).switch_organization(
        raw_token=token, organization_id=payload.organization_id
    )
    return {
        "data": {"active_organization_id": str(user_session.active_organization_id)},
        "meta": {},
    }

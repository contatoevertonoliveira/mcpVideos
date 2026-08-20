from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.enums import AuditActorType, OrganizationRole, UserStatus
from app.models.organization import Organization
from app.models.session import UserSession
from app.models.user import User
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.session import SessionRepository
from app.security.password import verify_password
from app.security.tokens import generate_session_token, hash_token
from app.services.audit import AuditService
from app.services.organization import OrganizationService
from app.services.user import UserService

SESSION_LIFETIME = timedelta(days=7)


class AuthService:
    """Documento 09, secoes 3-7: autenticacao propria da plataforma,
    separada da autorizacao OAuth de providers externos (Fase 04)."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserService(session)
        self.organizations = OrganizationService(session)
        self.members = OrganizationMemberRepository(session)
        self.sessions = SessionRepository(session)
        self.audit = AuditService(session)

    def register(
        self,
        *,
        email: str,
        name: str,
        password: str,
        organization_name: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Organization, str]:
        user = self.users.create_user(email=email, name=name, password=password)
        organization = self.organizations.create_organization(name=organization_name)
        self.organizations.add_member(
            organization_id=organization.id, user_id=user.id, role=OrganizationRole.OWNER
        )

        raw_token, _ = self._create_session(
            user_id=user.id,
            organization_id=organization.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.audit.record(
            organization_id=organization.id,
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            action="user.registered",
            resource_type="user",
            resource_id=user.id,
        )
        return user, organization, raw_token

    def login(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str, UserSession]:
        user = self.users.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password", code="INVALID_CREDENTIALS")
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("This account is not active", code="ACCOUNT_NOT_ACTIVE")

        memberships = self.members.list_for_user(user_id=user.id)
        active_organization_id = memberships[0].organization_id if memberships else None

        raw_token, user_session = self._create_session(
            user_id=user.id,
            organization_id=active_organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        user.last_login_at = datetime.now(UTC)
        self.session.flush()

        if active_organization_id is not None:
            self.audit.record(
                organization_id=active_organization_id,
                actor_type=AuditActorType.USER,
                actor_id=user.id,
                action="user.login",
                resource_type="user",
                resource_id=user.id,
            )
        return user, raw_token, user_session

    def logout(self, *, raw_token: str) -> None:
        user_session = self.get_valid_session(raw_token)
        user_session.revoked_at = datetime.now(UTC)
        self.session.flush()

        if user_session.active_organization_id is not None:
            self.audit.record(
                organization_id=user_session.active_organization_id,
                actor_type=AuditActorType.USER,
                actor_id=user_session.user_id,
                action="user.logout",
                resource_type="user",
                resource_id=user_session.user_id,
            )

    def get_valid_session(self, raw_token: str) -> UserSession:
        user_session = self.sessions.get_by_token_hash(hash_token(raw_token))
        if user_session is None:
            raise AuthenticationError("Invalid session", code="INVALID_SESSION")

        now = datetime.now(UTC)
        if user_session.revoked_at is not None:
            raise AuthenticationError("Session has been revoked", code="SESSION_REVOKED")
        if user_session.expires_at < now:
            raise AuthenticationError("Session has expired", code="SESSION_EXPIRED")

        user_session.last_seen_at = now
        self.session.flush()
        return user_session

    def switch_organization(self, *, raw_token: str, organization_id: uuid.UUID) -> UserSession:
        user_session = self.get_valid_session(raw_token)
        member = self.members.get_by_user(
            organization_id=organization_id, user_id=user_session.user_id
        )
        if member is None:
            raise AuthorizationError(
                "You are not a member of this organization", code="NOT_A_MEMBER"
            )

        user_session.active_organization_id = organization_id
        self.session.flush()
        return user_session

    def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        """Usado por um futuro "logout de todos os dispositivos" (Documento
        09, secao 7)."""
        now = datetime.now(UTC)
        for user_session in self.sessions.list_active_for_user(user_id):
            user_session.revoked_at = now
        self.session.flush()

    def _create_session(
        self,
        *,
        user_id: uuid.UUID,
        organization_id: uuid.UUID | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[str, UserSession]:
        raw_token = generate_session_token()
        user_session = UserSession(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            active_organization_id=organization_id,
            expires_at=datetime.now(UTC) + SESSION_LIFETIME,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.sessions.add(user_session)
        return raw_token, user_session

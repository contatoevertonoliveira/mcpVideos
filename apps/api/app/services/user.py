from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.user import UserRepository
from app.security.password import hash_password


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def create_user(self, *, email: str, name: str, password: str) -> User:
        if self.users.get_by_email(email) is not None:
            raise DomainError("A user with this email already exists", code="EMAIL_TAKEN")

        user = User(
            email=email,
            name=name,
            password_hash=hash_password(password),
            status=UserStatus.ACTIVE,
        )
        return self.users.add(user)

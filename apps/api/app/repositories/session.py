from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.session import UserSession
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    model = UserSession

    def get_by_token_hash(self, token_hash: str) -> UserSession | None:
        stmt = select(UserSession).where(UserSession.token_hash == token_hash)
        return self.session.scalars(stmt).first()

    def list_active_for_user(self, user_id: uuid.UUID) -> list[UserSession]:
        stmt = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.revoked_at.is_(None)
        )
        return list(self.session.scalars(stmt).all())

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.source_playlist import SourcePlaylist
from app.repositories.base import TenantScopedRepository


class SourcePlaylistRepository(TenantScopedRepository[SourcePlaylist]):
    model = SourcePlaylist

    def get_by_external_id(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, external_playlist_id: str
    ) -> SourcePlaylist | None:
        stmt = select(SourcePlaylist).where(
            SourcePlaylist.organization_id == organization_id,
            SourcePlaylist.channel_id == channel_id,
            SourcePlaylist.external_playlist_id == external_playlist_id,
        )
        return self.session.scalars(stmt).first()

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 200
    ) -> list[SourcePlaylist]:
        stmt = (
            select(SourcePlaylist)
            .where(
                SourcePlaylist.organization_id == organization_id,
                SourcePlaylist.channel_id == channel_id,
            )
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

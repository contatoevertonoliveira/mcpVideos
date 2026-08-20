from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.channel_dna_version import ChannelDNAVersion
from app.models.enums import ChannelDNAStatus
from app.repositories.base import TenantScopedRepository


class ChannelDNAVersionRepository(TenantScopedRepository[ChannelDNAVersion]):
    model = ChannelDNAVersion

    def get_active(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> ChannelDNAVersion | None:
        stmt = select(ChannelDNAVersion).where(
            ChannelDNAVersion.organization_id == organization_id,
            ChannelDNAVersion.channel_id == channel_id,
            ChannelDNAVersion.status == ChannelDNAStatus.ACTIVE,
        )
        return self.session.scalars(stmt).first()

    def get_latest_version_number(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID
    ) -> int:
        stmt = (
            select(ChannelDNAVersion.version)
            .where(
                ChannelDNAVersion.organization_id == organization_id,
                ChannelDNAVersion.channel_id == channel_id,
            )
            .order_by(ChannelDNAVersion.version.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first() or 0

    def list_by_channel(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 50
    ) -> list[ChannelDNAVersion]:
        stmt = (
            select(ChannelDNAVersion)
            .where(
                ChannelDNAVersion.organization_id == organization_id,
                ChannelDNAVersion.channel_id == channel_id,
            )
            .order_by(ChannelDNAVersion.version.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

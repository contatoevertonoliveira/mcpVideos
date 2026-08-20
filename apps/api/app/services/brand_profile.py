from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.brand_profile import BrandProfile
from app.repositories.brand_profile import BrandProfileRepository
from app.repositories.channel import ChannelRepository
from app.schemas.brand_profile import BrandProfileWrite


class BrandProfileService:
    """Documento 03, secao 18. User-defined brand identity (colors, tone
    of voice, prohibited elements) - not agent-inferred, so this is plain
    CRUD, unlike Channel/Audience profile."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.channels = ChannelRepository(session)
        self.brand_profiles = BrandProfileRepository(session)

    def get(self, channel_id: uuid.UUID, *, organization_id: uuid.UUID) -> BrandProfile | None:
        return self.brand_profiles.get_by_channel(channel_id, organization_id=organization_id)

    def upsert(
        self, channel_id: uuid.UUID, *, organization_id: uuid.UUID, payload: BrandProfileWrite
    ) -> BrandProfile:
        if self.channels.get_by_id(channel_id, organization_id=organization_id) is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        profile = self.brand_profiles.get_by_channel(channel_id, organization_id=organization_id)
        if profile is None:
            profile = BrandProfile(organization_id=organization_id, channel_id=channel_id)
            self.session.add(profile)

        profile.name = payload.name
        profile.colors_json = payload.colors_json
        profile.typography_json = payload.typography_json
        profile.visual_style_json = payload.visual_style_json
        profile.tone_of_voice_json = payload.tone_of_voice_json
        profile.rules_json = payload.rules_json
        profile.prohibited_elements_json = payload.prohibited_elements_json
        self.session.flush()
        return profile

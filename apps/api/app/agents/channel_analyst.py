"""Channel Analyst agent (Documento 05, secao 6)."""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.agents.runtime import run_structured_agent
from app.agents.schemas import ChannelAnalystOutput
from app.gateways.llm import LLMGateway
from app.models.channel import Channel
from app.models.channel_profile import ChannelProfile
from app.models.source_playlist import SourcePlaylist
from app.models.source_video import SourceVideo

AGENT_ID = "channel_analyst"
VERSION = "v1"


def _build_user_prompt(
    *,
    channel: Channel,
    videos: list[SourceVideo],
    playlists: list[SourcePlaylist],
    existing_profile: ChannelProfile | None,
) -> str:
    payload = {
        "channel": {
            "name": channel.name,
            "handle": channel.handle,
            "description": channel.description,
            "language": channel.language,
            "country": channel.country,
        },
        "videos": [
            {
                "title": video.title,
                "video_type": video.video_type.value,
                "duration_seconds": video.duration_seconds,
                "published_at": video.published_at.isoformat() if video.published_at else None,
            }
            for video in videos
        ],
        "playlists": [
            {"title": playlist.title, "item_count": playlist.item_count} for playlist in playlists
        ],
        "existing_channel_profile": (
            {
                "primary_language": existing_profile.primary_language,
                "primary_category": existing_profile.primary_category,
                "content_summary": existing_profile.content_summary,
            }
            if existing_profile
            else None
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_channel_analyst(
    gateway: LLMGateway,
    *,
    channel: Channel,
    videos: list[SourceVideo],
    playlists: list[SourcePlaylist],
    existing_profile: ChannelProfile | None,
    session: Session,
    organization_id: uuid.UUID,
    channel_id: uuid.UUID | None = None,
    workflow_run_id: uuid.UUID | None = None,
    workflow_step_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
) -> ChannelAnalystOutput:
    user_prompt = _build_user_prompt(
        channel=channel, videos=videos, playlists=playlists, existing_profile=existing_profile
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=ChannelAnalystOutput,
        session=session,
        organization_id=organization_id,
        channel_id=channel_id,
        workflow_run_id=workflow_run_id,
        workflow_step_id=workflow_step_id,
        correlation_id=correlation_id,
    )

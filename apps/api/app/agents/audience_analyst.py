"""Audience Analyst agent (Documento 05, secao 7)."""

from __future__ import annotations

import json
import uuid

from app.agents.runtime import run_structured_agent
from app.agents.schemas import AudienceAnalystOutput
from app.gateways.llm import LLMGateway
from app.models.audience_profile import AudienceProfile
from app.models.channel import Channel
from app.models.source_video import SourceVideo
from app.models.source_video_metric import SourceVideoMetric

AGENT_ID = "audience_analyst"
VERSION = "v1"


def _video_with_metrics(
    video: SourceVideo, latest_metrics_by_video_id: dict[uuid.UUID, SourceVideoMetric]
) -> dict[str, object]:
    metric = latest_metrics_by_video_id.get(video.id)
    return {
        "title": video.title,
        "video_type": video.video_type.value,
        "views": metric.views if metric else None,
        "likes": metric.likes if metric else None,
        "comments": metric.comments if metric else None,
    }


def _build_user_prompt(
    *,
    channel: Channel,
    videos: list[SourceVideo],
    latest_metrics_by_video_id: dict[uuid.UUID, SourceVideoMetric],
    existing_profile: AudienceProfile | None,
) -> str:
    payload = {
        "channel": {
            "name": channel.name,
            "description": channel.description,
            "language": channel.language,
            "country": channel.country,
        },
        "videos": [_video_with_metrics(video, latest_metrics_by_video_id) for video in videos],
        "existing_audience_profile": existing_profile.profile_json if existing_profile else None,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def run_audience_analyst(
    gateway: LLMGateway,
    *,
    channel: Channel,
    videos: list[SourceVideo],
    latest_metrics_by_video_id: dict[uuid.UUID, SourceVideoMetric],
    existing_profile: AudienceProfile | None,
) -> AudienceAnalystOutput:
    user_prompt = _build_user_prompt(
        channel=channel,
        videos=videos,
        latest_metrics_by_video_id=latest_metrics_by_video_id,
        existing_profile=existing_profile,
    )
    return await run_structured_agent(
        gateway,
        agent_id=AGENT_ID,
        version=VERSION,
        user_prompt=user_prompt,
        response_model=AudienceAnalystOutput,
    )

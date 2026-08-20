"""YouTubeGateway (Documento 02, secao 47; Documento 06 gateway pattern).

Services never call Google's APIs directly - only through this
abstraction, so nothing outside this module needs to know whether it is
talking to the real Google OAuth/Data API or a fake for local dev/tests
(Documento 02, secao 71 - "FakeYouTubeGateway").
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx

from app.core.config import Settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
YOUTUBE_PLAYLISTS_URL = "https://www.googleapis.com/youtube/v3/playlists"
YOUTUBE_PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

YOUTUBE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]

# Safety caps for Fase 05 (MVP import) - full pagination with quota/cost
# tracking (Documento 06) is a later concern, not this phase's scope.
MAX_PLAYLIST_PAGES = 5
MAX_VIDEO_IDS_PER_BATCH = 50

_ISO8601_DURATION_RE = re.compile(
    r"^P(?:(?P<days>\d+)D)?"
    r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
)


def parse_iso8601_duration(value: str) -> int | None:
    """Parses YouTube's contentDetails.duration (e.g. "PT4M13S") into
    seconds. Returns None for live streams, which report "P0D"/empty."""
    if value == "P0D":
        return None
    match = _ISO8601_DURATION_RE.match(value)
    if not match:
        return None
    parts = match.groupdict()
    if not any(parts.values()):
        return None
    days = int(parts["days"] or 0)
    hours = int(parts["hours"] or 0)
    minutes = int(parts["minutes"] or 0)
    seconds = int(parts["seconds"] or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


@dataclass
class OAuthTokenSet:
    access_token: str
    refresh_token: str
    expires_at: datetime
    scopes: list[str] = field(default_factory=list)


@dataclass
class YouTubeChannelInfo:
    external_channel_id: str
    title: str
    description: str | None
    thumbnail_url: str | None
    custom_url: str | None


@dataclass
class YouTubePlaylistInfo:
    external_playlist_id: str
    title: str
    description: str | None
    item_count: int
    raw: dict = field(default_factory=dict)


@dataclass
class YouTubeVideoInfo:
    external_video_id: str
    title: str
    description: str | None
    duration_seconds: int | None
    published_at: datetime | None
    privacy_status: str | None
    thumbnail_url: str | None
    is_live: bool
    raw: dict = field(default_factory=dict)


@dataclass
class YouTubeVideoMetrics:
    external_video_id: str
    views: int | None
    likes: int | None
    comments: int | None
    raw: dict = field(default_factory=dict)


class YouTubeGateway(ABC):
    @abstractmethod
    def get_authorization_url(self, state: str) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> OAuthTokenSet: ...

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenSet: ...

    @abstractmethod
    async def get_channel_info(self, access_token: str) -> YouTubeChannelInfo: ...

    @abstractmethod
    async def revoke_token(self, token: str) -> None: ...

    @abstractmethod
    async def list_playlists(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubePlaylistInfo]: ...

    @abstractmethod
    async def list_videos(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubeVideoInfo]: ...

    @abstractmethod
    async def get_video_metrics(
        self, access_token: str, external_video_ids: list[str]
    ) -> list[YouTubeVideoMetrics]: ...


class GoogleYouTubeGateway(YouTubeGateway):
    """Talks to the real Google OAuth2 + YouTube Data API v3 endpoints."""

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.google_client_id
        self._client_secret = settings.google_client_secret
        self._redirect_uri = settings.google_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(YOUTUBE_OAUTH_SCOPES),
            "state": state,
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> OAuthTokenSet:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            payload = response.json()
        return self._token_set_from_payload(payload)

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenSet:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            payload = response.json()
        payload.setdefault("refresh_token", refresh_token)
        return self._token_set_from_payload(payload)

    async def get_channel_info(self, access_token: str) -> YouTubeChannelInfo:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                YOUTUBE_CHANNELS_URL,
                params={"part": "snippet", "mine": "true"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            payload = response.json()

        items = payload.get("items", [])
        if not items:
            raise ValueError("No YouTube channel found for this Google account")
        snippet = items[0]["snippet"]
        return YouTubeChannelInfo(
            external_channel_id=items[0]["id"],
            title=snippet.get("title", ""),
            description=snippet.get("description"),
            thumbnail_url=(snippet.get("thumbnails", {}).get("default") or {}).get("url"),
            custom_url=snippet.get("customUrl"),
        )

    async def revoke_token(self, token: str) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(GOOGLE_REVOKE_URL, data={"token": token})

    async def list_playlists(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubePlaylistInfo]:
        headers = {"Authorization": f"Bearer {access_token}"}
        playlists: list[YouTubePlaylistInfo] = []
        page_token: str | None = None

        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(MAX_PLAYLIST_PAGES):
                params: dict[str, str | int] = {
                    "part": "snippet,contentDetails",
                    "channelId": channel_external_id,
                    "maxResults": 50,
                }
                if page_token:
                    params["pageToken"] = page_token
                response = await client.get(YOUTUBE_PLAYLISTS_URL, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()

                for item in payload.get("items", []):
                    snippet = item.get("snippet", {})
                    playlists.append(
                        YouTubePlaylistInfo(
                            external_playlist_id=item["id"],
                            title=snippet.get("title", ""),
                            description=snippet.get("description"),
                            item_count=item.get("contentDetails", {}).get("itemCount", 0),
                            raw=item,
                        )
                    )
                page_token = payload.get("nextPageToken")
                if not page_token:
                    break
        return playlists

    async def _get_uploads_playlist_id(
        self, client: httpx.AsyncClient, headers: dict, channel_external_id: str
    ) -> str | None:
        response = await client.get(
            YOUTUBE_CHANNELS_URL,
            params={"part": "contentDetails", "id": channel_external_id},
            headers=headers,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        if not items:
            return None
        return items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

    async def list_videos(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubeVideoInfo]:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            uploads_playlist_id = await self._get_uploads_playlist_id(
                client, headers, channel_external_id
            )
            if uploads_playlist_id is None:
                return []

            video_ids: list[str] = []
            page_token: str | None = None
            for _ in range(MAX_PLAYLIST_PAGES):
                params: dict[str, str | int] = {
                    "part": "contentDetails",
                    "playlistId": uploads_playlist_id,
                    "maxResults": 50,
                }
                if page_token:
                    params["pageToken"] = page_token
                response = await client.get(
                    YOUTUBE_PLAYLIST_ITEMS_URL, params=params, headers=headers
                )
                response.raise_for_status()
                payload = response.json()
                video_ids.extend(
                    item["contentDetails"]["videoId"] for item in payload.get("items", [])
                )
                page_token = payload.get("nextPageToken")
                if not page_token:
                    break

            videos: list[YouTubeVideoInfo] = []
            for batch_start in range(0, len(video_ids), MAX_VIDEO_IDS_PER_BATCH):
                batch = video_ids[batch_start : batch_start + MAX_VIDEO_IDS_PER_BATCH]
                response = await client.get(
                    YOUTUBE_VIDEOS_URL,
                    params={"part": "snippet,contentDetails,status", "id": ",".join(batch)},
                    headers=headers,
                )
                response.raise_for_status()
                for item in response.json().get("items", []):
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    status = item.get("status", {})
                    duration = content_details.get("duration")
                    published_at = snippet.get("publishedAt")
                    videos.append(
                        YouTubeVideoInfo(
                            external_video_id=item["id"],
                            title=snippet.get("title", ""),
                            description=snippet.get("description"),
                            duration_seconds=parse_iso8601_duration(duration) if duration else None,
                            published_at=(
                                datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                                if published_at
                                else None
                            ),
                            privacy_status=status.get("privacyStatus"),
                            thumbnail_url=(snippet.get("thumbnails", {}).get("default") or {}).get(
                                "url"
                            ),
                            is_live=snippet.get("liveBroadcastContent", "none") != "none",
                            raw=item,
                        )
                    )
        return videos

    async def get_video_metrics(
        self, access_token: str, external_video_ids: list[str]
    ) -> list[YouTubeVideoMetrics]:
        if not external_video_ids:
            return []
        headers = {"Authorization": f"Bearer {access_token}"}
        metrics: list[YouTubeVideoMetrics] = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for batch_start in range(0, len(external_video_ids), MAX_VIDEO_IDS_PER_BATCH):
                batch = external_video_ids[batch_start : batch_start + MAX_VIDEO_IDS_PER_BATCH]
                response = await client.get(
                    YOUTUBE_VIDEOS_URL,
                    params={"part": "statistics", "id": ",".join(batch)},
                    headers=headers,
                )
                response.raise_for_status()
                for item in response.json().get("items", []):
                    stats = item.get("statistics", {})
                    metrics.append(
                        YouTubeVideoMetrics(
                            external_video_id=item["id"],
                            views=int(stats["viewCount"]) if "viewCount" in stats else None,
                            likes=int(stats["likeCount"]) if "likeCount" in stats else None,
                            comments=int(stats["commentCount"])
                            if "commentCount" in stats
                            else None,
                            raw=item,
                        )
                    )
        return metrics

    @staticmethod
    def _token_set_from_payload(payload: dict) -> OAuthTokenSet:
        expires_in = int(payload.get("expires_in", 3600))
        return OAuthTokenSet(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token", ""),
            expires_at=datetime.now(UTC) + timedelta(seconds=expires_in),
            scopes=payload.get("scope", "").split(),
        )


class FakeYouTubeGateway(YouTubeGateway):
    """Deterministic, network-free double for local dev and tests
    (Documento 02, secao 71). Enabled while YOUTUBE_FAKE_GATEWAY=true.

    The "authorization url" points straight at our own OAuth callback route
    (with a fake ``code`` already attached) instead of a fake external
    domain, so the whole connect flow stays genuinely clickable end-to-end
    in a browser without a real Google account.
    """

    def __init__(self, redirect_uri: str | None = None) -> None:
        self._redirect_uri = redirect_uri or "http://localhost:3000/oauth/youtube/callback"

    def get_authorization_url(self, state: str) -> str:
        fake_code = f"fake-code-{uuid.uuid4().hex[:12]}"
        return f"{self._redirect_uri}?code={fake_code}&state={state}"

    async def exchange_code(self, code: str) -> OAuthTokenSet:
        return OAuthTokenSet(
            access_token=f"fake-access-{code}",
            refresh_token=f"fake-refresh-{code}",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            scopes=YOUTUBE_OAUTH_SCOPES,
        )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenSet:
        return OAuthTokenSet(
            access_token=f"fake-access-refreshed-{uuid.uuid4().hex[:8]}",
            refresh_token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            scopes=YOUTUBE_OAUTH_SCOPES,
        )

    async def get_channel_info(self, access_token: str) -> YouTubeChannelInfo:
        # Deliberately NOT derived from access_token: a real Google account
        # keeps the same YouTube channel identity across separate OAuth
        # grants (fresh access token each time), so reconnecting must
        # resolve to the same external_channel_id every time too - that's
        # exactly what exercises the upsert-not-duplicate path.
        return YouTubeChannelInfo(
            external_channel_id="UCfakegateway00000000001",
            title="Canal de Teste (Fake Gateway)",
            description="Canal gerado pelo FakeYouTubeGateway para desenvolvimento/testes.",
            thumbnail_url="https://placehold.co/88x88",
            custom_url=None,
        )

    async def revoke_token(self, token: str) -> None:
        return None

    async def list_playlists(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubePlaylistInfo]:
        # Deterministic by channel_external_id (not access_token) for the
        # same reason as get_channel_info: re-sync must resolve to the same
        # playlist identity, never a new one.
        return [
            YouTubePlaylistInfo(
                external_playlist_id=f"PL-{channel_external_id}-uploads",
                title="Uploads (Fake)",
                description="Playlist gerada pelo FakeYouTubeGateway.",
                item_count=len(_FAKE_VIDEOS),
            )
        ]

    async def list_videos(
        self, access_token: str, channel_external_id: str
    ) -> list[YouTubeVideoInfo]:
        return [
            YouTubeVideoInfo(
                external_video_id=f"fake-video-{channel_external_id}-{i}",
                title=f"Video de Teste {i}",
                description="Video gerado pelo FakeYouTubeGateway para desenvolvimento/testes.",
                duration_seconds=duration_seconds,
                published_at=datetime(2026, 1, i, tzinfo=UTC),
                privacy_status="public",
                thumbnail_url="https://placehold.co/320x180",
                is_live=False,
            )
            for i, duration_seconds in enumerate(_FAKE_VIDEOS, start=1)
        ]

    async def get_video_metrics(
        self, access_token: str, external_video_ids: list[str]
    ) -> list[YouTubeVideoMetrics]:
        return [
            YouTubeVideoMetrics(
                external_video_id=video_id,
                views=1000 * (index + 1),
                likes=100 * (index + 1),
                comments=10 * (index + 1),
            )
            for index, video_id in enumerate(external_video_ids)
        ]


# (index, duration_seconds) - 2 shorts (<=60s) and 3 long-form videos, so
# tests/fixtures can exercise SourceVideoType classification deterministically.
_FAKE_VIDEOS = [45, 58, 320, 610, 902]


def get_youtube_gateway(settings: Settings) -> YouTubeGateway:
    if settings.youtube_fake_gateway:
        return FakeYouTubeGateway(redirect_uri=settings.google_redirect_uri)
    return GoogleYouTubeGateway(settings)

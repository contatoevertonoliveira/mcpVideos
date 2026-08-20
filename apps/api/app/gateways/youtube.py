"""YouTubeGateway (Documento 02, secao 47; Documento 06 gateway pattern).

Services never call Google's APIs directly - only through this
abstraction, so nothing outside this module needs to know whether it is
talking to the real Google OAuth/Data API or a fake for local dev/tests
(Documento 02, secao 71 - "FakeYouTubeGateway").
"""

from __future__ import annotations

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

YOUTUBE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]


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


def get_youtube_gateway(settings: Settings) -> YouTubeGateway:
    if settings.youtube_fake_gateway:
        return FakeYouTubeGateway(redirect_uri=settings.google_redirect_uri)
    return GoogleYouTubeGateway(settings)

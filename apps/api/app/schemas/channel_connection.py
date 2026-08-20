from __future__ import annotations

from pydantic import BaseModel


class ConnectChannelResponse(BaseModel):
    authorization_url: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

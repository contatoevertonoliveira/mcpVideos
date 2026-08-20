"""Signed, self-contained OAuth "state" tokens (CSRF protection for the
Google OAuth flow, Documento 09 general secret-handling principles).

Stdlib-only HMAC signing - no server-side storage needed to validate a
callback, and no new dependency for a narrow, well-defined need.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.core.config import get_settings


class InvalidStateError(Exception):
    pass


def _signing_key() -> bytes:
    return get_settings().secret_key.encode("utf-8")


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_state(payload: dict[str, Any], max_age_seconds: int = 600) -> str:
    body = {**payload, "exp": int(time.time()) + max_age_seconds}
    body_bytes = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(_signing_key(), body_bytes, hashlib.sha256).digest()
    return f"{_b64encode(body_bytes)}.{_b64encode(signature)}"


def verify_state(state: str) -> dict[str, Any]:
    try:
        body_part, signature_part = state.split(".", 1)
        body_bytes = _b64decode(body_part)
        signature = _b64decode(signature_part)
    except Exception as exc:
        # Untrusted input: any parse failure just means "not a valid state".
        raise InvalidStateError("Malformed state") from exc

    expected_signature = hmac.new(_signing_key(), body_bytes, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_signature):
        raise InvalidStateError("Signature mismatch")

    body: dict[str, Any] = json.loads(body_bytes)
    if body.get("exp", 0) < time.time():
        raise InvalidStateError("State expired")

    return body

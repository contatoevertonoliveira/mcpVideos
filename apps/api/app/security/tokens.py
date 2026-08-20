"""Opaque session tokens.

Unlike passwords, session tokens already have high entropy, so a fast
deterministic hash (sha256) is the standard, appropriate choice for
storage - never store the raw token (Documento 09, secao 27).
"""

import hashlib
import secrets


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

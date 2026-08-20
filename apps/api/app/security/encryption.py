"""Symmetric encryption for OAuth tokens at rest (Documento 09, secao 22-23).

The key comes from an environment secret (``TOKEN_ENCRYPTION_KEY``), never
from the database. Fernet gives us authenticated encryption plus a bundled
timestamp - suitable for the "small opaque secret" shape of an OAuth token.
"""

from functools import lru_cache

from cryptography.fernet import Fernet

from app.core.config import get_settings


@lru_cache
def _fernet() -> Fernet:
    return Fernet(get_settings().token_encryption_key.encode("utf-8"))


def encrypt_token(plain_token: str) -> str:
    return _fernet().encrypt(plain_token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    return _fernet().decrypt(encrypted_token.encode("utf-8")).decode("utf-8")

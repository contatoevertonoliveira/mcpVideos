"""Login brute-force protection (Documento 09, secao 140).

Redis is used only as a counter/cache here, never as source of truth for
business state (Documento 02, secao 21).
"""

from __future__ import annotations

import redis

from app.core.exceptions import RateLimitError

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60


class LoginRateLimiter:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    def _key(self, identifier: str) -> str:
        return f"login_attempts:{identifier.lower()}"

    def check(self, identifier: str) -> None:
        attempts = self.redis.get(self._key(identifier))
        if attempts is not None and int(attempts) >= MAX_ATTEMPTS:
            raise RateLimitError(
                "Too many login attempts. Try again later.", code="LOGIN_RATE_LIMITED"
            )

    def record_failure(self, identifier: str) -> None:
        key = self._key(identifier)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, WINDOW_SECONDS)
        pipe.execute()

    def reset(self, identifier: str) -> None:
        self.redis.delete(self._key(identifier))

import pytest

from app.core.exceptions import RateLimitError
from app.security.rate_limit import MAX_ATTEMPTS, LoginRateLimiter


def test_check_allows_under_threshold(redis_client):
    limiter = LoginRateLimiter(redis_client)

    for _ in range(MAX_ATTEMPTS - 1):
        limiter.check("someone@example.com")
        limiter.record_failure("someone@example.com")

    limiter.check("someone@example.com")  # still under threshold, no raise


def test_check_blocks_after_max_attempts(redis_client):
    limiter = LoginRateLimiter(redis_client)

    for _ in range(MAX_ATTEMPTS):
        limiter.record_failure("someone@example.com")

    with pytest.raises(RateLimitError):
        limiter.check("someone@example.com")


def test_reset_clears_attempts(redis_client):
    limiter = LoginRateLimiter(redis_client)
    for _ in range(MAX_ATTEMPTS):
        limiter.record_failure("someone@example.com")

    limiter.reset("someone@example.com")

    limiter.check("someone@example.com")  # no raise


def test_identifier_is_case_insensitive(redis_client):
    limiter = LoginRateLimiter(redis_client)
    for _ in range(MAX_ATTEMPTS):
        limiter.record_failure("Someone@Example.com")

    with pytest.raises(RateLimitError):
        limiter.check("someone@example.com")

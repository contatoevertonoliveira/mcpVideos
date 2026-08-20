import os
from unittest.mock import MagicMock

import pytest
import redis as redis_lib
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.redis import get_redis_client
from app.db.session import get_db
from app.main import app
from app.tasks import channel_sync as channel_sync_tasks

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos_test",
)
TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")


@pytest.fixture
def anyio_backend() -> str:
    """Runs @pytest.mark.anyio async tests (Fase 04's YouTubeGateway
    coroutines) on asyncio only - no need for trio in this project."""
    return "asyncio"


@pytest.fixture(autouse=True)
def no_celery_dispatch(monkeypatch):
    """Never enqueue real Celery tasks from tests: DB writes made in a test
    transaction that gets rolled back must never reach a worker consuming
    the real Redis broker. The task body itself is tested directly (with
    its own db_session), never through .delay()."""
    monkeypatch.setattr(channel_sync_tasks.run_channel_sync_task, "delay", MagicMock())


@pytest.fixture(scope="session")
def db_engine():
    """Assumes the schema is already migrated (`alembic upgrade head`
    against TEST_DATABASE_URL) - tests never create/drop tables themselves."""
    engine = create_engine(TEST_DATABASE_URL, future=True)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Wraps each test in an outer transaction that is always rolled back,
    so tests never leak data into each other or require manual cleanup.
    Code under test must never call session.commit() - only flush()."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        # A mid-test error (e.g. a request that hits an unhandled DB error)
        # may already have ended this transaction via session.rollback().
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def redis_client():
    """A separate Redis DB index than the app's defaults, flushed before
    each test so login-rate-limit counters never leak between tests."""
    client = redis_lib.from_url(TEST_REDIS_URL, decode_responses=True)
    client.flushdb()
    yield client
    client.flushdb()


@pytest.fixture
def client(db_session, redis_client) -> TestClient:
    """TestClient wired to the same per-test DB transaction and a scratch
    Redis DB, so HTTP-level tests share state correctly with service-layer
    assertions and never touch real dev data."""

    def _get_db_override():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_redis_client] = lambda: redis_client
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

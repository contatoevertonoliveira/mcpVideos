import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos_test",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


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
        transaction.rollback()
        connection.close()

import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.tasks import channel_sync as channel_sync_tasks


def test_mark_running_with_retry_recovers_from_transient_not_found(monkeypatch):
    """Reproduces the real race found via manual E2E testing: the Celery
    worker can pick up a task before the API request that created the Job
    row has committed. The retry must absorb a couple of NotFoundError
    attempts and still succeed once the row becomes visible."""
    calls = {"n": 0}

    def fake_mark_running(self, job_uuid, *, organization_id):
        calls["n"] += 1
        if calls["n"] < 3:
            raise NotFoundError("Job not found", code="JOB_NOT_FOUND")

    monkeypatch.setattr(channel_sync_tasks.JobService, "mark_running", fake_mark_running)
    monkeypatch.setattr(channel_sync_tasks.time, "sleep", lambda _seconds: None)

    channel_sync_tasks._mark_running_with_retry(uuid.uuid4(), uuid.uuid4())

    assert calls["n"] == 3


def test_mark_running_with_retry_gives_up_after_max_attempts(monkeypatch):
    calls = {"n": 0}

    def always_not_found(self, job_uuid, *, organization_id):
        calls["n"] += 1
        raise NotFoundError("Job not found", code="JOB_NOT_FOUND")

    monkeypatch.setattr(channel_sync_tasks.JobService, "mark_running", always_not_found)
    monkeypatch.setattr(channel_sync_tasks.time, "sleep", lambda _seconds: None)

    with pytest.raises(NotFoundError):
        channel_sync_tasks._mark_running_with_retry(uuid.uuid4(), uuid.uuid4())

    assert calls["n"] == channel_sync_tasks._JOB_VISIBILITY_RETRIES

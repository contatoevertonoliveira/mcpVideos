import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.tasks import _job_utils


def test_mark_running_with_retry_recovers_from_transient_not_found(monkeypatch):
    """Reproduces the real race found via manual E2E testing (Fase 05): the
    Celery worker can pick up a task before the API request that created
    the Job row has committed. The retry must absorb a couple of
    NotFoundError attempts and still succeed once the row becomes
    visible. Shared by every task that dispatches via a Job row (channel
    sync, channel intelligence, ...)."""
    calls = {"n": 0}

    def fake_mark_running(self, job_uuid, *, organization_id):
        calls["n"] += 1
        if calls["n"] < 3:
            raise NotFoundError("Job not found", code="JOB_NOT_FOUND")

    monkeypatch.setattr(_job_utils.JobService, "mark_running", fake_mark_running)
    monkeypatch.setattr(_job_utils.time, "sleep", lambda _seconds: None)

    _job_utils.mark_running_with_retry(uuid.uuid4(), uuid.uuid4())

    assert calls["n"] == 3


def test_mark_running_with_retry_gives_up_after_max_attempts(monkeypatch):
    calls = {"n": 0}

    def always_not_found(self, job_uuid, *, organization_id):
        calls["n"] += 1
        raise NotFoundError("Job not found", code="JOB_NOT_FOUND")

    monkeypatch.setattr(_job_utils.JobService, "mark_running", always_not_found)
    monkeypatch.setattr(_job_utils.time, "sleep", lambda _seconds: None)

    with pytest.raises(NotFoundError):
        _job_utils.mark_running_with_retry(uuid.uuid4(), uuid.uuid4())

    assert calls["n"] == _job_utils._JOB_VISIBILITY_RETRIES

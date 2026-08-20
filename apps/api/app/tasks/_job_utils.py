"""Shared plumbing for Celery tasks that track their progress via the
generic ``Job`` entity (Documento 02, secao 20-23).

The API request that creates a Job row and the ``.delay()`` call that
wakes a worker up are not atomic: Celery/Redis can deliver the message to
a worker faster than the API's own transaction commits. This was found as
a real, reproducible bug in Fase 05 (channel.sync) via manual E2E testing
against the Docker stack - a short bounded retry on "not found yet" is the
pragmatic fix (a real transactional outbox is more machinery than this
project needs at this stage). Reused here for channel.intelligence since
the exact same race applies to any task dispatched this way.
"""

from __future__ import annotations

import time
import uuid

from app.core.exceptions import NotFoundError
from app.db.session import db_session_scope
from app.services.job import JobService

_JOB_VISIBILITY_RETRIES = 5
_JOB_VISIBILITY_DELAY_SECONDS = 0.3


def mark_running_with_retry(job_uuid: uuid.UUID, org_uuid: uuid.UUID) -> None:
    for attempt in range(_JOB_VISIBILITY_RETRIES):
        try:
            with db_session_scope() as db:
                JobService(db).mark_running(job_uuid, organization_id=org_uuid)
            return
        except NotFoundError:
            if attempt == _JOB_VISIBILITY_RETRIES - 1:
                raise
            time.sleep(_JOB_VISIBILITY_DELAY_SECONDS)

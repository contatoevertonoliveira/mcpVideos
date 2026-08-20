"""Documento 02, secao 20-23: primeira task Celery real do projeto (as
anteriores eram apenas ``foundation.ping``). Segue a regra fundamental de
jobs - o estado da sincronizacao vive em ``channel_sync_runs``/``jobs`` no
Postgres, o Celery apenas executa e pode ser reiniciado sem perda de
informacao.

A infraestrutura completa de workflows versionados (``workflow_runs``,
retry/resume/pause) chega na Fase 11 - aqui ``channel.sync.v1`` (Documento
04, secao 16) e apenas o nome logico do fluxo, implementado como uma unica
task Celery com retry simples.
"""

from __future__ import annotations

import asyncio
import time
import uuid

import httpx
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.exceptions import NotFoundError
from app.db.session import db_session_scope
from app.models.enums import SyncType
from app.models.job import Job
from app.observability.logging import get_logger
from app.services.channel_sync import ChannelSyncService
from app.services.job import JobService

logger = get_logger(__name__)

# The API request that creates the Job row and the .delay() call that wakes
# this task up are not atomic: Celery/Redis can deliver the message to a
# worker faster than the API's own transaction commits (Documento 02, secao
# 21 assumes the DB write happens first, but nothing enforces that
# ordering here). A short bounded retry on "not found yet" is the pragmatic
# fix - a real transactional outbox is more machinery than this phase
# needs.
_JOB_VISIBILITY_RETRIES = 5
_JOB_VISIBILITY_DELAY_SECONDS = 0.3


def _mark_running_with_retry(job_uuid: uuid.UUID, org_uuid: uuid.UUID) -> None:
    for attempt in range(_JOB_VISIBILITY_RETRIES):
        try:
            with db_session_scope() as db:
                JobService(db).mark_running(job_uuid, organization_id=org_uuid)
            return
        except NotFoundError:
            if attempt == _JOB_VISIBILITY_RETRIES - 1:
                raise
            time.sleep(_JOB_VISIBILITY_DELAY_SECONDS)


def dispatch_channel_sync(
    session: Session,
    *,
    channel_id: uuid.UUID,
    organization_id: uuid.UUID,
    sync_type: SyncType,
    correlation_id: uuid.UUID | None = None,
) -> Job:
    """Creates the user-visible Job row and enqueues the Celery task.

    Uses the caller's own session/transaction to create the Job (so it
    commits/rolls back together with whatever triggered the sync, e.g. the
    OAuth connect flow), then hands off to Celery for the actual work.
    """
    job = JobService(session).create_job(
        organization_id=organization_id,
        job_type="channel.sync",
        resource_type="channel",
        resource_id=channel_id,
        correlation_id=correlation_id,
    )
    run_channel_sync_task.delay(
        job_id=str(job.id),
        channel_id=str(channel_id),
        organization_id=str(organization_id),
        sync_type=sync_type.value,
        correlation_id=str(job.correlation_id),
    )
    return job


@celery_app.task(
    name="channel.sync",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_channel_sync_task(
    self,
    *,
    job_id: str,
    channel_id: str,
    organization_id: str,
    sync_type: str,
    correlation_id: str,
) -> None:
    org_uuid = uuid.UUID(organization_id)
    job_uuid = uuid.UUID(job_id)

    _mark_running_with_retry(job_uuid, org_uuid)

    try:
        asyncio.run(_execute(channel_id, organization_id, sync_type, correlation_id))
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="CHANNEL_SYNC_TRANSIENT_ERROR",
                error_message=str(exc)[:2000],
            )
        raise self.retry(exc=exc) from exc
    except Exception as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="CHANNEL_SYNC_FAILED",
                error_message=str(exc)[:2000],
            )
        logger.error("channel_sync_task_failed", channel_id=channel_id, error=str(exc))
        raise
    else:
        with db_session_scope() as db:
            JobService(db).mark_completed(job_uuid, organization_id=org_uuid)


async def _execute(
    channel_id: str, organization_id: str, sync_type: str, correlation_id: str
) -> None:
    with db_session_scope() as db:
        await ChannelSyncService(db).run_sync(
            channel_id=uuid.UUID(channel_id),
            organization_id=uuid.UUID(organization_id),
            sync_type=SyncType(sync_type),
            correlation_id=uuid.UUID(correlation_id),
        )

"""Documento 10 Fase 06: Channel Analyst + Audience Analyst run
asynchronously (Documento 02 sec. 20 lists "analise" as a Celery use
case), tracked the same way as channel.sync (Fase 05) - a Job row for
user-visible progress, real state in Postgres.
"""

from __future__ import annotations

import asyncio
import uuid

import httpx
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.db.session import db_session_scope
from app.models.job import Job
from app.observability.logging import get_logger
from app.services.channel_intelligence import ChannelIntelligenceService
from app.services.job import JobService
from app.tasks._job_utils import mark_running_with_retry

logger = get_logger(__name__)


def dispatch_channel_intelligence(
    session: Session,
    *,
    channel_id: uuid.UUID,
    organization_id: uuid.UUID,
    correlation_id: uuid.UUID | None = None,
) -> Job:
    job = JobService(session).create_job(
        organization_id=organization_id,
        job_type="channel.intelligence",
        resource_type="channel",
        resource_id=channel_id,
        correlation_id=correlation_id,
    )
    run_channel_intelligence_task.delay(
        job_id=str(job.id),
        channel_id=str(channel_id),
        organization_id=str(organization_id),
        correlation_id=str(job.correlation_id),
    )
    return job


@celery_app.task(
    name="channel.intelligence",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_channel_intelligence_task(
    self, *, job_id: str, channel_id: str, organization_id: str, correlation_id: str
) -> None:
    org_uuid = uuid.UUID(organization_id)
    job_uuid = uuid.UUID(job_id)

    mark_running_with_retry(job_uuid, org_uuid)

    try:
        asyncio.run(_execute(channel_id, organization_id))
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="CHANNEL_INTELLIGENCE_TRANSIENT_ERROR",
                error_message=str(exc)[:2000],
            )
        raise self.retry(exc=exc) from exc
    except Exception as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="CHANNEL_INTELLIGENCE_FAILED",
                error_message=str(exc)[:2000],
            )
        logger.error("channel_intelligence_task_failed", channel_id=channel_id, error=str(exc))
        raise
    else:
        with db_session_scope() as db:
            JobService(db).mark_completed(job_uuid, organization_id=org_uuid)


async def _execute(channel_id: str, organization_id: str) -> None:
    with db_session_scope() as db:
        await ChannelIntelligenceService(db).analyze_channel(
            channel_id=uuid.UUID(channel_id), organization_id=uuid.UUID(organization_id)
        )

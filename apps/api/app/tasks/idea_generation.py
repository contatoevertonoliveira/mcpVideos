"""Documento 10 Fase 09: fifth Celery task in the project. Generating
ideas auto-dispatches evaluation for each newly created draft right
after (Documento 10 F09 needs the system to be able to "reject an
irrelevant trend" - an idea nobody ever scores can't be rejected).
Unlike Strategy (Fase 08), scoring/ranking an idea isn't "activating"
anything a human needs to gate - only the idea's own approval is a
human action (app/services/content_idea.py).
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
from app.services.idea_generation import IdeaGenerationService
from app.services.job import JobService
from app.tasks._job_utils import mark_running_with_retry
from app.tasks.opportunity_evaluation import dispatch_opportunity_evaluation

logger = get_logger(__name__)


def dispatch_idea_generation(
    session: Session,
    *,
    channel_id: uuid.UUID,
    organization_id: uuid.UUID,
    correlation_id: uuid.UUID | None = None,
) -> Job:
    job = JobService(session).create_job(
        organization_id=organization_id,
        job_type="idea.generation",
        resource_type="channel",
        resource_id=channel_id,
        correlation_id=correlation_id,
    )
    run_idea_generation_task.delay(
        job_id=str(job.id),
        channel_id=str(channel_id),
        organization_id=str(organization_id),
        correlation_id=str(job.correlation_id),
    )
    return job


@celery_app.task(
    name="idea.generation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_idea_generation_task(
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
                error_code="IDEA_GENERATION_TRANSIENT_ERROR",
                error_message=str(exc)[:2000],
            )
        raise self.retry(exc=exc) from exc
    except Exception as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="IDEA_GENERATION_FAILED",
                error_message=str(exc)[:2000],
            )
        logger.error("idea_generation_task_failed", channel_id=channel_id, error=str(exc))
        raise
    else:
        with db_session_scope() as db:
            JobService(db).mark_completed(job_uuid, organization_id=org_uuid)


async def _execute(channel_id: str, organization_id: str) -> None:
    with db_session_scope() as db:
        ideas = await IdeaGenerationService(db).generate_ideas(
            channel_id=uuid.UUID(channel_id), organization_id=uuid.UUID(organization_id)
        )
        for idea in ideas:
            dispatch_opportunity_evaluation(
                db, idea_id=idea.id, organization_id=uuid.UUID(organization_id)
            )

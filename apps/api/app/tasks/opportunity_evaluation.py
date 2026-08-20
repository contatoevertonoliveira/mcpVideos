"""Documento 10 Fase 09: sixth Celery task in the project."""

from __future__ import annotations

import asyncio
import uuid

import httpx
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.db.session import db_session_scope
from app.models.job import Job
from app.observability.logging import get_logger
from app.services.job import JobService
from app.services.opportunity_evaluation import OpportunityEvaluationService
from app.tasks._job_utils import mark_running_with_retry

logger = get_logger(__name__)


def dispatch_opportunity_evaluation(
    session: Session,
    *,
    idea_id: uuid.UUID,
    organization_id: uuid.UUID,
    correlation_id: uuid.UUID | None = None,
) -> Job:
    job = JobService(session).create_job(
        organization_id=organization_id,
        job_type="opportunity.evaluation",
        resource_type="content_idea",
        resource_id=idea_id,
        correlation_id=correlation_id,
    )
    run_opportunity_evaluation_task.delay(
        job_id=str(job.id),
        idea_id=str(idea_id),
        organization_id=str(organization_id),
        correlation_id=str(job.correlation_id),
    )
    return job


@celery_app.task(
    name="opportunity.evaluation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_opportunity_evaluation_task(
    self, *, job_id: str, idea_id: str, organization_id: str, correlation_id: str
) -> None:
    org_uuid = uuid.UUID(organization_id)
    job_uuid = uuid.UUID(job_id)

    mark_running_with_retry(job_uuid, org_uuid)

    try:
        asyncio.run(_execute(idea_id, organization_id))
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="OPPORTUNITY_EVALUATION_TRANSIENT_ERROR",
                error_message=str(exc)[:2000],
            )
        raise self.retry(exc=exc) from exc
    except Exception as exc:
        with db_session_scope() as db:
            JobService(db).mark_failed(
                job_uuid,
                organization_id=org_uuid,
                error_code="OPPORTUNITY_EVALUATION_FAILED",
                error_message=str(exc)[:2000],
            )
        logger.error("opportunity_evaluation_task_failed", idea_id=idea_id, error=str(exc))
        raise
    else:
        with db_session_scope() as db:
            JobService(db).mark_completed(job_uuid, organization_id=org_uuid)


async def _execute(idea_id: str, organization_id: str) -> None:
    with db_session_scope() as db:
        await OpportunityEvaluationService(db).evaluate_idea(
            idea_id=uuid.UUID(idea_id), organization_id=uuid.UUID(organization_id)
        )

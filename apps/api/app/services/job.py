from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.enums import JobStatus
from app.models.job import Job
from app.repositories.job import JobRepository


class JobService:
    """Documento 04, secao 107-108: toda operacao longa possui um Job;
    o Celery apenas executa, o status real vive aqui no Postgres."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.jobs = JobRepository(session)

    def create_job(
        self,
        *,
        organization_id: uuid.UUID,
        job_type: str,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
    ) -> Job:
        job = Job(
            organization_id=organization_id,
            job_type=job_type,
            resource_type=resource_type,
            resource_id=resource_id,
            correlation_id=correlation_id or uuid.uuid4(),
            status=JobStatus.PENDING,
        )
        return self.jobs.add(job)

    def get_job(self, job_id: uuid.UUID, *, organization_id: uuid.UUID) -> Job:
        job = self.jobs.get_by_id(job_id, organization_id=organization_id)
        if job is None:
            raise NotFoundError("Job not found", code="JOB_NOT_FOUND")
        return job

    def mark_running(self, job_id: uuid.UUID, *, organization_id: uuid.UUID) -> Job:
        job = self.get_job(job_id, organization_id=organization_id)
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        self.session.flush()
        return job

    def mark_completed(self, job_id: uuid.UUID, *, organization_id: uuid.UUID) -> Job:
        job = self.get_job(job_id, organization_id=organization_id)
        job.status = JobStatus.COMPLETED
        job.progress_percent = 100
        job.completed_at = datetime.now(UTC)
        self.session.flush()
        return job

    def mark_failed(
        self, job_id: uuid.UUID, *, organization_id: uuid.UUID, error_code: str, error_message: str
    ) -> Job:
        job = self.get_job(job_id, organization_id=organization_id)
        job.status = JobStatus.FAILED
        job.error_code = error_code
        job.error_message = error_message
        job.completed_at = datetime.now(UTC)
        self.session.flush()
        return job

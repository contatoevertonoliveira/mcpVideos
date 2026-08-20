from app.services.job import JobService
from app.services.organization import OrganizationService


def test_job_lifecycle(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    service = JobService(db_session)

    job = service.create_job(organization_id=org.id, job_type="channel_import")
    assert job.status == "pending"
    assert job.correlation_id is not None

    running = service.mark_running(job.id, organization_id=org.id)
    assert running.status == "running"
    assert running.started_at is not None

    completed = service.mark_completed(job.id, organization_id=org.id)
    assert completed.status == "completed"
    assert completed.progress_percent == 100
    assert completed.completed_at is not None


def test_job_failure(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")
    service = JobService(db_session)
    job = service.create_job(organization_id=org.id, job_type="channel_import")

    failed = service.mark_failed(
        job.id, organization_id=org.id, error_code="PROVIDER_TIMEOUT", error_message="boom"
    )

    assert failed.status == "failed"
    assert failed.error_code == "PROVIDER_TIMEOUT"

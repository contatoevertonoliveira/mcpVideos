import pytest

from app.core.exceptions import DomainError
from app.models.enums import WorkflowRunStatus, WorkflowStepStatus
from app.services.organization import OrganizationService
from app.services.workflow_engine import WorkflowEngineService


def _org(db_session):
    return OrganizationService(db_session).create_organization(name="Acme")


def _engine(db_session) -> WorkflowEngineService:
    return WorkflowEngineService(db_session)


def _started_run(db_session, organization_id, steps=("sync", "intelligence", "dna")):
    engine = _engine(db_session)
    version = engine.ensure_definition(
        slug="test.workflow",
        name="Test Workflow",
        description="A test workflow.",
        steps=list(steps),
    )
    run = engine.start_run(workflow_version=version, organization_id=organization_id)
    return engine, run


def test_ensure_definition_creates_and_reuses(db_session):
    engine = _engine(db_session)

    first = engine.ensure_definition(
        slug="test.workflow", name="Test Workflow", description="desc", steps=["a", "b"]
    )
    second = engine.ensure_definition(
        slug="test.workflow", name="Test Workflow", description="desc", steps=["a", "b"]
    )

    assert first.id == second.id
    assert second.version == 1


def test_ensure_definition_mints_new_version_when_steps_change(db_session):
    engine = _engine(db_session)

    first = engine.ensure_definition(
        slug="test.workflow", name="Test Workflow", description="desc", steps=["a", "b"]
    )
    second = engine.ensure_definition(
        slug="test.workflow", name="Test Workflow", description="desc", steps=["a", "b", "c"]
    )

    assert second.id != first.id
    assert second.version == 2
    assert second.definition_json["steps"] == ["a", "b", "c"]


def test_start_run_creates_pending_steps_and_started_event(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id)

    assert run.status == WorkflowRunStatus.RUNNING
    assert run.current_step == "sync"

    steps = engine.steps.list_by_run(run.id, organization_id=org.id)
    assert [step.step_key for step in steps] == ["sync", "intelligence", "dna"]
    assert all(step.status == WorkflowStepStatus.PENDING for step in steps)

    events = engine.events.list_by_run(run.id, organization_id=org.id)
    assert [event.event_type for event in events] == ["workflow.started"]
    assert events[0].correlation_id == run.correlation_id


def test_mark_step_completed_advances_current_step(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id)

    engine.mark_step_running(run_id=run.id, step_key="sync", organization_id=org.id)
    engine.mark_step_completed(run_id=run.id, step_key="sync", organization_id=org.id)

    db_session.refresh(run)
    assert run.status == WorkflowRunStatus.RUNNING
    assert run.current_step == "intelligence"

    sync_step = engine.steps.get_by_key(
        workflow_run_id=run.id, step_key="sync", organization_id=org.id
    )
    assert sync_step.status == WorkflowStepStatus.COMPLETED
    assert sync_step.attempt_count == 1


def test_mark_step_completed_on_last_step_completes_run(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id, steps=("only",))

    engine.mark_step_running(run_id=run.id, step_key="only", organization_id=org.id)
    engine.mark_step_completed(run_id=run.id, step_key="only", organization_id=org.id)

    db_session.refresh(run)
    assert run.status == WorkflowRunStatus.COMPLETED
    assert run.current_step is None
    assert run.completed_at is not None

    events = engine.events.list_by_run(run.id, organization_id=org.id)
    assert [event.event_type for event in events] == [
        "workflow.started",
        "step.started",
        "step.completed",
        "workflow.completed",
    ]


def test_mark_step_failed_fails_run(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id)

    engine.mark_step_running(run_id=run.id, step_key="sync", organization_id=org.id)
    engine.mark_step_failed(
        run_id=run.id,
        step_key="sync",
        organization_id=org.id,
        error_code="SYNC_FAILED",
        error_message="boom",
    )

    db_session.refresh(run)
    assert run.status == WorkflowRunStatus.FAILED
    assert run.error_code == "SYNC_FAILED"

    sync_step = engine.steps.get_by_key(
        workflow_run_id=run.id, step_key="sync", organization_id=org.id
    )
    assert sync_step.status == WorkflowStepStatus.FAILED
    assert sync_step.error_json == {"code": "SYNC_FAILED", "message": "boom"}

    events = engine.events.list_by_run(run.id, organization_id=org.id)
    assert [event.event_type for event in events][-2:] == ["step.failed", "workflow.failed"]


def test_resume_resets_failed_step_and_run(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id)

    engine.mark_step_running(run_id=run.id, step_key="sync", organization_id=org.id)
    engine.mark_step_failed(
        run_id=run.id,
        step_key="sync",
        organization_id=org.id,
        error_code="SYNC_FAILED",
        error_message="boom",
    )

    resumed = engine.resume(run_id=run.id, organization_id=org.id)

    assert resumed.status == WorkflowRunStatus.RUNNING
    assert resumed.current_step == "sync"
    assert resumed.error_code is None
    assert resumed.completed_at is None

    sync_step = engine.steps.get_by_key(
        workflow_run_id=run.id, step_key="sync", organization_id=org.id
    )
    assert sync_step.status == WorkflowStepStatus.PENDING
    assert sync_step.error_json is None


def test_resume_raises_when_run_not_resumable(db_session):
    org = _org(db_session)
    engine, run = _started_run(db_session, org.id)

    with pytest.raises(DomainError):
        engine.resume(run_id=run.id, organization_id=org.id)

"""Workflow Engine (Documento 02, secao 25-27; Documento 03, secoes
46-50; Documento 10 Fase 11).

Generic, linear step-execution engine: a WorkflowVersion pins an ordered
list of step keys (``definition_json = {"steps": [...]}"); a WorkflowRun
walks through them one at a time via WorkflowStep rows, emitting
WorkflowEvent rows for every transition. The engine itself does not know
*how* to execute a step - the Celery task for each step calls
``mark_step_running``/``mark_step_completed``/``mark_step_failed`` around
its own real work (same "engine tracks state, Celery just executes"
split as ``Job``/``JobService`` since Fase 05).

``ensure_definition`` is idempotent and self-seeding, same pattern as
``AgentRegistryService.ensure_current_version``: the first caller that
needs a given workflow slug registers it; if the step list changes later,
a new WorkflowVersion is minted rather than mutating the existing one
(CLAUDE.md: "nunca alterar versao existente silenciosamente" /
Documento 02 sec. 27).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, NotFoundError
from app.models.enums import WorkflowRunStatus, WorkflowStepStatus
from app.models.workflow_definition import WorkflowDefinition
from app.models.workflow_event import WorkflowEvent
from app.models.workflow_run import WorkflowRun
from app.models.workflow_step import WorkflowStep
from app.models.workflow_version import WorkflowVersion
from app.repositories.workflow_definition import WorkflowDefinitionRepository
from app.repositories.workflow_event import WorkflowEventRepository
from app.repositories.workflow_run import WorkflowRunRepository
from app.repositories.workflow_step import WorkflowStepRepository
from app.repositories.workflow_version import WorkflowVersionRepository

_RESUMABLE_STATUSES = (WorkflowRunStatus.FAILED, WorkflowRunStatus.PAUSED)


class WorkflowEngineService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.definitions = WorkflowDefinitionRepository(session)
        self.versions = WorkflowVersionRepository(session)
        self.runs = WorkflowRunRepository(session)
        self.steps = WorkflowStepRepository(session)
        self.events = WorkflowEventRepository(session)

    def ensure_definition(
        self, *, slug: str, name: str, description: str, steps: list[str]
    ) -> WorkflowVersion:
        definition = self.definitions.get_by_slug(slug)
        if definition is None:
            definition = WorkflowDefinition(
                name=name, slug=slug, description=description, active=True
            )
            self.definitions.add(definition)

        latest = self.versions.get_latest(definition.id)
        if latest is not None and latest.definition_json.get("steps") == steps:
            return latest

        next_version = (latest.version if latest else 0) + 1
        version = WorkflowVersion(
            workflow_definition_id=definition.id,
            version=next_version,
            definition_json={"steps": steps},
        )
        return self.versions.add(version)

    def start_run(
        self,
        *,
        workflow_version: WorkflowVersion,
        organization_id: uuid.UUID,
        channel_id: uuid.UUID | None = None,
        input_json: dict[str, Any] | None = None,
        correlation_id: uuid.UUID | None = None,
    ) -> WorkflowRun:
        steps: list[str] = workflow_version.definition_json["steps"]
        run = WorkflowRun(
            organization_id=organization_id,
            workflow_version_id=workflow_version.id,
            channel_id=channel_id,
            status=WorkflowRunStatus.RUNNING,
            current_step=steps[0] if steps else None,
            correlation_id=correlation_id or uuid.uuid4(),
            input_json=input_json or {},
        )
        self.runs.add(run)

        for index, step_key in enumerate(steps):
            self.steps.add(
                WorkflowStep(
                    organization_id=organization_id,
                    workflow_run_id=run.id,
                    step_key=step_key,
                    sequence=index,
                    status=WorkflowStepStatus.PENDING,
                )
            )

        self._emit(run, None, "workflow.started", {"steps": steps})
        return run

    def mark_step_running(
        self, *, run_id: uuid.UUID, step_key: str, organization_id: uuid.UUID
    ) -> WorkflowStep:
        run = self._get_run(run_id, organization_id)
        step = self._get_step(run_id, step_key, organization_id)

        step.status = WorkflowStepStatus.RUNNING
        step.started_at = datetime.now(UTC)
        step.attempt_count += 1
        run.current_step = step_key
        self.session.flush()

        self._emit(run, step, "step.started", {"attempt_count": step.attempt_count})
        return step

    def mark_step_completed(
        self,
        *,
        run_id: uuid.UUID,
        step_key: str,
        organization_id: uuid.UUID,
        output_json: dict[str, Any] | None = None,
    ) -> WorkflowStep:
        run = self._get_run(run_id, organization_id)
        step = self._get_step(run_id, step_key, organization_id)

        step.status = WorkflowStepStatus.COMPLETED
        step.completed_at = datetime.now(UTC)
        step.output_json = output_json
        self.session.flush()
        self._emit(run, step, "step.completed", {})

        next_step = self.get_next_pending_step(run_id=run_id, organization_id=organization_id)
        if next_step is not None:
            run.current_step = next_step.step_key
            self.session.flush()
        else:
            run.status = WorkflowRunStatus.COMPLETED
            run.current_step = None
            run.completed_at = datetime.now(UTC)
            self.session.flush()
            self._emit(run, None, "workflow.completed", {})
        return step

    def mark_step_failed(
        self,
        *,
        run_id: uuid.UUID,
        step_key: str,
        organization_id: uuid.UUID,
        error_code: str,
        error_message: str,
    ) -> WorkflowStep:
        run = self._get_run(run_id, organization_id)
        step = self._get_step(run_id, step_key, organization_id)

        step.status = WorkflowStepStatus.FAILED
        step.completed_at = datetime.now(UTC)
        step.error_json = {"code": error_code, "message": error_message}
        self.session.flush()
        self._emit(run, step, "step.failed", {"error_code": error_code})

        run.status = WorkflowRunStatus.FAILED
        run.error_code = error_code
        run.error_message = error_message
        run.completed_at = datetime.now(UTC)
        self.session.flush()
        self._emit(run, None, "workflow.failed", {"failed_step": step_key})
        return step

    def resume(self, *, run_id: uuid.UUID, organization_id: uuid.UUID) -> WorkflowRun:
        """Documento 10 Fase 11 acceptance criterion: "resume". Resets the
        failed step back to pending and puts the run back in RUNNING -
        the caller (a Celery task dispatch) is responsible for actually
        re-executing that step's work."""
        run = self._get_run(run_id, organization_id)
        if run.status not in _RESUMABLE_STATUSES:
            raise DomainError(
                f"Workflow run is {run.status.value}, not resumable", code="WORKFLOW_NOT_RESUMABLE"
            )

        failed_step = next(
            (
                step
                for step in self.steps.list_by_run(run_id, organization_id=organization_id)
                if step.status == WorkflowStepStatus.FAILED
            ),
            None,
        )
        if failed_step is not None:
            failed_step.status = WorkflowStepStatus.PENDING
            failed_step.error_json = None

        run.status = WorkflowRunStatus.RUNNING
        run.current_step = failed_step.step_key if failed_step else run.current_step
        run.completed_at = None
        run.error_code = None
        run.error_message = None
        self.session.flush()

        self._emit(
            run,
            failed_step,
            "workflow.resumed",
            {"resumed_step": failed_step.step_key if failed_step else None},
        )
        return run

    def get_next_pending_step(
        self, *, run_id: uuid.UUID, organization_id: uuid.UUID
    ) -> WorkflowStep | None:
        pending = [
            step
            for step in self.steps.list_by_run(run_id, organization_id=organization_id)
            if step.status == WorkflowStepStatus.PENDING
        ]
        return min(pending, key=lambda step: step.sequence) if pending else None

    def _get_run(self, run_id: uuid.UUID, organization_id: uuid.UUID) -> WorkflowRun:
        run = self.runs.get_by_id(run_id, organization_id=organization_id)
        if run is None:
            raise NotFoundError("Workflow run not found", code="WORKFLOW_RUN_NOT_FOUND")
        return run

    def _get_step(
        self, run_id: uuid.UUID, step_key: str, organization_id: uuid.UUID
    ) -> WorkflowStep:
        step = self.steps.get_by_key(
            workflow_run_id=run_id, step_key=step_key, organization_id=organization_id
        )
        if step is None:
            raise NotFoundError("Workflow step not found", code="WORKFLOW_STEP_NOT_FOUND")
        return step

    def _emit(
        self,
        run: WorkflowRun,
        step: WorkflowStep | None,
        event_type: str,
        payload: dict[str, Any],
    ) -> WorkflowEvent:
        return self.events.add(
            WorkflowEvent(
                organization_id=run.organization_id,
                workflow_run_id=run.id,
                workflow_step_id=step.id if step else None,
                event_type=event_type,
                payload_json=payload,
                correlation_id=run.correlation_id,
            )
        )

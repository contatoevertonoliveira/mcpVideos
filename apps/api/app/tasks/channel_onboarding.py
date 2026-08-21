"""Documento 10 Fase 11: the "channel.onboarding" workflow - sync ->
intelligence -> dna (Documento 04 sec. 4 event chain) - reimplemented on
top of the generic Workflow Engine instead of the ad-hoc inter-service
dispatch chain used since Fase 05/06/07. Each step is still its own
existing Celery task (channel.sync / channel.intelligence / channel.dna);
the Workflow Engine only adds tracking (WorkflowRun/WorkflowStep/
WorkflowEvent) around them - it does not change what any step does.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.enums import SyncType
from app.models.job import Job
from app.models.workflow_run import WorkflowRun
from app.services.workflow_engine import WorkflowEngineService
from app.tasks.channel_sync import dispatch_channel_sync

WORKFLOW_SLUG = "channel.onboarding"
WORKFLOW_STEPS = ["sync", "intelligence", "dna"]


def dispatch_channel_onboarding(
    session: Session, *, channel_id: uuid.UUID, organization_id: uuid.UUID
) -> tuple[Job, WorkflowRun]:
    engine = WorkflowEngineService(session)
    version = engine.ensure_definition(
        slug=WORKFLOW_SLUG,
        name="Channel Onboarding",
        description=(
            "connect -> sync -> intelligence -> dna, run once per newly connected channel "
            "(Documento 04 sec. 4)."
        ),
        steps=WORKFLOW_STEPS,
    )
    run = engine.start_run(
        workflow_version=version, organization_id=organization_id, channel_id=channel_id
    )
    job = dispatch_channel_sync(
        session,
        channel_id=channel_id,
        organization_id=organization_id,
        sync_type=SyncType.INITIAL,
        correlation_id=run.correlation_id,
        workflow_run_id=run.id,
    )
    return job, run

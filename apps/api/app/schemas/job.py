from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import JobStatus


class JobCreate(BaseModel):
    job_type: str
    resource_type: str | None = None
    resource_id: uuid.UUID | None = None
    correlation_id: uuid.UUID | None = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    job_type: str
    resource_type: str | None
    resource_id: uuid.UUID | None
    status: JobStatus
    progress_percent: int
    started_at: datetime | None
    completed_at: datetime | None
    error_code: str | None
    error_message: str | None
    correlation_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

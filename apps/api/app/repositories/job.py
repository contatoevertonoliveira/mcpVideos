from __future__ import annotations

from app.models.job import Job
from app.repositories.base import TenantScopedRepository


class JobRepository(TenantScopedRepository[Job]):
    model = Job

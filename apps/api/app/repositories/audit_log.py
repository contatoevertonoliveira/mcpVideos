from __future__ import annotations

from app.models.audit_log import AuditLog
from app.repositories.base import TenantScopedRepository


class AuditLogRepository(TenantScopedRepository[AuditLog]):
    model = AuditLog

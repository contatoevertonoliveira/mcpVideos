from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import AuditActorType
from app.repositories.audit_log import AuditLogRepository


class AuditService:
    """Documento 09, secao 50-52: acoes criticas rastreaveis, append-only."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit_logs = AuditLogRepository(session)

    def record(
        self,
        *,
        organization_id: uuid.UUID,
        actor_type: AuditActorType,
        action: str,
        resource_type: str,
        actor_id: uuid.UUID | None = None,
        resource_id: uuid.UUID | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            organization_id=organization_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata or {},
            ip_address=ip_address,
        )
        return self.audit_logs.add(entry)

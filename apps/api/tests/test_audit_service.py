from app.models.enums import AuditActorType
from app.services.audit import AuditService
from app.services.organization import OrganizationService


def test_record_creates_audit_entry(db_session):
    org = OrganizationService(db_session).create_organization(name="Acme")

    entry = AuditService(db_session).record(
        organization_id=org.id,
        actor_type=AuditActorType.USER,
        action="channel.connected",
        resource_type="channel",
        metadata={"platform": "youtube"},
    )

    assert entry.organization_id == org.id
    assert entry.action == "channel.connected"
    assert entry.metadata_json == {"platform": "youtube"}

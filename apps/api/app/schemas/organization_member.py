from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MembershipStatus, OrganizationRole


class OrganizationMemberCreate(BaseModel):
    user_id: uuid.UUID
    role: OrganizationRole = OrganizationRole.VIEWER


class OrganizationMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: OrganizationRole
    status: MembershipStatus
    created_at: datetime
    updated_at: datetime

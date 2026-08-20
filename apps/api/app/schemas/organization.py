from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrganizationStatus


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    timezone: str = "UTC"


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: OrganizationStatus
    timezone: str
    created_at: datetime
    updated_at: datetime

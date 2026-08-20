from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import OrganizationRole
from app.schemas.organization import OrganizationRead
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=200)
    organization_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MembershipSummary(BaseModel):
    organization_id: uuid.UUID
    organization_name: str
    role: OrganizationRole


class AuthResponse(BaseModel):
    token: str | None = None
    user: UserRead
    active_organization_id: uuid.UUID | None
    memberships: list[MembershipSummary]


class RegisterResponse(BaseModel):
    token: str
    user: UserRead
    organization: OrganizationRead


class SwitchOrganizationRequest(BaseModel):
    organization_id: uuid.UUID

"""Base repository patterns (Documento 02, secao 7 e 11).

Two variants:

- ``BaseRepository``: for entities that are not themselves scoped to an
  organization (``Organization``, ``User``).
- ``TenantScopedRepository``: for every entity that belongs to an
  organization. Every read requires ``organization_id`` explicitly - there
  is no ``get_by_id(id)`` without it, on purpose (Documento 02, secao 11:
  "Evitar: repository.get_by_id(project_id)" sem escopo).
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, Protocol, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base


class _HasOrganizationId(Protocol):
    # Typed as Any on purpose: at the class level these are SQLAlchemy
    # InstrumentedAttribute descriptors (usable in query expressions like
    # ``self.model.id == id``), not plain uuid.UUID values.
    id: Any
    organization_id: Any


ModelType = TypeVar("ModelType", bound=Base)
TenantModelType = TypeVar("TenantModelType", bound=_HasOrganizationId)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        return self.session.get(self.model, id)

    def list(self, limit: int = 50, offset: int = 0) -> list[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.flush()
        return obj


class TenantScopedRepository(Generic[TenantModelType]):
    model: type[TenantModelType]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: uuid.UUID, *, organization_id: uuid.UUID) -> TenantModelType | None:
        stmt = select(self.model).where(
            self.model.id == id, self.model.organization_id == organization_id
        )
        return self.session.scalars(stmt).first()

    def list(
        self, *, organization_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[TenantModelType]:
        stmt = (
            select(self.model)
            .where(self.model.organization_id == organization_id)
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt).all())

    def add(self, obj: TenantModelType) -> TenantModelType:
        self.session.add(obj)
        self.session.flush()
        return obj

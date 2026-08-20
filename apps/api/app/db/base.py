from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for all ORM models.

    Domain models start arriving in Phase 02 (Core Domain & Database) per
    Documento 03. This module stays intentionally empty of entities here.
    """

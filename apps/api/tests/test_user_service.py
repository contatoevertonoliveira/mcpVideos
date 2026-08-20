import pytest

from app.core.exceptions import DomainError
from app.security.password import verify_password
from app.services.user import UserService


def test_create_user_hashes_password(db_session):
    user = UserService(db_session).create_user(
        email="ana@example.com", name="Ana", password="supersecret1"
    )

    assert user.password_hash != "supersecret1"
    assert verify_password("supersecret1", user.password_hash)
    assert not verify_password("wrong-password", user.password_hash)


def test_create_user_duplicate_email_raises(db_session):
    service = UserService(db_session)
    service.create_user(email="dup@example.com", name="Ana", password="supersecret1")

    with pytest.raises(DomainError):
        service.create_user(email="dup@example.com", name="Outra", password="anotherpass1")

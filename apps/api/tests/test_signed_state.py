import time

import pytest

from app.security.signed_state import InvalidStateError, create_state, verify_state


def test_create_and_verify_round_trip():
    state = create_state({"organization_id": "org-1", "user_id": "user-1"})

    payload = verify_state(state)

    assert payload["organization_id"] == "org-1"
    assert payload["user_id"] == "user-1"


def test_tampered_state_is_rejected():
    state = create_state({"organization_id": "org-1"})
    body_part, signature_part = state.split(".", 1)
    tampered = f"{body_part}x.{signature_part}"

    with pytest.raises(InvalidStateError):
        verify_state(tampered)


def test_expired_state_is_rejected():
    state = create_state({"organization_id": "org-1"}, max_age_seconds=-1)
    time.sleep(0.01)

    with pytest.raises(InvalidStateError):
        verify_state(state)


def test_malformed_state_is_rejected():
    with pytest.raises(InvalidStateError):
        verify_state("not-a-valid-state-token")

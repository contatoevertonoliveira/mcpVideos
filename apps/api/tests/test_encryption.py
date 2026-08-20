from app.security.encryption import decrypt_token, encrypt_token


def test_encrypt_decrypt_round_trip():
    plain = "ya29.some-fake-access-token"

    encrypted = encrypt_token(plain)

    assert encrypted != plain
    assert decrypt_token(encrypted) == plain

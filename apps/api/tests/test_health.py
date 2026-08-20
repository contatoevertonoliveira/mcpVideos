"""Foundation health checks.

/health/db and /health/redis require live PostgreSQL/Redis and are validated
via the docker compose smoke test (see README), not the unit suite, per
Documento 02 secao 54 (no real infra required for basic tests).
"""


def test_health_ok(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"data": {"status": "ok"}, "meta": {}}

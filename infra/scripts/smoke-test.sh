#!/usr/bin/env bash
# Fase 01 smoke test — run after `docker compose up`.
# Confirms the API, its DB connection, and Redis connection are reachable,
# and that the frontend is serving.
set -euo pipefail

API_URL="${API_URL:-http://localhost:8002}"
WEB_URL="${WEB_URL:-http://localhost:3000}"

check() {
  local name="$1" url="$2"
  echo -n "-> ${name} (${url}) ... "
  if curl -fsS "${url}" > /dev/null; then
    echo "OK"
  else
    echo "FAILED"
    exit 1
  fi
}

check "API health" "${API_URL}/health"
check "API <-> PostgreSQL" "${API_URL}/health/db"
check "API <-> Redis" "${API_URL}/health/redis"
check "Web frontend" "${WEB_URL}"

echo "All smoke checks passed."

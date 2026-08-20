from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.redis import get_redis_client
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"data": {"status": "ok"}, "meta": {}}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"data": {"status": "ok", "component": "database"}, "meta": {}}


@router.get("/health/redis")
def health_redis() -> dict:
    client = get_redis_client()
    client.ping()
    return {"data": {"status": "ok", "component": "redis"}, "meta": {}}

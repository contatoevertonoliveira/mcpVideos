from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.channels import router as channels_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(channels_router)

# Health checks are intentionally unversioned - see app/api/health.py.

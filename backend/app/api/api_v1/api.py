from fastapi import APIRouter

from app.api.api_v1.endpoints import discovery

api_router = APIRouter()

api_router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])

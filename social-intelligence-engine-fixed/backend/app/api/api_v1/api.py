from fastapi import APIRouter

from app.api.api_v1.endpoints import discovery, entities, relationships

api_router = APIRouter()

api_router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["relationships"])

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.services.entity_resolution import EntityResolutionService
from app.schemas.entities import EntityResponse, EntityMentionResponse

router = APIRouter()


@router.get("/", response_model=List[EntityResponse])
async def get_entities(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        svc = EntityResolutionService(db)
        return svc.get_entities(skip=skip, limit=limit, entity_type=entity_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[EntityResponse])
async def search_entities(
    query: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    try:
        svc = EntityResolutionService(db)
        return svc.search_entities(query=query, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: int, db: Session = Depends(get_db)):
    svc = EntityResolutionService(db)
    ent = svc.get_entity(entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entity not found")
    return ent


@router.get("/{entity_id}/mentions", response_model=List[EntityMentionResponse])
async def get_mentions(entity_id: int, db: Session = Depends(get_db)):
    svc = EntityResolutionService(db)
    return svc.get_entity_mentions(entity_id)


@router.post("/resolve")
async def resolve(text: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    try:
        svc = EntityResolutionService(db)
        ents = await svc.resolve_entities_in_text(text)
        return {"entities": ents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

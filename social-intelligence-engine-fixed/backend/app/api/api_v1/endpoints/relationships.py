from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.relationship_inference import RelationshipInferenceService

router = APIRouter()


@router.get("/")
def list_relationships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = RelationshipInferenceService(db)
    rels = svc.get_relationships(skip=skip, limit=limit)

    # Return simple JSON for UI
    return [
        {
            "id": r.id,
            "subject_entity_id": r.subject_entity_id,
            "object_entity_id": r.object_entity_id,
            "relationship_type": r.relationship_type,
            "confidence_score": r.confidence_score,
            "source_text": r.source_text,
        }
        for r in rels
    ]


@router.post("/extract")
def extract_relationships(text: str, db: Session = Depends(get_db)):
    svc = RelationshipInferenceService(db)
    return {"relationships": svc.extract_relationships_from_text(text)}

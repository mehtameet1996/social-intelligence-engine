from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RelationshipResponse(BaseModel):
    id: int
    subject_entity_id: int
    object_entity_id: int
    relationship_type: str
    confidence_score: float
    source_text: Optional[str] = None
    created_at: datetime

    subject_name: Optional[str] = None
    object_name: Optional[str] = None

    class Config:
        from_attributes = True

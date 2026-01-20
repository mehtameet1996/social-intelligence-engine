from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EntityResponse(BaseModel):
    id: int
    canonical_name: str
    entity_type: str
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class EntityMentionResponse(BaseModel):
    id: int
    entity_id: int
    mention_text: str
    context: str
    source_url: Optional[str] = None
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from typing import Optional
from typing import Any, Dict, List

from pydantic import BaseModel


class SubredditDiscoveryRequest(BaseModel):
    company_domain: str


class SubredditResponse(BaseModel):
    name: str
    subscribers: int
    description: Optional[str] = None
    business_value_score: float
    relevance_score: float
    engagement_score: float
    mention_count: int = 0
    sample_posts: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

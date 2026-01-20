from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.community_discovery import CommunityDiscoveryService
from app.schemas.discovery import SubredditDiscoveryRequest, SubredditResponse

router = APIRouter()


@router.post("/subreddits", response_model=List[SubredditResponse])
async def discover_subreddits(request: SubredditDiscoveryRequest, db: Session = Depends(get_db)):
    try:
        svc = CommunityDiscoveryService(db)
        return await svc.discover_subreddits(request.company_domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subreddits/{subreddit_name}/analyze")
async def analyze_subreddit(subreddit_name: str):
    # For Level0/1 demo: not implemented in fixed version
    return {"subreddit": subreddit_name, "status": "not_implemented"}

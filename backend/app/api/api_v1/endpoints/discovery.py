from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.services.community_discovery import CommunityDiscoveryService
from app.schemas.discovery import SubredditDiscoveryRequest, SubredditResponse

router = APIRouter()


@router.post("/subreddits", response_model=List[SubredditResponse])
async def discover_subreddits(request: SubredditDiscoveryRequest):
    try:
        svc = CommunityDiscoveryService()
        return await svc.discover_subreddits(request.company_domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


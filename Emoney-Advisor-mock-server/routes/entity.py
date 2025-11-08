from fastapi import APIRouter, Depends, HTTPException, Header, Query, Path, status
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from database import get_db
from services.entity_factory import get_entity_service
from auth.dependencies import verify_api_key

router = APIRouter(
    tags=["Entities"],
    dependencies=[Depends(verify_api_key)],
    responses={401: {"description": "Unauthorized"}},
)

@router.get("/entities")
async def get_entities(
    type: str = Query(..., description="Entity type (e.g., Client, Account, Goal)"),
    q: Optional[str] = Query(None, description="Query filter (e.g., status==active)"),
    limit: int = Query(100, description="Number of results", ge=1, le=500),
    offset: int = Query(0, description="Pagination offset", ge=0),
    options: Optional[str] = Query(None, description="Response options (count for count only)"),
    firm_id: Optional[str] = Query(None, description="Filter by firm identifier"),
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get entities with filtering and pagination support.
    """
    # Verify API key and secret (handled by dependency)
    
    # Get the appropriate service based on entity type
    service = get_entity_service(type, db)
    if not service:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {type}")
    
    # Get entities using the service
    return service.get_entities(q=q, limit=limit, offset=offset, options=options, firm_id=firm_id)
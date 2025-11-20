# routes/admin.py

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Path, status
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from services.admin import AdminService

router = APIRouter(
    tags=["Admin"],
    dependencies=[],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/seed")
async def seed_database(
    entity_type: str = Query("all", description="Entity type to seed"),
    db: Session = Depends(get_db)
):
    """
    Seed the database with test data.
    """
    
    admin_service = AdminService(db)
    return admin_service.seed_database(entity_type)

@router.post("/reset")
async def reset_database(
    db: Session = Depends(get_db)
):
    """
    Reset the database by dropping and recreating all tables.
    """
    admin_service = AdminService(db)
    result = admin_service.reset_database()
    
    return result

@router.get("/status")
async def get_database_status(
    db: Session = Depends(get_db)
):
    """
    Get database status information.
    """
    admin_service = AdminService(db)
    return admin_service.get_database_status()
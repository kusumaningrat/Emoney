from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/users", tags=["User & Access Management"])
def get_users(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all users"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("User", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/users/{user_id}", tags=["User & Access Management"])
def get_user(
    user_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific user by ID"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("User", db)
    return service.get_entity_by_id(user_id)

@router.get("/roles", tags=["User & Access Management"])
def get_roles(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Role", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/permissions", tags=["User & Access Management"])
def get_permissions(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Permission", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/firms", tags=["User & Access Management"])
def get_firms(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all firms"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Firm", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/advisors", tags=["User & Access Management"])
def get_advisors(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all advisors"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Advisor", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/logons", tags=["User & Access Management"])
def get_logons(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all portal logon details"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/logons/{logon_id}", tags=["User & Access Management"])
def get_logon(
    logon_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific portal logon"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_entity_by_id(logon_id)
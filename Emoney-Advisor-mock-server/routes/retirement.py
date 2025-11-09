from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/retirement", tags=["Retirement Planning"])
def get_client_retirement_plan(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client retirement plan"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("RetirementPlan", db)
    return service.get_retirement_plan_by_client_id(client_id)

@router.get("/clients/{client_id}/retirement/pension", tags=["Retirement Planning"])
def get_client_pension(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client pension information"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Pension", db)
    return service.get_pension_by_client_id(client_id)

@router.get("/clients/{client_id}/retirement/social-security", tags=["Retirement Planning"])
def get_client_social_security(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client social security information"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("SocialSecurity", db)
    return service.get_social_security_by_client_id(client_id)

@router.get("/clients/{client_id}/retirement/rmds", tags=["Retirement Planning"])
def get_client_rmds(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client required minimum distributions (RMDs)"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("RMD", db)
    return service.get_rmds_by_client_id(client_id)
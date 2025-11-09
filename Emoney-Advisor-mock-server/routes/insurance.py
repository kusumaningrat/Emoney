from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/insurance", tags=["Insurance Planning"])
def get_client_insurance(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client insurance information"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Insurance", db)
    return service.get_insurance_by_client_id(client_id)

@router.get("/clients/{client_id}/insurance/policies", tags=["Insurance Planning"])
def get_client_insurance_policies(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client insurance policies"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Policy", db)
    return service.get_policies_by_client_id(client_id)

@router.get("/clients/{client_id}/insurance/coverage", tags=["Insurance Planning"])
def get_client_insurance_coverage(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client insurance coverage"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Coverage", db)
    return service.get_coverage_by_client_id(client_id)

@router.get("/clients/{client_id}/insurance/premiums", tags=["Insurance Planning"])
def get_client_insurance_premiums(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client insurance premiums"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Premium", db)
    return service.get_premiums_by_client_id(client_id)
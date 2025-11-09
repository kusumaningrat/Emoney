from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/estate", tags=["Estate Planning"])
def get_client_estate(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client estate planning data"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Estate", db)
    return service.get_estate_by_client_id(client_id)

@router.get("/clients/{client_id}/estate/will", tags=["Estate Planning"])
def get_client_will(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client will"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Will", db)
    return service.get_will_by_client_id(client_id)

@router.get("/clients/{client_id}/estate/trusts", tags=["Estate Planning"])
def get_client_trusts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client trusts"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Trust", db)
    return service.get_trusts_by_client_id(client_id)

@router.get("/clients/{client_id}/estate/beneficiaries", tags=["Estate Planning"])
def get_client_beneficiaries(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client beneficiaries"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Beneficiary", db)
    return service.get_beneficiaries_by_client_id(client_id)
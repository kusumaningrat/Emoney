from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/tax", tags=["Tax Planning"])
def get_client_tax_plan(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client tax plan"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("TaxPlan", db)
    return service.get_tax_plan_by_client_id(client_id)

@router.get("/clients/{client_id}/tax/brackets", tags=["Tax Planning"])
def get_client_tax_brackets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client tax brackets"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("TaxBracket", db)
    return service.get_tax_brackets_by_client_id(client_id)

@router.get("/clients/{client_id}/tax/deductions", tags=["Tax Planning"])
def get_client_tax_deductions(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client tax deductions"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Deduction", db)
    return service.get_deductions_by_client_id(client_id)

@router.get("/clients/{client_id}/tax/credits", tags=["Tax Planning"])
def get_client_tax_credits(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client tax credits"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Credit", db)
    return service.get_credits_by_client_id(client_id)
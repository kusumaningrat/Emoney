from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/accounts", tags=["Account Management"])
def get_client_accounts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all accounts for a client"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Account", db)
    return service.get_accounts_by_client_id(client_id)

@router.get("/clients/{client_id}/accounts/{account_id}", tags=["Account Management"])
def get_account(
    client_id: str,
    account_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific account"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Account", db)
    return service.get_account_by_id(client_id, account_id)

@router.get("/clients/{client_id}/accounts/{account_id}/investments", tags=["Account Management"])
def get_account_investments(
    client_id: str,
    account_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get investments for an account"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Investment", db)
    return service.get_investments_by_account_id(client_id, account_id)

@router.get("/clients/{client_id}/liabilities", tags=["Account Management"])
def get_client_liabilities(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client liabilities"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Liability", db)
    return service.get_liabilities_by_client_id(client_id)

@router.get("/account-types", tags=["Account Management"])
def get_account_types(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all account types"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("AccountType", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)
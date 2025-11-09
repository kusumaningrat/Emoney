from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients", tags=["Client & Relationship Management"])
def get_clients(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """List all clients"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Client", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/clients/{client_id}", tags=["Client & Relationship Management"])
def get_client(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific client"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Client", db)
    return service.get_entity_by_id(client_id)

@router.get("/clients/{client_id}/spouse", tags=["Client & Relationship Management"])
def get_client_spouse(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client spouse information"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Spouse", db)
    return service.get_spouse_by_client_id(client_id)

@router.get("/clients/{client_id}/household", tags=["Client & Relationship Management"])
def get_client_household(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client household information"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Household", db)
    return service.get_household_by_client_id(client_id)

@router.get("/clients/{client_id}/contacts", tags=["Client & Relationship Management"])
def get_client_contacts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client contacts"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Contact", db)
    return service.get_contacts_by_client_id(client_id)

@router.get("/clients/{client_id}/relationships", tags=["Client & Relationship Management"])
def get_client_relationships(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client relationships"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Relationship", db)
    return service.get_relationships_by_client_id(client_id)

@router.get("/clients/{client_id}/logons", tags=["Client & Relationship Management"])
def get_client_logon(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client portal logon"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_logon_by_client_id(client_id)
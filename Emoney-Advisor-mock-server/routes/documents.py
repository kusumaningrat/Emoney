from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/vault", tags=["Documents & Communication"])
def get_client_vault_documents(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client vault documents"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("VaultDocument", db)
    return service.get_documents_by_client_id(client_id)

@router.get("/clients/{client_id}/vault/{document_id}", tags=["Documents & Communication"])
def get_client_vault_document(
    client_id: str,
    document_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific vault document"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("VaultDocument", db)
    return service.get_document_by_id(client_id, document_id)

@router.get("/file-types", tags=["Documents & Communication"])
def get_file_types(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all file types"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FileType", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/clients/{client_id}/notes", tags=["Documents & Communication"])
def get_client_notes(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client notes"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Note", db)
    return service.get_notes_by_client_id(client_id)

@router.get("/clients/{client_id}/tasks", tags=["Documents & Communication"])
def get_client_tasks(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client tasks"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Task", db)
    return service.get_tasks_by_client_id(client_id)

@router.get("/alerts", tags=["Documents & Communication"])
def get_alerts(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all alerts"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Alert", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)
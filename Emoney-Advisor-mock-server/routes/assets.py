from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/assets", tags=["Asset Management"])
def get_client_assets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all assets for a client"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Asset", db)
    return service.get_assets_by_client_id(client_id)

@router.get("/clients/{client_id}/plans/{plan_id}/assets", tags=["Asset Management"])
def get_plan_assets(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan assets"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Asset", db)
    return service.get_assets_by_plan_id(client_id, plan_id)

@router.get("/asset-classes", tags=["Asset Management"])
def get_asset_classes(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all asset classes"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("AssetClass", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@router.get("/securities", tags=["Asset Management"])
def get_securities(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all securities"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Security", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)
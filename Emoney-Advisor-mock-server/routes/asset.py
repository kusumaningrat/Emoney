# routes/asset.py - eMoney Advisor Asset Management (Version 4b)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from database import get_db
from models.asset import Asset, AssetClass, Liability
from services.asset import AssetService, AssetClassService, LiabilityService

router = APIRouter(
    tags=["eMoney Asset Management"],
    dependencies=[]
)

# Helper function to convert SQLAlchemy models to dict
def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        # Handle enum serialization
        elif hasattr(value, 'value'):
            value = value.value
        # Handle decimal serialization
        elif hasattr(value, '__float__'):
            value = float(value)
        result[column.name] = value
    return result

# ============================================================================
# ASSET MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/assets")
def get_assets(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    assetClass: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    accountId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all assets"""
    service = AssetService()
    skip = (page - 1) * pageSize
    
    # Use the actual service method signature from services/asset.py
    assets = service.get_all(
        db, 
        skip=skip, 
        limit=pageSize,
        account_id=accountId,
        asset_class_id=assetClass,
        symbol=symbol,
        status=status
    )
    
    # Count total (get all without pagination)
    all_assets = service.get_all(db, limit=10000)
    total = len(all_assets)
    
    return {
        "assets": [model_to_dict(asset) for asset in assets],
        "total": total,
        "page": page,
        "pageSize": len(assets),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/assets/{assetId}")
def get_asset(
    assetId: str = Path(...),
    includePerformance: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get asset details"""
    service = AssetService()
    asset = service.get_by_id(db, assetId)
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {assetId} not found")
    
    result = model_to_dict(asset)
    
    # Add asset class details
    if asset.asset_class:
        result['assetClassName'] = asset.asset_class.class_name
        result['assetCategory'] = asset.asset_class.category
        result['riskLevel'] = asset.asset_class.risk_level
    
    # Add account details
    if asset.account:
        result['accountNumber'] = asset.account.account_number
        result['accountName'] = asset.account.account_name
    
    # Calculate percentage of account
    if asset.account and asset.account.balance and asset.value:
        result['percentOfAccount'] = (float(asset.value) / float(asset.account.balance)) * 100
    
    if includePerformance:
        result['performance'] = service.get_asset_performance(db, assetId)
    
    return result

@router.get("/assets/{assetId}/performance")
def get_asset_performance(
    assetId: str = Path(...),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get asset performance"""
    service = AssetService()
    asset = service.get_by_id(db, assetId)
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {assetId} not found")
    
    performance = service.get_asset_performance(db, assetId, start_date=startDate, end_date=endDate)
    
    return {
        "assetId": assetId,
        "securityName": asset.security_name,
        "symbol": asset.symbol,
        "currentPrice": float(asset.price) if asset.price else None,
        "currentValue": float(asset.value) if asset.value else None,
        "shares": float(asset.shares) if asset.shares else None,
        "startDate": startDate,
        "endDate": endDate,
        "performance": performance
    }

# ============================================================================
# ASSET CLASS ENDPOINTS
# ============================================================================

@router.get("/assetclasses")
def get_asset_classes(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    riskLevel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List asset classes"""
    service = AssetClassService()
    skip = (page - 1) * pageSize
    
    # Use the actual service method signature
    asset_classes = service.get_all(
        db,
        skip=skip,
        limit=pageSize,
        category=category,
        risk_level=riskLevel,
        status=status
    )
    
    # Count total
    all_classes = service.get_all(db, limit=1000)
    total = len(all_classes)
    
    return {
        "assetClasses": [model_to_dict(ac) for ac in asset_classes],
        "total": total,
        "page": page,
        "pageSize": len(asset_classes),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/assetclasses/{classId}")
def get_asset_class(
    classId: str = Path(...),
    includeAssets: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get specific asset class"""
    service = AssetClassService()
    asset_class = service.get_by_id(db, classId)
    
    if not asset_class:
        raise HTTPException(status_code=404, detail=f"Asset class {classId} not found")
    
    result = model_to_dict(asset_class)
    
    if includeAssets:
        # Get assets for this class
        asset_service = AssetService()
        assets = asset_service.get_all(db, asset_class_id=classId, limit=1000)
        result['assets'] = [model_to_dict(a) for a in assets]
        result['assetCount'] = len(assets)
        result['totalValue'] = sum(float(a.value) if a.value else 0 for a in assets)
    
    return result

# ============================================================================
# LIABILITY MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/liabilities")
def get_liabilities(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    liabilityType: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    householdId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all liabilities"""
    service = LiabilityService()
    skip = (page - 1) * pageSize
    
    # Use the actual service method signature
    liabilities = service.get_all(
        db,
        skip=skip,
        limit=pageSize,
        client_id=clientId,
        household_id=householdId,
        liability_type=liabilityType,
        status=status
    )
    
    # Count total
    all_liabilities = service.get_all(db, limit=10000)
    total = len(all_liabilities)
    
    return {
        "liabilities": [model_to_dict(liability) for liability in liabilities],
        "total": total,
        "page": page,
        "pageSize": len(liabilities),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/liabilities/{liabilityId}")
def get_liability(
    liabilityId: str = Path(...),
    includeSchedule: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get specific liability"""
    service = LiabilityService()
    liability = service.get_by_id(db, liabilityId)
    
    if not liability:
        raise HTTPException(status_code=404, detail=f"Liability {liabilityId} not found")
    
    result = model_to_dict(liability)
    
    # Calculate additional fields
    if liability.current_balance and liability.original_amount:
        result['principalPaid'] = float(liability.original_amount) - float(liability.current_balance)
        result['percentPaid'] = (result['principalPaid'] / float(liability.original_amount)) * 100
    
    if includeSchedule:
        result['paymentSchedule'] = service.get_liability_schedule(db, liabilityId)
    
    return result

@router.get("/liabilities/{liabilityId}/schedule")
def get_liability_schedule(
    liabilityId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get payment schedule"""
    service = LiabilityService()
    liability = service.get_by_id(db, liabilityId)
    
    if not liability:
        raise HTTPException(status_code=404, detail=f"Liability {liabilityId} not found")
    
    schedule = service.get_liability_schedule(db, liabilityId)
    
    return {
        "liabilityId": liabilityId,
        "liabilityName": liability.liability_name,
        "liabilityType": liability.liability_type,
        "schedule": schedule
    }

# ============================================================================
# HOUSEHOLD & CLIENT ASSET/LIABILITY ENDPOINTS
# ============================================================================

@router.get("/households/{householdId}/assets")
def get_household_assets(
    householdId: str = Path(...),
    includePerformance: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get household assets"""
    service = AssetService()
    
    # Get all assets and filter by household (through accounts/clients)
    all_assets = service.get_all(db, limit=10000)
    household_assets = []
    
    for asset in all_assets:
        # Check if asset belongs to household (through client)
        if asset.account and asset.account.client_id:
            # Would need to check if client belongs to household
            # Simplified: just return all assets for now
            household_assets.append(asset)
    
    result = {
        "householdId": householdId,
        "assets": [model_to_dict(a) for a in household_assets[:100]],  # Limit to 100
        "totalValue": sum(float(a.value) if a.value else 0 for a in household_assets),
        "totalCostBasis": sum(float(a.cost_basis) if a.cost_basis else 0 for a in household_assets),
        "total": len(household_assets)
    }
    
    return result

@router.get("/households/{householdId}/liabilities")
def get_household_liabilities(
    householdId: str = Path(...),
    status: Optional[str] = Query("Active"),
    db: Session = Depends(get_db)
):
    """Get household liabilities"""
    service = LiabilityService()
    
    liabilities = service.get_all(
        db,
        household_id=householdId,
        status=status,
        limit=1000
    )
    
    result = {
        "householdId": householdId,
        "liabilities": [model_to_dict(l) for l in liabilities],
        "totalCurrentBalance": sum(float(l.current_balance) if l.current_balance else 0 for l in liabilities),
        "totalMonthlyPayments": sum(float(l.monthly_payment) if l.monthly_payment else 0 for l in liabilities),
        "total": len(liabilities)
    }
    
    # Group by type
    by_type = {}
    for liability in liabilities:
        lib_type = liability.liability_type
        if lib_type not in by_type:
            by_type[lib_type] = {"count": 0, "totalBalance": 0, "totalMonthlyPayment": 0}
        by_type[lib_type]["count"] += 1
        by_type[lib_type]["totalBalance"] += float(liability.current_balance) if liability.current_balance else 0
        by_type[lib_type]["totalMonthlyPayment"] += float(liability.monthly_payment) if liability.monthly_payment else 0
    
    result["byType"] = by_type
    
    return result

@router.get("/clients/{clientId}/net-worth")
def get_client_net_worth(
    clientId: str = Path(...),
    asOfDate: Optional[str] = Query(None),
    includeBreakdown: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Calculate client net worth from assets and liabilities"""
    asset_service = AssetService()
    liability_service = LiabilityService()
    
    # Get client assets (through accounts)
    all_assets = asset_service.get_all(db, limit=10000)
    client_assets = [a for a in all_assets if a.account and a.account.client_id == clientId]
    total_assets = sum(float(a.value) if a.value else 0 for a in client_assets)
    
    # Get client liabilities
    client_liabilities = liability_service.get_all(db, client_id=clientId, limit=1000)
    total_liabilities = sum(float(l.current_balance) if l.current_balance else 0 for l in client_liabilities)
    
    result = {
        "clientId": clientId,
        "asOfDate": asOfDate or datetime.now().isoformat(),
        "netWorth": total_assets - total_liabilities,
        "totalAssets": total_assets,
        "totalLiabilities": total_liabilities
    }
    
    if includeBreakdown:
        # Asset breakdown by class
        asset_breakdown = {}
        for asset in client_assets:
            class_name = asset.asset_class.class_name if asset.asset_class else "Unknown"
            if class_name not in asset_breakdown:
                asset_breakdown[class_name] = 0
            asset_breakdown[class_name] += float(asset.value) if asset.value else 0
        
        # Liability breakdown by type
        liability_breakdown = {}
        for liability in client_liabilities:
            lib_type = liability.liability_type
            if lib_type not in liability_breakdown:
                liability_breakdown[lib_type] = 0
            liability_breakdown[lib_type] += float(liability.current_balance) if liability.current_balance else 0
        
        result["breakdown"] = {
            "assets": asset_breakdown,
            "liabilities": liability_breakdown
        }
    
    return result
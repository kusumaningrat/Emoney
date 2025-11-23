# routes/asset.py - eMoney Advisor Asset Management (Version 4b)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from database import get_db
from models.asset import Asset, AssetClass, Liability
from services.asset import AssetService, AssetClassService, LiabilityService

router = APIRouter(
    prefix="/api/v1",
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
    minValue: Optional[float] = Query(None),
    maxValue: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """List all assets"""
    service = AssetService()
    skip = (page - 1) * pageSize
    
    filters = {}
    if assetClass:
        filters['asset_class_id'] = assetClass
    if symbol:
        filters['symbol'] = symbol
    if accountId:
        filters['account_id'] = accountId
    if status:
        filters['status'] = status
    if minValue:
        filters['min_value'] = minValue
    if maxValue:
        filters['max_value'] = maxValue
    
    assets = service.get_all_filtered(db, skip=skip, limit=pageSize, **filters)
    total = service.count_filtered(db, **filters)
    
    return {
        "assets": [model_to_dict(asset) for asset in assets],
        "total": total,
        "page": page,
        "pageSize": len(assets),
        "totalPages": (total + pageSize - 1) // pageSize
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
        result['performance'] = service.get_performance(db, assetId)
        result['priceHistory'] = service.get_price_history(db, assetId, days=90)
    
    return result

@router.get("/assets/{assetId}/performance")
def get_asset_performance(
    assetId: str = Path(...),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    period: Optional[str] = Query(None),  # YTD, 1M, 3M, 6M, 1Y, 3Y, 5Y
    db: Session = Depends(get_db)
):
    """Get asset performance"""
    service = AssetService()
    asset = service.get_by_id(db, assetId)
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {assetId} not found")
    
    performance = service.get_performance(db, assetId, start_date=startDate, end_date=endDate, period=period)
    
    return {
        "assetId": assetId,
        "securityName": asset.security_name,
        "symbol": asset.symbol,
        "cusip": asset.cusip,
        "currentPrice": float(asset.price) if asset.price else None,
        "currentValue": float(asset.value) if asset.value else None,
        "shares": float(asset.shares) if asset.shares else None,
        "startDate": startDate,
        "endDate": endDate,
        "period": period,
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
    
    filters = {}
    if category:
        filters['category'] = category
    if riskLevel:
        filters['risk_level'] = riskLevel
    if status:
        filters['status'] = status
    
    asset_classes = service.get_all_filtered(db, skip=skip, limit=pageSize, **filters)
    total = service.count_filtered(db, **filters)
    
    return {
        "assetClasses": [model_to_dict(ac) for ac in asset_classes],
        "total": total,
        "page": page,
        "pageSize": len(asset_classes),
        "totalPages": (total + pageSize - 1) // pageSize
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
        assets = service.get_assets_in_class(db, classId)
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
    lender: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all liabilities"""
    service = LiabilityService()
    skip = (page - 1) * pageSize
    
    filters = {}
    if liabilityType:
        filters['liability_type'] = liabilityType
    if clientId:
        filters['client_id'] = clientId
    if householdId:
        filters['household_id'] = householdId
    if status:
        filters['status'] = status
    if lender:
        filters['lender'] = lender
    
    liabilities = service.get_all_filtered(db, skip=skip, limit=pageSize, **filters)
    total = service.count_filtered(db, **filters)
    
    return {
        "liabilities": [model_to_dict(liability) for liability in liabilities],
        "total": total,
        "page": page,
        "pageSize": len(liabilities),
        "totalPages": (total + pageSize - 1) // pageSize
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
    
    # Calculate remaining term
    if liability.maturity_date:
        remaining_months = service.calculate_remaining_months(db, liabilityId)
        result['remainingMonths'] = remaining_months
        result['remainingYears'] = remaining_months / 12 if remaining_months else 0
    
    if includeSchedule:
        result['paymentSchedule'] = service.get_payment_schedule(db, liabilityId)
        result['totalInterestRemaining'] = service.calculate_total_interest_remaining(db, liabilityId)
    
    return result

@router.get("/liabilities/{liabilityId}/schedule")
def get_liability_schedule(
    liabilityId: str = Path(...),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get payment schedule"""
    service = LiabilityService()
    liability = service.get_by_id(db, liabilityId)
    
    if not liability:
        raise HTTPException(status_code=404, detail=f"Liability {liabilityId} not found")
    
    skip = (page - 1) * pageSize
    schedule = service.get_payment_schedule(
        db, liabilityId, 
        start_date=startDate, 
        end_date=endDate,
        skip=skip,
        limit=pageSize
    )
    
    total_payments = service.count_scheduled_payments(db, liabilityId, start_date=startDate, end_date=endDate)
    
    return {
        "liabilityId": liabilityId,
        "liabilityName": liability.liability_name,
        "liabilityType": liability.liability_type,
        "currentBalance": float(liability.current_balance) if liability.current_balance else 0,
        "monthlyPayment": float(liability.monthly_payment) if liability.monthly_payment else 0,
        "interestRate": float(liability.interest_rate) if liability.interest_rate else 0,
        "paymentSchedule": schedule,
        "startDate": startDate,
        "endDate": endDate,
        "total": total_payments,
        "page": page,
        "pageSize": len(schedule),
        "totalPages": (total_payments + pageSize - 1) // pageSize if total_payments > 0 else 0
    }

# ============================================================================
# COMPLEX DATA EXTRACTION ENDPOINTS
# ============================================================================

@router.get("/households/{householdId}/assets")
def get_household_assets(
    householdId: str = Path(...),
    groupBy: Optional[str] = Query("assetClass"),  # assetClass, account, symbol
    includePerformance: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get household assets grouped by specified criteria"""
    service = AssetService()
    
    assets = service.get_by_household_id(db, householdId)
    
    result = {
        "householdId": householdId,
        "assets": [model_to_dict(a) for a in assets],
        "totalValue": sum(float(a.value) if a.value else 0 for a in assets),
        "totalCostBasis": sum(float(a.cost_basis) if a.cost_basis else 0 for a in assets),
        "totalUnrealizedGain": sum(float(a.unrealized_gain) if a.unrealized_gain else 0 for a in assets),
        "groupedBy": groupBy
    }
    
    # Group assets by specified criteria
    grouped = {}
    for asset in assets:
        if groupBy == "assetClass":
            key = asset.asset_class.class_name if asset.asset_class else "Unknown"
        elif groupBy == "account":
            key = f"{asset.account.account_name} ({asset.account.account_number})" if asset.account else "Unknown"
        elif groupBy == "symbol":
            key = asset.symbol or "No Symbol"
        else:
            key = "All Assets"
        
        if key not in grouped:
            grouped[key] = {
                "assets": [],
                "totalValue": 0,
                "totalCostBasis": 0,
                "totalUnrealizedGain": 0,
                "count": 0
            }
        
        grouped[key]["assets"].append(model_to_dict(asset))
        grouped[key]["totalValue"] += float(asset.value) if asset.value else 0
        grouped[key]["totalCostBasis"] += float(asset.cost_basis) if asset.cost_basis else 0
        grouped[key]["totalUnrealizedGain"] += float(asset.unrealized_gain) if asset.unrealized_gain else 0
        grouped[key]["count"] += 1
    
    result["grouped"] = grouped
    result["total"] = len(assets)
    
    if includePerformance:
        result["householdPerformance"] = service.get_household_performance(db, householdId)
    
    return result

@router.get("/households/{householdId}/liabilities")
def get_household_liabilities(
    householdId: str = Path(...),
    status: Optional[str] = Query("Active"),
    includeSchedules: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get household liabilities"""
    service = LiabilityService()
    
    filters = {'household_id': householdId}
    if status:
        filters['status'] = status
    
    liabilities = service.get_all_filtered(db, **filters)
    
    result = {
        "householdId": householdId,
        "liabilities": [],
        "totalCurrentBalance": 0,
        "totalMonthlyPayments": 0,
        "byType": {},
        "byLender": {}
    }
    
    for liability in liabilities:
        liability_data = model_to_dict(liability)
        
        if includeSchedules:
            liability_data['upcomingPayments'] = service.get_upcoming_payments(db, liability.liability_id, months=12)
        
        result["liabilities"].append(liability_data)
        result["totalCurrentBalance"] += float(liability.current_balance) if liability.current_balance else 0
        result["totalMonthlyPayments"] += float(liability.monthly_payment) if liability.monthly_payment else 0
        
        # Group by type
        lib_type = liability.liability_type
        if lib_type not in result["byType"]:
            result["byType"][lib_type] = {"count": 0, "totalBalance": 0, "totalMonthlyPayment": 0}
        result["byType"][lib_type]["count"] += 1
        result["byType"][lib_type]["totalBalance"] += float(liability.current_balance) if liability.current_balance else 0
        result["byType"][lib_type]["totalMonthlyPayment"] += float(liability.monthly_payment) if liability.monthly_payment else 0
        
        # Group by lender
        lender = liability.lender or "Unknown"
        if lender not in result["byLender"]:
            result["byLender"][lender] = {"count": 0, "totalBalance": 0, "totalMonthlyPayment": 0}
        result["byLender"][lender]["count"] += 1
        result["byLender"][lender]["totalBalance"] += float(liability.current_balance) if liability.current_balance else 0
        result["byLender"][lender]["totalMonthlyPayment"] += float(liability.monthly_payment) if liability.monthly_payment else 0
    
    result["total"] = len(liabilities)
    
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
    
    # Get client assets
    assets = asset_service.get_by_client_id(db, clientId, as_of_date=asOfDate)
    total_assets = sum(float(a.value) if a.value else 0 for a in assets)
    
    # Get client liabilities  
    liabilities = liability_service.get_by_client_id(db, clientId)
    total_liabilities = sum(float(l.current_balance) if l.current_balance else 0 for l in liabilities)
    
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
        for asset in assets:
            class_name = asset.asset_class.class_name if asset.asset_class else "Unknown"
            if class_name not in asset_breakdown:
                asset_breakdown[class_name] = 0
            asset_breakdown[class_name] += float(asset.value) if asset.value else 0
        
        # Liability breakdown by type
        liability_breakdown = {}
        for liability in liabilities:
            lib_type = liability.liability_type
            if lib_type not in liability_breakdown:
                liability_breakdown[lib_type] = 0
            liability_breakdown[lib_type] += float(liability.current_balance) if liability.current_balance else 0
        
        result["breakdown"] = {
            "assets": asset_breakdown,
            "liabilities": liability_breakdown
        }
    
    return result

# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics/assets")
def get_asset_analytics(
    db: Session = Depends(get_db)
):
    """Get asset analytics"""
    service = AssetService()
    
    analytics = {
        "total_assets": service.count_all(db),
        "active_assets": service.count_by_status(db, "Active"),
        "by_asset_class": service.count_by_asset_class(db),
        "total_value": service.get_total_value_all_assets(db),
        "average_asset_value": service.get_average_asset_value(db),
        "top_holdings_by_value": service.get_top_holdings_by_value(db, limit=10),
        "most_held_securities": service.get_most_held_securities(db, limit=10),
        "unrealized_gains_losses": service.get_unrealized_gains_summary(db)
    }
    
    return analytics

@router.get("/analytics/asset-classes")
def get_asset_class_analytics(
    db: Session = Depends(get_db)
):
    """Get asset class analytics"""
    service = AssetClassService()
    
    analytics = {
        "total_asset_classes": service.count_all(db),
        "active_asset_classes": service.count_by_status(db, "Active"),
        "by_category": service.count_by_category(db),
        "by_risk_level": service.count_by_risk_level(db),
        "allocation_summary": service.get_allocation_summary(db),
        "performance_by_class": service.get_performance_by_class(db)
    }
    
    return analytics

@router.get("/analytics/liabilities")
def get_liability_analytics(
    db: Session = Depends(get_db)
):
    """Get liability analytics"""
    service = LiabilityService()
    
    analytics = {
        "total_liabilities": service.count_all(db),
        "active_liabilities": service.count_by_status(db, "Active"),
        "by_liability_type": service.count_by_liability_type(db),
        "by_lender": service.count_by_lender(db),
        "total_current_balance": service.get_total_current_balance(db),
        "total_monthly_payments": service.get_total_monthly_payments(db),
        "average_interest_rate": service.get_average_interest_rate(db),
        "debt_to_income_ratios": service.get_debt_ratios(db)
    }
    
    return analytics
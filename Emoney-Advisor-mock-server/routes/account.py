# routes/account.py - eMoney Advisor Account Management (Version 4a)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from database import get_db
from models.account import Account, AccountType
from services.account import AccountService, AccountTypeService

router = APIRouter(
    tags=["eMoney Account Management"],
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
# ACCOUNT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/accounts")
def get_accounts(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    accountType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    householdId: Optional[str] = Query(None),
    totalValue: Optional[str] = Query(None),  # e.g., "gt:500000"
    isManaged: Optional[bool] = Query(None),
    isTaxable: Optional[bool] = Query(None),
    custodian: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all accounts"""
    service = AccountService()
    skip = (page - 1) * pageSize
    
    # Map API parameters to service parameters
    accounts = service.get_all(
        db, skip=skip, limit=pageSize,
        client_id=clientId, 
        household_id=householdId,
        account_type=accountType,
        status=status,
        custodian_name=custodian
    )
    
    # Apply additional filtering for boolean fields
    if isManaged is not None:
        accounts = [a for a in accounts if a.IsManaged == isManaged]
    if isTaxable is not None:
        accounts = [a for a in accounts if a.IsTaxable == isTaxable]
    
    # Apply value filtering
    if totalValue:
        operator, amount = totalValue.split(":", 1) if ":" in totalValue else ("eq", totalValue)
        amount = float(amount)
        if operator == "gt":
            accounts = [a for a in accounts if a.Balance and float(a.Balance) > amount]
        elif operator == "lt":
            accounts = [a for a in accounts if a.Balance and float(a.Balance) < amount]
        elif operator == "eq":
            accounts = [a for a in accounts if a.Balance and float(a.Balance) == amount]
    
    # Get total count for pagination
    total_accounts = service.get_all(
        db, client_id=clientId, household_id=householdId,
        account_type=accountType, status=status, custodian_name=custodian
    )
    total = len(total_accounts)
    
    return {
        "accounts": [model_to_dict(account) for account in accounts],
        "total": total,
        "page": page,
        "pageSize": len(accounts),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/accounts/{accountId}")
def get_account(
    accountId: str = Path(...),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get specific account"""
    service = AccountService()
    account = service.get_by_id(db, accountId)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {accountId} not found")
    
    result = model_to_dict(account)
    
    # Add account type details
    if account.account_type:
        result['accountTypeName'] = account.account_type.TypeName
        result['accountCategory'] = account.account_type.Category
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'holdings' in includes:
            holdings = service.get_account_holdings(db, accountId)
            result['holdings'] = [model_to_dict(h) for h in holdings]
        
        if 'positions' in includes:
            positions = service.get_account_positions(db, accountId)
            result['positions'] = [model_to_dict(p) for p in positions]
        
        if 'transactions' in includes:
            transactions = service.get_account_transactions(db, accountId)
            result['transactions'] = transactions  # Already a list of dicts
        
        if 'performance' in includes:
            result['performance'] = service.get_account_performance(db, accountId)
    
    return result

@router.get("/accounts/{accountId}/holdings")
def get_account_holdings(
    accountId: str = Path(...),
    asOfDate: Optional[str] = Query(None),
    includePerformance: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get account holdings"""
    service = AccountService()
    account = service.get_by_id(db, accountId)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {accountId} not found")
    
    holdings = service.get_account_holdings(db, accountId, as_of_date=asOfDate)
    
    result = {
        "accountId": accountId,
        "accountNumber": account.AccountNumber,
        "accountName": account.AccountName,
        "accountType": account.account_type.TypeName if account.account_type else None,
        "balance": float(account.Balance) if account.Balance else 0,
        "asOfDate": asOfDate or (account.AsOfDate.isoformat() if account.AsOfDate else datetime.now().isoformat()),
        "holdings": []
    }
    
    total_value = 0
    total_cost_basis = 0
    total_unrealized_gain = 0
    
    for holding in holdings:
        holding_data = model_to_dict(holding)
        result["holdings"].append(holding_data)
        
        if holding.Value:
            total_value += float(holding.Value)
        if holding.CostBasis:
            total_cost_basis += float(holding.CostBasis)
        if holding.UnrealizedGain:
            total_unrealized_gain += float(holding.UnrealizedGain)
    
    result["totalValue"] = total_value
    result["totalCostBasis"] = total_cost_basis
    result["totalUnrealizedGain"] = total_unrealized_gain
    result["unrealizedGainPercent"] = (total_unrealized_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0
    
    if includePerformance:
        performance = service.get_account_performance(db, accountId)
        result['performanceYTD'] = performance.get('unrealized_gain_percent', 0)
        result['performance1Year'] = performance.get('unrealized_gain_percent', 0)  # Simplified
    
    return result

@router.get("/accounts/{accountId}/positions")
def get_account_positions(
    accountId: str = Path(...),
    asOfDate: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get account positions"""
    service = AccountService()
    account = service.get_by_id(db, accountId)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {accountId} not found")
    
    positions = service.get_account_positions(db, accountId)
    
    return {
        "accountId": accountId,
        "accountNumber": account.AccountNumber,
        "asOfDate": asOfDate or datetime.now().isoformat(),
        "positions": [model_to_dict(p) for p in positions],
        "total": len(positions)
    }

@router.get("/accounts/{accountId}/transactions")
def get_account_transactions(
    accountId: str = Path(...),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    transactionType: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get account transactions"""
    service = AccountService()
    account = service.get_by_id(db, accountId)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {accountId} not found")
    
    # Get transactions (placeholder implementation)
    transactions = service.get_account_transactions(db, accountId, start_date=startDate, end_date=endDate)
    
    return {
        "accountId": accountId,
        "accountNumber": account.AccountNumber,
        "transactions": transactions,
        "total": len(transactions),
        "page": page,
        "pageSize": len(transactions),
        "totalPages": 1,
        "note": "Transaction data would require additional Transaction model implementation"
    }

@router.get("/accounts/{accountId}/performance")
def get_account_performance(
    accountId: str = Path(...),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    period: Optional[str] = Query(None),  # YTD, 1M, 3M, 6M, 1Y, 3Y, 5Y
    db: Session = Depends(get_db)
):
    """Get account performance"""
    service = AccountService()
    account = service.get_by_id(db, accountId)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {accountId} not found")
    
    performance = service.get_account_performance(db, accountId, start_date=startDate, end_date=endDate)
    
    return {
        "accountId": accountId,
        "accountNumber": account.AccountNumber,
        "accountName": account.AccountName,
        "accountType": account.account_type.TypeName if account.account_type else None,
        "startDate": startDate,
        "endDate": endDate,
        "period": period,
        "performance": performance
    }

# ============================================================================
# ACCOUNT TYPE ENDPOINTS
# ============================================================================

@router.get("/account-types")
def get_account_types(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    isTaxDeferred: Optional[bool] = Query(None),
    isTaxable: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List all account types"""
    service = AccountTypeService()
    skip = (page - 1) * pageSize
    
    account_types = service.get_all(db, skip=skip, limit=pageSize, category=category)
    
    # Apply boolean filtering
    if isTaxDeferred is not None:
        account_types = [at for at in account_types if at.IsTaxDeferred == isTaxDeferred]
    if isTaxable is not None:
        account_types = [at for at in account_types if at.IsTaxable == isTaxable]
    
    # Get total count
    all_types = service.get_all(db, category=category)
    total = len(all_types)
    
    return {
        "accountTypes": [model_to_dict(at) for at in account_types],
        "total": total,
        "page": page,
        "pageSize": len(account_types),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/account-types/{accountTypeId}")
def get_account_type(
    accountTypeId: str = Path(...),
    includeAccounts: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get specific account type"""
    service = AccountTypeService()
    account_type = service.get_by_id(db, accountTypeId)
    
    if not account_type:
        raise HTTPException(status_code=404, detail=f"Account type {accountTypeId} not found")
    
    result = model_to_dict(account_type)
    
    if includeAccounts:
        # Get accounts of this type
        account_service = AccountService()
        accounts = account_service.get_all(db, account_type=account_type.TypeName)
        result['accounts'] = [model_to_dict(a) for a in accounts]
        result['accountCount'] = len(accounts)
    
    return result

# ============================================================================
# COMPLEX DATA EXTRACTION ENDPOINTS
# ============================================================================

@router.get("/households/{householdId}/accounts")
def get_household_accounts(
    householdId: str = Path(...),
    includeHoldings: bool = Query(False),
    includePerformance: bool = Query(False),
    accountType: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get household accounts"""
    service = AccountService()
    
    accounts = service.get_all(db, household_id=householdId, account_type=accountType)
    
    result = {
        "householdId": householdId,
        "accounts": [],
        "totalValue": 0,
        "accountTypes": {},
        "custodians": {}
    }
    
    for account in accounts:
        account_data = model_to_dict(account)
        
        # Add account type name
        if account.account_type:
            account_data['accountTypeName'] = account.account_type.TypeName
            account_data['accountCategory'] = account.account_type.Category
        
        if includeHoldings:
            holdings = service.get_account_holdings(db, account.AccountID)
            account_data['holdings'] = [model_to_dict(h) for h in holdings]
        
        if includePerformance:
            account_data['performance'] = service.get_account_performance(db, account.AccountID)
        
        result["accounts"].append(account_data)
        result["totalValue"] += float(account.Balance) if account.Balance else 0
        
        # Count by account type
        acc_type = account.account_type.TypeName if account.account_type else "Unknown"
        if acc_type not in result["accountTypes"]:
            result["accountTypes"][acc_type] = {"count": 0, "totalValue": 0}
        result["accountTypes"][acc_type]["count"] += 1
        result["accountTypes"][acc_type]["totalValue"] += float(account.Balance) if account.Balance else 0
        
        # Count by custodian
        custodian = account.CustodianName or "Unknown"
        if custodian not in result["custodians"]:
            result["custodians"][custodian] = {"count": 0, "totalValue": 0}
        result["custodians"][custodian]["count"] += 1
        result["custodians"][custodian]["totalValue"] += float(account.Balance) if account.Balance else 0
    
    result["total"] = len(accounts)
    
    return result

@router.get("/clients/{clientId}/accounts")
def get_client_accounts(
    clientId: str = Path(...),
    includeHoldings: bool = Query(False),
    accountType: Optional[str] = Query(None),
    status: Optional[str] = Query("Active"),
    db: Session = Depends(get_db)
):
    """Get client accounts"""
    service = AccountService()
    
    accounts = service.get_all(db, client_id=clientId, account_type=accountType, status=status)
    
    result = {
        "clientId": clientId,
        "accounts": [],
        "totalValue": 0,
        "retirementAccounts": {"count": 0, "totalValue": 0},
        "taxableAccounts": {"count": 0, "totalValue": 0},
        "managedAccounts": {"count": 0, "totalValue": 0}
    }
    
    for account in accounts:
        account_data = model_to_dict(account)
        
        # Add account type details
        if account.account_type:
            account_data['accountTypeName'] = account.account_type.TypeName
            account_data['accountCategory'] = account.account_type.Category
            account_data['isTaxDeferred'] = account.account_type.IsTaxDeferred
        
        if includeHoldings:
            holdings = service.get_account_holdings(db, account.AccountID)
            account_data['holdings'] = [model_to_dict(h) for h in holdings]
        
        result["accounts"].append(account_data)
        
        balance = float(account.Balance) if account.Balance else 0
        result["totalValue"] += balance
        
        # Categorize accounts
        if account.account_type and account.account_type.IsTaxDeferred:
            result["retirementAccounts"]["count"] += 1
            result["retirementAccounts"]["totalValue"] += balance
        elif account.IsTaxable:
            result["taxableAccounts"]["count"] += 1
            result["taxableAccounts"]["totalValue"] += balance
        
        if account.IsManaged:
            result["managedAccounts"]["count"] += 1
            result["managedAccounts"]["totalValue"] += balance
    
    result["total"] = len(accounts)
    
    return result

# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics/accounts")
def get_account_analytics(
    groupBy: Optional[str] = Query("accountType"),
    db: Session = Depends(get_db)
):
    """Get account analytics"""
    service = AccountService()
    
    # Get all accounts for analytics
    all_accounts = service.get_all(db, limit=1000)
    
    # Calculate basic counts
    active_accounts = [a for a in all_accounts if a.Status == "Active"]
    inactive_accounts = [a for a in all_accounts if a.Status == "Inactive"]
    managed_accounts = [a for a in all_accounts if a.IsManaged]
    taxable_accounts = [a for a in all_accounts if a.IsTaxable]
    
    # Calculate totals
    total_value = sum(float(a.Balance) if a.Balance else 0 for a in all_accounts)
    average_value = total_value / len(all_accounts) if all_accounts else 0
    
    # Count by account type
    type_counts = {}
    for account in all_accounts:
        type_name = account.account_type.TypeName if account.account_type else "Unknown"
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # Count by custodian
    custodian_counts = {}
    for account in all_accounts:
        custodian = account.CustodianName or "Unknown"
        custodian_counts[custodian] = custodian_counts.get(custodian, 0) + 1
    
    analytics = {
        "total_accounts": len(all_accounts),
        "active_accounts": len(active_accounts),
        "inactive_accounts": len(inactive_accounts),
        "by_account_type": type_counts,
        "by_custodian": custodian_counts,
        "total_value": total_value,
        "average_account_value": average_value,
        "managed_accounts": len(managed_accounts),
        "taxable_accounts": len(taxable_accounts),
        "accounts_over_500k": len([a for a in all_accounts if a.Balance and float(a.Balance) > 500000]),
        "accounts_over_1m": len([a for a in all_accounts if a.Balance and float(a.Balance) > 1000000])
    }
    
    return analytics

@router.get("/analytics/account-types")
def get_account_type_analytics(
    db: Session = Depends(get_db)
):
    """Get account type analytics"""
    service = AccountTypeService()
    
    all_types = service.get_all(db, limit=100)
    
    # Count by category
    category_counts = {}
    tax_deferred_count = 0
    taxable_count = 0
    
    for acc_type in all_types:
        category = acc_type.Category or "Unknown"
        category_counts[category] = category_counts.get(category, 0) + 1
        
        if acc_type.IsTaxDeferred:
            tax_deferred_count += 1
        if acc_type.IsTaxable:
            taxable_count += 1
    
    analytics = {
        "total_account_types": len(all_types),
        "by_category": category_counts,
        "tax_deferred_types": tax_deferred_count,
        "taxable_types": taxable_count,
        "usage_statistics": "Account usage statistics would require account counts by type"
    }
    
    return analytics
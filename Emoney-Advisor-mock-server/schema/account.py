# schema/account.py - Version 4: Account Management Schemas

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for created/modified timestamps"""
    created_date: datetime
    modified_date: datetime

# ============================================================================
# ACCOUNT TYPE SCHEMAS
# ============================================================================

class AccountTypeBase(BaseModel):
    """Base Account Type schema"""
    type_name: str = Field(..., description="Account type name")
    category: str = Field(default="Taxable", description="Account category")
    description: Optional[str] = Field(None, description="Account type description")
    is_tax_deferred: bool = Field(default=False, description="Is tax deferred account")
    is_taxable: bool = Field(default=True, description="Is taxable account")

class AccountTypeCreate(AccountTypeBase):
    """Schema for creating a new account type"""
    pass

class AccountTypeUpdate(BaseModel):
    """Schema for updating an account type"""
    type_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_tax_deferred: Optional[bool] = None
    is_taxable: Optional[bool] = None

class AccountType(AccountTypeBase):
    """Complete Account Type schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    account_type_id: str = Field(..., description="Unique account type identifier")
    created_date: datetime

# ============================================================================
# ACCOUNT SCHEMAS
# ============================================================================

class AccountBase(BaseModel):
    """Base Account schema"""
    account_number: str = Field(..., description="Account number")
    account_name: str = Field(..., description="Account name")
    balance: Optional[Decimal] = Field(default=Decimal('0.00'), description="Account balance")
    as_of_date: Optional[datetime] = Field(None, description="Balance as of date")
    custodian_name: Optional[str] = Field(None, description="Custodian/institution name")
    status: str = Field(default="Active", description="Account status")
    is_managed: bool = Field(default=False, description="Is professionally managed")
    is_taxable: bool = Field(default=True, description="Is taxable account")
    owner_type: str = Field(default="Individual", description="Account owner type")

class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")
    account_type_id: str = Field(..., description="Account type ID")

class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    account_name: Optional[str] = None
    balance: Optional[Decimal] = None
    as_of_date: Optional[datetime] = None
    custodian_name: Optional[str] = None
    status: Optional[str] = None
    is_managed: Optional[bool] = None
    is_taxable: Optional[bool] = None
    owner_type: Optional[str] = None

class Account(AccountBase, TimestampMixin):
    """Complete Account schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: str = Field(..., description="Unique account identifier")
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")
    account_type_id: str = Field(..., description="Account type ID")

class AccountWithRelations(Account):
    """Account with related entities"""
    account_type: Optional[AccountType] = None
    assets: List['Asset'] = []

class AccountPerformance(BaseModel):
    """Account performance metrics"""
    account_id: str
    account_name: str
    balance: Optional[Decimal] = None
    total_holdings_value: Decimal
    total_cost_basis: Decimal
    total_unrealized_gain: Decimal
    unrealized_gain_percent: Decimal
    holdings_count: int
    as_of_date: Optional[datetime] = None

# ============================================================================
# schema/asset.py - Version 4: Asset Management Schemas
# ============================================================================






# ASSET CLASS SCHEMAS
class AssetClassBase(BaseModel):
    """Base Asset Class schema"""
    class_name: str = Field(..., description="Asset class name")
    category: Optional[str] = Field(None, description="Asset class category")
    description: Optional[str] = Field(None, description="Asset class description")
    risk_level: Optional[str] = Field(default="Moderate", description="Risk level")
    status: str = Field(default="Active", description="Asset class status")

class AssetClassCreate(AssetClassBase):
    """Schema for creating a new asset class"""
    pass

class AssetClassUpdate(BaseModel):
    """Schema for updating an asset class"""
    class_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None

class AssetClass(AssetClassBase):
    """Complete Asset Class schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    asset_class_id: str = Field(..., description="Unique asset class identifier")
    created_date: datetime

# ============================================================================
# ASSET SCHEMAS
# ============================================================================

class AssetBase(BaseModel):
    """Base Asset schema"""
    security_name: str = Field(..., description="Security/asset name")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    cusip: Optional[str] = Field(None, description="CUSIP identifier")
    shares: Optional[Decimal] = Field(default=Decimal('0.000000'), description="Number of shares")
    price: Optional[Decimal] = Field(default=Decimal('0.0000'), description="Current price per share")
    value: Optional[Decimal] = Field(default=Decimal('0.00'), description="Current market value")
    cost_basis: Optional[Decimal] = Field(default=Decimal('0.00'), description="Cost basis")
    unrealized_gain: Optional[Decimal] = Field(default=Decimal('0.00'), description="Unrealized gain/loss")
    unrealized_gain_percent: Optional[Decimal] = Field(default=Decimal('0.00'), description="Unrealized gain percentage")
    as_of_date: Optional[datetime] = Field(None, description="Price/value as of date")
    status: str = Field(default="Active", description="Asset status")

class AssetCreate(AssetBase):
    """Schema for creating a new asset"""
    account_id: str = Field(..., description="Associated account ID")
    asset_class_id: Optional[str] = Field(None, description="Asset class ID")

class AssetUpdate(BaseModel):
    """Schema for updating an asset"""
    security_name: Optional[str] = None
    symbol: Optional[str] = None
    cusip: Optional[str] = None
    shares: Optional[Decimal] = None
    price: Optional[Decimal] = None
    value: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    unrealized_gain: Optional[Decimal] = None
    unrealized_gain_percent: Optional[Decimal] = None
    as_of_date: Optional[datetime] = None
    status: Optional[str] = None

class Asset(AssetBase, TimestampMixin):
    """Complete Asset schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    asset_id: str = Field(..., description="Unique asset identifier")
    account_id: str = Field(..., description="Associated account ID")
    asset_class_id: Optional[str] = Field(None, description="Asset class ID")

class AssetWithRelations(Asset):
    """Asset with related entities"""
    account: Optional[Account] = None
    asset_class: Optional[AssetClass] = None

class AssetPerformance(BaseModel):
    """Asset performance metrics"""
    asset_id: str
    security_name: str
    symbol: Optional[str] = None
    shares: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    unrealized_gain: Optional[Decimal] = None
    unrealized_gain_percent: Optional[Decimal] = None
    asset_class: Optional[str] = None
    as_of_date: Optional[datetime] = None

# ============================================================================
# LIABILITY SCHEMAS
# ============================================================================

class LiabilityBase(BaseModel):
    """Base Liability schema"""
    liability_name: str = Field(..., description="Liability name")
    liability_type: str = Field(default="Other", description="Type of liability")
    current_balance: Optional[Decimal] = Field(default=Decimal('0.00'), description="Current balance")
    original_amount: Optional[Decimal] = Field(default=Decimal('0.00'), description="Original loan amount")
    interest_rate: Optional[Decimal] = Field(default=Decimal('0.0000'), description="Interest rate")
    monthly_payment: Optional[Decimal] = Field(default=Decimal('0.00'), description="Monthly payment")
    maturity_date: Optional[datetime] = Field(None, description="Maturity/payoff date")
    lender: Optional[str] = Field(None, description="Lender/creditor name")
    status: str = Field(default="Active", description="Liability status")

class LiabilityCreate(LiabilityBase):
    """Schema for creating a new liability"""
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")

class LiabilityUpdate(BaseModel):
    """Schema for updating a liability"""
    liability_name: Optional[str] = None
    liability_type: Optional[str] = None
    current_balance: Optional[Decimal] = None
    original_amount: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    monthly_payment: Optional[Decimal] = None
    maturity_date: Optional[datetime] = None
    lender: Optional[str] = None
    status: Optional[str] = None

class Liability(LiabilityBase, TimestampMixin):
    """Complete Liability schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    liability_id: str = Field(..., description="Unique liability identifier")
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")

class LiabilityWithRelations(Liability):
    """Liability with related entities"""
    pass

class LiabilitySchedule(BaseModel):
    """Liability payment schedule"""
    liability_id: str
    liability_name: str
    current_balance: Optional[Decimal] = None
    monthly_payment: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    remaining_payments: int
    estimated_payoff_months: int
    total_interest_remaining: Decimal

# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class AccountSearchParams(BaseModel):
    """Parameters for account search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    household_id: Optional[str] = Field(None, description="Filter by household")
    account_type: Optional[str] = Field(None, description="Filter by account type")
    status: Optional[str] = Field(None, description="Filter by status")
    custodian_name: Optional[str] = Field(None, description="Filter by custodian")
    is_managed: Optional[bool] = Field(None, description="Filter by managed accounts")
    min_balance: Optional[Decimal] = Field(None, description="Minimum balance filter")

class AssetSearchParams(BaseModel):
    """Parameters for asset search"""
    account_id: Optional[str] = Field(None, description="Filter by account")
    asset_class_id: Optional[str] = Field(None, description="Filter by asset class")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    status: Optional[str] = Field(None, description="Filter by status")
    min_value: Optional[Decimal] = Field(None, description="Minimum value filter")

class LiabilitySearchParams(BaseModel):
    """Parameters for liability search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    household_id: Optional[str] = Field(None, description="Filter by household")
    liability_type: Optional[str] = Field(None, description="Filter by liability type")
    status: Optional[str] = Field(None, description="Filter by status")
    lender: Optional[str] = Field(None, description="Filter by lender")

# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int = Field(..., description="Total number of records")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")
    has_more: bool = Field(..., description="Whether more records are available")

class PaginatedAccountsResponse(PaginatedResponse):
    """Paginated accounts response"""
    items: List[Account] = []

class PaginatedAssetsResponse(PaginatedResponse):
    """Paginated assets response"""
    items: List[Asset] = []

class PaginatedLiabilitiesResponse(PaginatedResponse):
    """Paginated liabilities response"""
    items: List[Liability] = []

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class AccountResponse(BaseModel):
    """Standard account response"""
    status: str = "success"
    data: Account

class AssetResponse(BaseModel):
    """Standard asset response"""
    status: str = "success"
    data: Asset

class LiabilityResponse(BaseModel):
    """Standard liability response"""
    status: str = "success"
    data: Liability

class AccountPerformanceResponse(BaseModel):
    """Account performance response"""
    status: str = "success"
    data: AccountPerformance

class AssetPerformanceResponse(BaseModel):
    """Asset performance response"""
    status: str = "success"
    data: AssetPerformance

class LiabilityScheduleResponse(BaseModel):
    """Liability schedule response"""
    status: str = "success"
    data: LiabilitySchedule

# ============================================================================
# PORTFOLIO SCHEMAS
# ============================================================================

class PortfolioSummary(BaseModel):
    """Portfolio summary for an account or household"""
    total_value: Decimal
    total_cost_basis: Decimal
    total_unrealized_gain: Decimal
    unrealized_gain_percent: Decimal
    asset_allocation: Dict[str, Decimal]  # Asset class -> percentage
    top_holdings: List[Dict[str, Any]]

class HoldingsSummary(BaseModel):
    """Holdings summary"""
    account_id: str
    account_name: str
    holdings: List[Asset]
    total_value: Decimal
    as_of_date: Optional[datetime] = None

# Forward references for relationships
AccountWithRelations.model_rebuild()
AssetWithRelations.model_rebuild()
LiabilityWithRelations.model_rebuild()
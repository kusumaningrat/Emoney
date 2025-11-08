from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import PaginatedResponse, BaseFilterParams
from .enums import AccountType, OwnershipType, TaxStatus, LiabilityType, PaymentFrequency


# Base schemas
class AccountBase(BaseModel):
    client_id: str = Field(..., description="ID of client account belongs to")
    name: str = Field(..., description="Account name")
    description: Optional[str] = Field(None, description="Account description")
    institution: str = Field(..., description="Financial institution")
    account_number: str = Field(..., description="Account number (masked)")
    type: str = Field(..., description="Account type")
    ownership: str = Field(..., description="Account ownership")
    tax_status: Optional[str] = Field(None, description="Account tax status")
    is_external: bool = Field(False, description="Whether account is external")
    created_by: str = Field(..., description="ID of user who created the account")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the account")


class LiabilityBase(BaseModel):
    client_id: str = Field(..., description="ID of client liability belongs to")
    plan_id: Optional[str] = Field(None, description="ID of plan liability belongs to")
    name: str = Field(..., description="Liability name")
    description: Optional[str] = Field(None, description="Liability description")
    type: str = Field(..., description="Liability type")
    balance: float = Field(..., description="Current balance")
    original_balance: Optional[float] = Field(None, description="Original balance")
    interest_rate: float = Field(..., description="Annual interest rate")
    payment_amount: Optional[float] = Field(None, description="Regular payment amount")
    payment_frequency: Optional[str] = Field(None, description="Payment frequency")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    ownership: str = Field(..., description="Liability ownership")
    account_id: Optional[str] = Field(None, description="Associated account ID")
    created_by: str = Field(..., description="ID of user who created the liability")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the liability")


class AccountTypeBase(BaseModel):
    name: str = Field(..., description="Account type name")
    description: Optional[str] = Field(None, description="Account type description")
    category: str = Field(..., description="Account category (Asset, Liability)")


# Create schemas
class AccountCreate(AccountBase):
    pass


class LiabilityCreate(LiabilityBase):
    pass


class AccountTypeCreate(AccountTypeBase):
    pass


# Update schemas
class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Account name")
    description: Optional[str] = Field(None, description="Account description")
    institution: Optional[str] = Field(None, description="Financial institution")
    account_number: Optional[str] = Field(None, description="Account number (masked)")
    type: Optional[str] = Field(None, description="Account type")
    ownership: Optional[str] = Field(None, description="Account ownership")
    tax_status: Optional[str] = Field(None, description="Account tax status")
    is_external: Optional[bool] = Field(None, description="Whether account is external")
    updated_by: str = Field(..., description="ID of user who updated the account")


class LiabilityUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Liability name")
    description: Optional[str] = Field(None, description="Liability description")
    type: Optional[str] = Field(None, description="Liability type")
    balance: Optional[float] = Field(None, description="Current balance")
    original_balance: Optional[float] = Field(None, description="Original balance")
    interest_rate: Optional[float] = Field(None, description="Annual interest rate")
    payment_amount: Optional[float] = Field(None, description="Regular payment amount")
    payment_frequency: Optional[str] = Field(None, description="Payment frequency")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    ownership: Optional[str] = Field(None, description="Liability ownership")
    account_id: Optional[str] = Field(None, description="Associated account ID")
    updated_by: str = Field(..., description="ID of user who updated the liability")


class AccountTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Account type name")
    description: Optional[str] = Field(None, description="Account type description")
    category: Optional[str] = Field(None, description="Account category (Asset, Liability)")


# Response models
class AccountResponse(BaseModel):
    id: str = Field(..., description="Account ID")
    clientId: str = Field(..., description="ID of client account belongs to")
    name: str = Field(..., description="Account name")
    description: Optional[str] = Field(None, description="Account description")
    institution: str = Field(..., description="Financial institution")
    accountNumber: str = Field(..., description="Account number (masked)")
    type: str = Field(..., description="Account type")
    ownership: str = Field(..., description="Account ownership")
    taxStatus: Optional[str] = Field(None, description="Account tax status")
    isExternal: bool = Field(False, description="Whether account is external")
    createdBy: str = Field(..., description="ID of user who created the account")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the account")
    createdAt: datetime = Field(..., description="Timestamp when account was created")
    updatedAt: datetime = Field(..., description="Timestamp when account was last updated")
    
    model_config = {
        "from_attributes": True
    }


class LiabilityResponse(BaseModel):
    id: str = Field(..., description="Liability ID")
    clientId: str = Field(..., description="ID of client liability belongs to")
    planId: Optional[str] = Field(None, description="ID of plan liability belongs to")
    name: str = Field(..., description="Liability name")
    description: Optional[str] = Field(None, description="Liability description")
    type: str = Field(..., description="Liability type")
    balance: float = Field(..., description="Current balance")
    originalBalance: Optional[float] = Field(None, description="Original balance")
    interestRate: float = Field(..., description="Annual interest rate")
    paymentAmount: Optional[float] = Field(None, description="Regular payment amount")
    paymentFrequency: Optional[str] = Field(None, description="Payment frequency")
    startDate: Optional[date] = Field(None, description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    ownership: str = Field(..., description="Liability ownership")
    accountId: Optional[str] = Field(None, description="Associated account ID")
    createdBy: str = Field(..., description="ID of user who created the liability")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the liability")
    createdAt: datetime = Field(..., description="Timestamp when liability was created")
    updatedAt: datetime = Field(..., description="Timestamp when liability was last updated")
    
    model_config = {
        "from_attributes": True
    }


class AccountTypeResponse(BaseModel):
    id: str = Field(..., description="Account type ID")
    name: str = Field(..., description="Account type name")
    description: Optional[str] = Field(None, description="Account type description")
    category: str = Field(..., description="Account category (Asset, Liability)")
    createdAt: datetime = Field(..., description="Timestamp when account type was created")
    updatedAt: datetime = Field(..., description="Timestamp when account type was last updated")
    
    model_config = {
        "from_attributes": True
    }


# List response classes
class AccountListResponse(BaseModel):
    accounts: List[AccountResponse] = Field(..., description="List of accounts")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class LiabilityListResponse(BaseModel):
    liabilities: List[LiabilityResponse] = Field(..., description="List of liabilities")
    totalBalance: float = Field(..., description="Total liability balance")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class AccountTypeListResponse(BaseModel):
    accountTypes: List[AccountTypeResponse] = Field(..., description="List of account types")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class AccountFilterParams(BaseFilterParams):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    type: Optional[str] = Field(None, description="Filter by account type")
    ownership: Optional[str] = Field(None, description="Filter by ownership")
    is_external: Optional[bool] = Field(None, description="Filter by external status")
    institution: Optional[str] = Field(None, description="Filter by institution")
    sort: str = Field("name", description="Sort field")


class LiabilityFilterParams(BaseFilterParams):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    type: Optional[str] = Field(None, description="Filter by liability type")
    ownership: Optional[str] = Field(None, description="Filter by ownership")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    balance_gt: Optional[float] = Field(None, description="Filter by minimum balance")
    sort: str = Field("balance", description="Sort field")


class AccountTypeFilterParams(BaseFilterParams):
    category: Optional[str] = Field(None, description="Filter by category")
    sort: str = Field("name", description="Sort field")
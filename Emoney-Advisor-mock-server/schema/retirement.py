# retirement.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class RetirementPlanType(str, Enum):
    TRADITIONAL_IRA = "Traditional IRA"
    ROTH_IRA = "Roth IRA"
    SIMPLE_IRA = "SIMPLE IRA"
    SEP_IRA = "SEP IRA"
    FOUR_01K = "401(k)"
    FOUR_03B = "403(b)"
    FOUR_57B = "457(b)"
    PENSION = "Pension"
    OTHER = "Other"


class RetirementPlanStatus(str, Enum):
    ACTIVE = "Active"
    ROLLOVER = "Rollover"
    INACTIVE = "Inactive"
    TERMINATED = "Terminated"


# Base schemas
class RetirementBase(BaseModel):
    client_id: str = Field(..., description="ID of client retirement plan belongs to")
    plan_name: str = Field(..., description="Retirement plan name")
    type: str = Field(..., description="Retirement plan type")
    status: str = Field(..., description="Plan status")
    provider: str = Field(..., description="Plan provider/custodian")
    account_number: str = Field(..., description="Account number")
    current_balance: float = Field(..., description="Current plan balance")
    annual_contribution: Optional[float] = Field(None, description="Annual contribution amount")
    employer_match: Optional[float] = Field(None, description="Employer match percentage")
    allocation: Dict[str, Any] = Field(..., description="Investment allocation")
    start_date: date = Field(..., description="Plan start date")
    beneficiaries: Optional[List[Dict[str, Any]]] = Field(None, description="List of beneficiaries")
    document_ids: Optional[List[str]] = Field(None, description="IDs of related documents")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_by: str = Field(..., description="ID of user who created the retirement plan record")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the retirement plan record")


# Response models with ID and timestamps
class RetirementResponse(BaseModel):
    id: str = Field(..., description="Retirement plan ID")
    clientId: str = Field(..., description="ID of client retirement plan belongs to")
    planName: str = Field(..., description="Retirement plan name")
    type: str = Field(..., description="Retirement plan type")
    status: str = Field(..., description="Plan status")
    provider: str = Field(..., description="Plan provider/custodian")
    accountNumber: str = Field(..., description="Account number")
    currentBalance: float = Field(..., description="Current plan balance")
    annualContribution: Optional[float] = Field(None, description="Annual contribution amount")
    employerMatch: Optional[float] = Field(None, description="Employer match percentage")
    allocation: Dict[str, Any] = Field(..., description="Investment allocation")
    startDate: date = Field(..., description="Plan start date")
    beneficiaries: Optional[List[Dict[str, Any]]] = Field(None, description="List of beneficiaries")
    documentIds: Optional[List[str]] = Field(None, description="IDs of related documents")
    notes: Optional[str] = Field(None, description="Additional notes")
    createdBy: str = Field(..., description="ID of user who created the retirement plan record")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the retirement plan record")
    createdAt: datetime = Field(..., description="Timestamp when retirement plan was created")
    updatedAt: datetime = Field(..., description="Timestamp when retirement plan was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Pagination response schema
class PaginatedResponse(BaseModel):
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of records per page")
    total_pages: int = Field(..., description="Total number of pages")


# Paginated list response classes
class RetirementListResponse(BaseModel):
    retirementPlans: List[Dict[str, Any]] = Field(..., description="List of retirement plans")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class RetirementFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    type: Optional[str] = Field(None, description="Filter by plan type")
    status: Optional[str] = Field(None, description="Filter by plan status")
    provider: Optional[str] = Field(None, description="Filter by provider")
    start_date_after: Optional[str] = Field(None, description="Filter by start date")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("plan_name", description="Sort field")
    count: bool = Field(False, description="Return count only")
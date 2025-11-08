# insurance.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class InsuranceType(str, Enum):
    LIFE = "Life"
    HEALTH = "Health"
    AUTO = "Auto"
    HOME = "Home"
    UMBRELLA = "Umbrella"
    DISABILITY = "Disability"
    LONG_TERM_CARE = "Long-term Care"
    OTHER = "Other"


class InsuranceStatus(str, Enum):
    ACTIVE = "Active"
    LAPSED = "Lapsed"
    CANCELLED = "Cancelled"
    PENDING = "Pending Approval"


# Base schemas
class InsuranceBase(BaseModel):
    client_id: str = Field(..., description="ID of client insurance belongs to")
    policy_number: str = Field(..., description="Insurance policy number")
    provider: str = Field(..., description="Insurance provider name")
    type: str = Field(..., description="Insurance type")
    status: str = Field(..., description="Policy status")
    premium_amount: float = Field(..., description="Premium amount")
    premium_frequency: str = Field(..., description="Premium payment frequency")
    coverage_amount: float = Field(..., description="Coverage amount")
    deductible: Optional[float] = Field(None, description="Deductible amount")
    beneficiaries: Optional[List[Dict[str, Any]]] = Field(None, description="List of beneficiaries")
    start_date: date = Field(..., description="Policy start date")
    end_date: Optional[date] = Field(None, description="Policy end date")
    document_ids: Optional[List[str]] = Field(None, description="IDs of related documents")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_by: str = Field(..., description="ID of user who created the insurance record")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the insurance record")


# Response models with ID and timestamps
class InsuranceResponse(BaseModel):
    id: str = Field(..., description="Insurance ID")
    clientId: str = Field(..., description="ID of client insurance belongs to")
    policyNumber: str = Field(..., description="Insurance policy number")
    provider: str = Field(..., description="Insurance provider name")
    type: str = Field(..., description="Insurance type")
    status: str = Field(..., description="Policy status")
    premiumAmount: float = Field(..., description="Premium amount")
    premiumFrequency: str = Field(..., description="Premium payment frequency")
    coverageAmount: float = Field(..., description="Coverage amount")
    deductible: Optional[float] = Field(None, description="Deductible amount")
    beneficiaries: Optional[List[Dict[str, Any]]] = Field(None, description="List of beneficiaries")
    startDate: date = Field(..., description="Policy start date")
    endDate: Optional[date] = Field(None, description="Policy end date")
    documentIds: Optional[List[str]] = Field(None, description="IDs of related documents")
    notes: Optional[str] = Field(None, description="Additional notes")
    createdBy: str = Field(..., description="ID of user who created the insurance record")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the insurance record")
    createdAt: datetime = Field(..., description="Timestamp when insurance was created")
    updatedAt: datetime = Field(..., description="Timestamp when insurance was last updated")
    
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
class InsuranceListResponse(BaseModel):
    insurances: List[Dict[str, Any]] = Field(..., description="List of insurance policies")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class InsuranceFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    type: Optional[str] = Field(None, description="Filter by insurance type")
    status: Optional[str] = Field(None, description="Filter by policy status")
    provider: Optional[str] = Field(None, description="Filter by provider")
    start_date_after: Optional[str] = Field(None, description="Filter by start date")
    end_date_before: Optional[str] = Field(None, description="Filter by end date")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("start_date", description="Sort field")
    count: bool = Field(False, description="Return count only")
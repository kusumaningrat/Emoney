# identity.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class IdentityDocumentType(str, Enum):
    PASSPORT = "Passport"
    DRIVERS_LICENSE = "Driver's License"
    BIRTH_CERTIFICATE = "Birth Certificate"
    SOCIAL_SECURITY = "Social Security Card"
    OTHER = "Other"


# Base schemas
class IdentityBase(BaseModel):
    client_id: str = Field(..., description="ID of client identity belongs to")
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: date = Field(..., description="Date of birth")
    ssn: Optional[str] = Field(None, description="Social Security Number")
    citizenship: str = Field(..., description="Citizenship status")
    residence_address: Dict[str, Any] = Field(..., description="Current residence address")
    mailing_address: Optional[Dict[str, Any]] = Field(None, description="Mailing address if different")
    phone_number: str = Field(..., description="Primary phone number")
    email: str = Field(..., description="Primary email address")
    document_ids: Optional[List[str]] = Field(None, description="IDs of identity documents")
    created_by: str = Field(..., description="ID of user who created the identity record")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the identity record")


# Response models with ID and timestamps
class IdentityResponse(BaseModel):
    id: str = Field(..., description="Identity ID")
    clientId: str = Field(..., description="ID of client identity belongs to")
    fullName: str = Field(..., description="Full legal name")
    dateOfBirth: date = Field(..., description="Date of birth")
    ssn: Optional[str] = Field(None, description="Social Security Number")
    citizenship: str = Field(..., description="Citizenship status")
    residenceAddress: Dict[str, Any] = Field(..., description="Current residence address")
    mailingAddress: Optional[Dict[str, Any]] = Field(None, description="Mailing address if different")
    phoneNumber: str = Field(..., description="Primary phone number")
    email: str = Field(..., description="Primary email address")
    documentIds: Optional[List[str]] = Field(None, description="IDs of identity documents")
    createdBy: str = Field(..., description="ID of user who created the identity record")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the identity record")
    createdAt: datetime = Field(..., description="Timestamp when identity was created")
    updatedAt: datetime = Field(..., description="Timestamp when identity was last updated")
    
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
class IdentityListResponse(BaseModel):
    identities: List[Dict[str, Any]] = Field(..., description="List of identities")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class IdentityFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    citizenship: Optional[str] = Field(None, description="Filter by citizenship")
    created_after: Optional[str] = Field(None, description="Filter by creation date")
    updated_after: Optional[str] = Field(None, description="Filter by update date")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("full_name", description="Sort field")
    count: bool = Field(False, description="Return count only")
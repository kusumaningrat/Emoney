from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import PaginatedResponse, BaseFilterParams
from .enums import MaritalStatus, ClientStatus


# Base schemas
class ClientBase(BaseModel):
    firm_id: str = Field(..., description="ID of firm client belongs to")
    first_name: str = Field(..., description="Client first name")
    last_name: str = Field(..., description="Client last name")
    email: Optional[EmailStr] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    marital_status: str = Field(..., description="Client marital status")
    previous_marriages: bool = Field(False, description="Whether client had previous marriages")
    date_of_birth: date = Field(..., description="Client date of birth")
    owning_advisor: str = Field(..., description="ID of client's primary advisor")
    external_id: Optional[str] = Field(None, description="External system ID")
    created_by: str = Field(..., description="ID of user who created the client")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the client")


class SpouseBase(BaseModel):
    client_id: str = Field(..., description="ID of client spouse belongs to")
    first_name: str = Field(..., description="Spouse first name")
    last_name: str = Field(..., description="Spouse last name")
    email: Optional[EmailStr] = Field(None, description="Spouse email")
    phone: Optional[str] = Field(None, description="Spouse phone")
    date_of_birth: date = Field(..., description="Spouse date of birth")
    previous_marriages: bool = Field(False, description="Whether spouse had previous marriages")
    created_by: str = Field(..., description="ID of user who created the spouse")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the spouse")


class ContactBase(BaseModel):
    client_id: str = Field(..., description="ID of client contact belongs to")
    type: str = Field(..., description="Contact type (Primary, Work, Emergency)")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    is_preferred: bool = Field(False, description="Whether this is the preferred contact")
    created_by: str = Field(..., description="ID of user who created the contact")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the contact")


# Create schemas
class ClientCreate(ClientBase):
    pass


class SpouseCreate(SpouseBase):
    pass


class ContactCreate(ContactBase):
    pass


# Update schemas
class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Client first name")
    last_name: Optional[str] = Field(None, description="Client last name")
    email: Optional[EmailStr] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    marital_status: Optional[str] = Field(None, description="Client marital status")
    previous_marriages: Optional[bool] = Field(None, description="Whether client had previous marriages")
    date_of_birth: Optional[date] = Field(None, description="Client date of birth")
    owning_advisor: Optional[str] = Field(None, description="ID of client's primary advisor")
    external_id: Optional[str] = Field(None, description="External system ID")
    updated_by: str = Field(..., description="ID of user who updated the client")


class SpouseUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Spouse first name")
    last_name: Optional[str] = Field(None, description="Spouse last name")
    email: Optional[EmailStr] = Field(None, description="Spouse email")
    phone: Optional[str] = Field(None, description="Spouse phone")
    date_of_birth: Optional[date] = Field(None, description="Spouse date of birth")
    previous_marriages: Optional[bool] = Field(None, description="Whether spouse had previous marriages")
    updated_by: str = Field(..., description="ID of user who updated the spouse")


class ContactUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Contact type (Primary, Work, Emergency)")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    is_preferred: Optional[bool] = Field(None, description="Whether this is the preferred contact")
    updated_by: str = Field(..., description="ID of user who updated the contact")


# Response models
class ClientResponse(BaseModel):
    id: str = Field(..., description="Client ID")
    firmId: str = Field(..., description="ID of firm client belongs to")
    firstName: str = Field(..., description="Client first name")
    lastName: str = Field(..., description="Client last name")
    email: Optional[str] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    maritalStatus: str = Field(..., description="Client marital status")
    previousMarriages: bool = Field(False, description="Whether client had previous marriages")
    dateOfBirth: date = Field(..., description="Client date of birth")
    owningAdvisor: str = Field(..., description="ID of client's primary advisor")
    externalId: Optional[str] = Field(None, description="External system ID")
    hasSpouse: bool = Field(False, description="Whether client has a spouse")
    createdBy: str = Field(..., description="ID of user who created the client")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the client")
    createdAt: datetime = Field(..., description="Timestamp when client was created")
    updatedAt: datetime = Field(..., description="Timestamp when client was last updated")
    
    model_config = {
        "from_attributes": True
    }


class SpouseResponse(BaseModel):
    id: str = Field(..., description="Spouse ID")
    clientId: str = Field(..., description="ID of client spouse belongs to")
    firstName: str = Field(..., description="Spouse first name")
    lastName: str = Field(..., description="Spouse last name")
    email: Optional[str] = Field(None, description="Spouse email")
    phone: Optional[str] = Field(None, description="Spouse phone")
    dateOfBirth: date = Field(..., description="Spouse date of birth")
    previousMarriages: bool = Field(False, description="Whether spouse had previous marriages")
    createdBy: str = Field(..., description="ID of user who created the spouse")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the spouse")
    createdAt: datetime = Field(..., description="Timestamp when spouse was created")
    updatedAt: datetime = Field(..., description="Timestamp when spouse was last updated")
    
    model_config = {
        "from_attributes": True
    }


class ContactResponse(BaseModel):
    id: str = Field(..., description="Contact ID")
    clientId: str = Field(..., description="ID of client contact belongs to")
    type: str = Field(..., description="Contact type (Primary, Work, Emergency)")
    addressLine1: Optional[str] = Field(None, description="Address line 1")
    addressLine2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postalCode: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    isPreferred: bool = Field(False, description="Whether this is the preferred contact")
    createdBy: str = Field(..., description="ID of user who created the contact")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the contact")
    createdAt: datetime = Field(..., description="Timestamp when contact was created")
    updatedAt: datetime = Field(..., description="Timestamp when contact was last updated")
    
    model_config = {
        "from_attributes": True
    }


# List response classes
class ClientListResponse(BaseModel):
    clients: List[ClientResponse] = Field(..., description="List of clients")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class SpouseListResponse(BaseModel):
    spouses: List[SpouseResponse] = Field(..., description="List of spouses")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class ContactListResponse(BaseModel):
    contacts: List[ContactResponse] = Field(..., description="List of contacts")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class ClientFilterParams(BaseFilterParams):
    firm_id: Optional[str] = Field(None, description="Filter by firm ID")
    marital_status: Optional[str] = Field(None, description="Filter by marital status")
    owning_advisor: Optional[str] = Field(None, description="Filter by owning advisor")
    name: Optional[str] = Field(None, description="Filter by name (first or last)")
    sort: str = Field("last_name", description="Sort field")


class SpouseFilterParams(BaseFilterParams):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    name: Optional[str] = Field(None, description="Filter by name (first or last)")
    sort: str = Field("last_name", description="Sort field")


class ContactFilterParams(BaseFilterParams):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    type: Optional[str] = Field(None, description="Filter by contact type")
    is_preferred: Optional[bool] = Field(None, description="Filter by preferred status")
    sort: str = Field("type", description="Sort field")
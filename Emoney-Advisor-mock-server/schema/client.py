# schema/client.py - Version 2: Client & Household Schemas

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
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
# CLIENT SCHEMAS
# ============================================================================

class ClientBase(BaseModel):
    """Base Client schema with common fields"""
    first_name: str = Field(..., description="Client's first name")
    last_name: str = Field(..., description="Client's last name")
    middle_name: Optional[str] = Field(None, description="Client's middle name")
    email: Optional[str] = Field(None, description="Client's email address")
    phone: Optional[str] = Field(None, description="Client's phone number")
    date_of_birth: Optional[datetime] = Field(None, description="Client's date of birth")
    gender: Optional[str] = Field(None, description="Client's gender")
    marital_status: Optional[str] = Field(None, description="Client's marital status")
    status: str = Field(default="Active", description="Client status")
    advisor_id: Optional[str] = Field(None, description="Assigned advisor ID")
    firm_id: Optional[str] = Field(None, description="Firm ID")

class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    household_id: Optional[str] = Field(None, description="Household ID")
    owning_user_id: Optional[str] = Field(None, description="Owning user ID")
    office_id: Optional[str] = Field(None, description="Office ID")

class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    status: Optional[str] = None
    advisor_id: Optional[str] = None
    firm_id: Optional[str] = None
    household_id: Optional[str] = None

class Client(ClientBase, TimestampMixin):
    """Complete Client schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    client_id: str = Field(..., description="Unique client identifier")
    household_id: Optional[str] = Field(None, description="Associated household ID")
    spouse_id: Optional[str] = Field(None, description="Associated spouse ID") 
    owning_user_id: Optional[str] = Field(None, description="Owning user ID")
    office_id: Optional[str] = Field(None, description="Office ID")

class ClientWithRelations(Client):
    """Client with related entities"""
    household: Optional['Household'] = None
    spouse: Optional['Spouse'] = None
    contacts: List['Contact'] = []
    relationships: List['Relationship'] = []

# ============================================================================
# HOUSEHOLD SCHEMAS
# ============================================================================

class HouseholdBase(BaseModel):
    """Base Household schema"""
    household_name: str = Field(..., description="Household name")
    net_worth: Optional[Decimal] = Field(default=Decimal('0.00'), description="Household net worth")
    status: str = Field(default="Active", description="Household status")
    risk_tolerance: Optional[str] = Field(default="Moderate", description="Risk tolerance")

class HouseholdCreate(HouseholdBase):
    """Schema for creating a new household"""
    primary_client_id: Optional[str] = Field(None, description="Primary client ID")

class HouseholdUpdate(BaseModel):
    """Schema for updating a household"""
    household_name: Optional[str] = None
    net_worth: Optional[Decimal] = None
    status: Optional[str] = None
    risk_tolerance: Optional[str] = None
    primary_client_id: Optional[str] = None

class Household(HouseholdBase, TimestampMixin):
    """Complete Household schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    household_id: str = Field(..., description="Unique household identifier")
    primary_client_id: Optional[str] = Field(None, description="Primary client ID")

class HouseholdWithMembers(Household):
    """Household with member clients"""
    members: List[Client] = []
    primary_client: Optional[Client] = None

# ============================================================================
# SPOUSE SCHEMAS
# ============================================================================

class SpouseBase(BaseModel):
    """Base Spouse schema"""
    first_name: str = Field(..., description="Spouse's first name")
    last_name: str = Field(..., description="Spouse's last name")
    middle_name: Optional[str] = Field(None, description="Spouse's middle name")
    email: Optional[str] = Field(None, description="Spouse's email address")
    phone: Optional[str] = Field(None, description="Spouse's phone number")
    date_of_birth: Optional[datetime] = Field(None, description="Spouse's date of birth")
    gender: Optional[str] = Field(None, description="Spouse's gender")
    status: str = Field(default="Active", description="Spouse status")

class SpouseCreate(SpouseBase):
    """Schema for creating a new spouse"""
    client_id: str = Field(..., description="Associated client ID")

class SpouseUpdate(BaseModel):
    """Schema for updating a spouse"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    status: Optional[str] = None

class Spouse(SpouseBase, TimestampMixin):
    """Complete Spouse schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    spouse_id: str = Field(..., description="Unique spouse identifier")
    client_id: str = Field(..., description="Associated client ID")

class SpouseWithClient(Spouse):
    """Spouse with associated client"""
    client: Optional[Client] = None

# ============================================================================
# CONTACT SCHEMAS
# ============================================================================

class ContactBase(BaseModel):
    """Base Contact schema"""
    contact_type: str = Field(default="Primary", description="Type of contact")
    first_name: str = Field(..., description="Contact's first name")
    last_name: str = Field(..., description="Contact's last name")
    email: Optional[str] = Field(None, description="Contact's email address")
    phone: Optional[str] = Field(None, description="Contact's phone number")
    address: Optional[str] = Field(None, description="Contact's address")
    city: Optional[str] = Field(None, description="Contact's city")
    state: Optional[str] = Field(None, description="Contact's state")
    zip_code: Optional[str] = Field(None, description="Contact's zip code")
    country: Optional[str] = Field(default="US", description="Contact's country")
    preferred_method: Optional[str] = Field(default="Email", description="Preferred communication method")
    status: str = Field(default="Active", description="Contact status")

class ContactCreate(ContactBase):
    """Schema for creating a new contact"""
    client_id: str = Field(..., description="Associated client ID")

class ContactUpdate(BaseModel):
    """Schema for updating a contact"""
    contact_type: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    preferred_method: Optional[str] = None
    status: Optional[str] = None

class Contact(ContactBase, TimestampMixin):
    """Complete Contact schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    contact_id: str = Field(..., description="Unique contact identifier")
    client_id: str = Field(..., description="Associated client ID")

class ContactWithClient(Contact):
    """Contact with associated client"""
    client: Optional[Client] = None

# ============================================================================
# RELATIONSHIP SCHEMAS
# ============================================================================

class RelationshipBase(BaseModel):
    """Base Relationship schema"""
    relationship_type: str = Field(default="Other", description="Type of relationship")
    description: Optional[str] = Field(None, description="Relationship description")
    status: str = Field(default="Active", description="Relationship status")

class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship"""
    client_id: str = Field(..., description="Primary client ID")
    related_client_id: str = Field(..., description="Related client ID")

class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship"""
    relationship_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Relationship(RelationshipBase, TimestampMixin):
    """Complete Relationship schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    relationship_id: str = Field(..., description="Unique relationship identifier")
    client_id: str = Field(..., description="Primary client ID")
    related_client_id: str = Field(..., description="Related client ID")

class RelationshipWithClients(Relationship):
    """Relationship with associated clients"""
    client: Optional[Client] = None
    related_client: Optional[Client] = None

# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class ClientSearchParams(BaseModel):
    """Parameters for client search"""
    first_name: Optional[str] = Field(None, description="Filter by first name")
    last_name: Optional[str] = Field(None, description="Filter by last name")
    email: Optional[str] = Field(None, description="Filter by email")
    status: Optional[str] = Field(None, description="Filter by status")
    advisor_id: Optional[str] = Field(None, description="Filter by advisor")
    household_id: Optional[str] = Field(None, description="Filter by household")
    office_id: Optional[str] = Field(None, description="Filter by office")

class HouseholdSearchParams(BaseModel):
    """Parameters for household search"""
    household_name: Optional[str] = Field(None, description="Filter by household name")
    status: Optional[str] = Field(None, description="Filter by status")
    min_net_worth: Optional[Decimal] = Field(None, description="Minimum net worth filter")
    max_net_worth: Optional[Decimal] = Field(None, description="Maximum net worth filter")
    risk_tolerance: Optional[str] = Field(None, description="Filter by risk tolerance")

class ContactSearchParams(BaseModel):
    """Parameters for contact search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    contact_type: Optional[str] = Field(None, description="Filter by contact type")
    status: Optional[str] = Field(None, description="Filter by status")

class RelationshipSearchParams(BaseModel):
    """Parameters for relationship search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    relationship_type: Optional[str] = Field(None, description="Filter by relationship type")
    status: Optional[str] = Field(None, description="Filter by status")

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

class PaginatedClientsResponse(PaginatedResponse):
    """Paginated clients response"""
    items: List[Client] = []

class PaginatedHouseholdsResponse(PaginatedResponse):
    """Paginated households response"""
    items: List[Household] = []

class PaginatedSpousesResponse(PaginatedResponse):
    """Paginated spouses response"""
    items: List[Spouse] = []

class PaginatedContactsResponse(PaginatedResponse):
    """Paginated contacts response"""
    items: List[Contact] = []

class PaginatedRelationshipsResponse(PaginatedResponse):
    """Paginated relationships response"""
    items: List[Relationship] = []

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ClientResponse(BaseModel):
    """Standard client response"""
    status: str = "success"
    data: Client

class HouseholdResponse(BaseModel):
    """Standard household response"""
    status: str = "success"
    data: Household

class SpouseResponse(BaseModel):
    """Standard spouse response"""
    status: str = "success"
    data: Spouse

class ContactResponse(BaseModel):
    """Standard contact response"""
    status: str = "success"
    data: Contact

class RelationshipResponse(BaseModel):
    """Standard relationship response"""
    status: str = "success"
    data: Relationship

# Forward references for relationships
ClientWithRelations.model_rebuild()
HouseholdWithMembers.model_rebuild()
SpouseWithClient.model_rebuild()
ContactWithClient.model_rebuild()
RelationshipWithClients.model_rebuild()
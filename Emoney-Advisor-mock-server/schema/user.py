from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import PaginatedResponse


class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"


class LogonStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"


# Base schemas
class UserBase(BaseModel):
    firm_id: str = Field(..., description="ID of firm user belongs to")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether user is active")


class RoleBase(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")


class PermissionBase(BaseModel):
    role_id: str = Field(..., description="ID of role permission belongs to")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")


class FirmBase(BaseModel):
    name: str = Field(..., description="Firm name")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website")


class LogonBase(BaseModel):
    user_id: Optional[str] = Field(None, description="ID of user logon belongs to")
    client_id: Optional[str] = Field(None, description="ID of client logon belongs to")
    username: str = Field(..., description="Username")
    status: str = Field(..., description="Logon status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


# Response models with ID and timestamps
class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    firmId: str = Field(..., description="ID of firm user belongs to")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    firstName: str = Field(..., description="First name")
    lastName: str = Field(..., description="Last name")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    isActive: bool = Field(True, description="Whether user is active")
    createdAt: datetime = Field(..., description="Timestamp when user was created")
    updatedAt: datetime = Field(..., description="Timestamp when user was last updated")
    
    model_config = {
        "from_attributes": True
    }


class RoleResponse(BaseModel):
    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    createdAt: datetime = Field(..., description="Timestamp when role was created")
    updatedAt: datetime = Field(..., description="Timestamp when role was last updated")
    
    model_config = {
        "from_attributes": True
    }


class PermissionResponse(BaseModel):
    id: str = Field(..., description="Permission ID")
    roleId: str = Field(..., description="ID of role permission belongs to")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    createdAt: datetime = Field(..., description="Timestamp when permission was created")
    updatedAt: datetime = Field(..., description="Timestamp when permission was last updated")
    
    model_config = {
        "from_attributes": True
    }


class FirmResponse(BaseModel):
    id: str = Field(..., description="Firm ID")
    name: str = Field(..., description="Firm name")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postalCode: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website")
    createdAt: datetime = Field(..., description="Timestamp when firm was created")
    updatedAt: datetime = Field(..., description="Timestamp when firm was last updated")
    
    model_config = {
        "from_attributes": True
    }


class LogonResponse(BaseModel):
    id: str = Field(..., description="Logon ID")
    userId: Optional[str] = Field(None, description="ID of user logon belongs to")
    clientId: Optional[str] = Field(None, description="ID of client logon belongs to")
    username: str = Field(..., description="Username")
    status: str = Field(..., description="Logon status")
    lastLogin: Optional[datetime] = Field(None, description="Last login timestamp")
    createdAt: datetime = Field(..., description="Timestamp when logon was created")
    updatedAt: datetime = Field(..., description="Timestamp when logon was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class UserListResponse(BaseModel):
    users: List[UserResponse] = Field(..., description="List of users")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class RoleListResponse(BaseModel):
    roles: List[RoleResponse] = Field(..., description="List of roles")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class PermissionListResponse(BaseModel):
    permissions: List[PermissionResponse] = Field(..., description="List of permissions")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class FirmListResponse(BaseModel):
    firms: List[FirmResponse] = Field(..., description="List of firms")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class LogonListResponse(BaseModel):
    logons: List[LogonResponse] = Field(..., description="List of logons")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class UserFilterParams(BaseModel):
    firm_id: Optional[str] = Field(None, description="Filter by firm ID")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    name: Optional[str] = Field(None, description="Filter by name (first or last)")
    email: Optional[str] = Field(None, description="Filter by email")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("last_name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class RoleFilterParams(BaseModel):
    name: Optional[str] = Field(None, description="Filter by role name")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class PermissionFilterParams(BaseModel):
    role_id: Optional[str] = Field(None, description="Filter by role ID")
    resource: Optional[str] = Field(None, description="Filter by resource")
    action: Optional[str] = Field(None, description="Filter by action")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("resource", description="Sort field")
    count: bool = Field(False, description="Return count only")


class FirmFilterParams(BaseModel):
    name: Optional[str] = Field(None, description="Filter by firm name")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class LogonFilterParams(BaseModel):
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    status: Optional[str] = Field(None, description="Filter by status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("last_login", description="Sort field")
    count: bool = Field(False, description="Return count only")
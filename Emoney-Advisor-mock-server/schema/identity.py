# schema/identity.py - Version 1: Identity & Access Management Schemas

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for created/modified timestamps"""
    created_date: datetime
    modified_date: datetime

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base User schema"""
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    status: str = Field(default="Active", description="User status")

class UserCreate(UserBase):
    """Schema for creating a new user"""
    office_id: Optional[str] = Field(None, description="Associated office ID")

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[str] = None
    office_id: Optional[str] = None

class User(UserBase, TimestampMixin):
    """Complete User schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(..., description="Unique user identifier")
    office_id: Optional[str] = Field(None, description="Associated office ID")
    last_login_date: Optional[datetime] = Field(None, description="Last login timestamp")

class UserWithRelations(User):
    """User with related entities"""
    office: Optional['Office'] = None
    roles: List['Role'] = []

class UserProfile(User):
    """User profile with office details"""
    office: Optional['Office'] = None

# ============================================================================
# OFFICE SCHEMAS
# ============================================================================

class OfficeBase(BaseModel):
    """Base Office schema"""
    office_name: str = Field(..., description="Office name")
    office_path: Optional[str] = Field(None, description="Office hierarchy path")
    status: str = Field(default="Active", description="Office status")
    address: Optional[str] = Field(None, description="Office address")
    city: Optional[str] = Field(None, description="Office city")
    state: Optional[str] = Field(None, description="Office state")
    zip_code: Optional[str] = Field(None, description="Office zip code")
    phone: Optional[str] = Field(None, description="Office phone number")

class OfficeCreate(OfficeBase):
    """Schema for creating a new office"""
    parent_office_id: Optional[str] = Field(None, description="Parent office ID")

class OfficeUpdate(BaseModel):
    """Schema for updating an office"""
    office_name: Optional[str] = None
    parent_office_id: Optional[str] = None
    office_path: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None

class Office(OfficeBase, TimestampMixin):
    """Complete Office schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    office_id: str = Field(..., description="Unique office identifier")
    parent_office_id: Optional[str] = Field(None, description="Parent office ID")

class OfficeWithRelations(Office):
    """Office with related entities"""
    parent_office: Optional[Office] = None
    child_offices: List[Office] = []
    users: List[User] = []

# ============================================================================
# ROLE SCHEMAS
# ============================================================================

class RoleBase(BaseModel):
    """Base Role schema"""
    role_name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    role_type: Optional[str] = Field(None, description="Role type")
    status: str = Field(default="Active", description="Role status")

class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    role_name: Optional[str] = None
    description: Optional[str] = None
    role_type: Optional[str] = None
    status: Optional[str] = None

class Role(RoleBase, TimestampMixin):
    """Complete Role schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    role_id: str = Field(..., description="Unique role identifier")

class RoleWithRelations(Role):
    """Role with related entities"""
    users: List[User] = []
    permissions: List['Permission'] = []

# ============================================================================
# PERMISSION SCHEMAS
# ============================================================================

class PermissionBase(BaseModel):
    """Base Permission schema"""
    permission_name: str = Field(..., description="Permission name")
    permission_code: str = Field(..., description="Unique permission code")
    category: Optional[str] = Field(None, description="Permission category")
    description: Optional[str] = Field(None, description="Permission description")
    status: str = Field(default="Active", description="Permission status")

class PermissionCreate(PermissionBase):
    """Schema for creating a new permission"""
    pass

class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""
    permission_name: Optional[str] = None
    permission_code: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Permission(PermissionBase):
    """Complete Permission schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    permission_id: str = Field(..., description="Unique permission identifier")
    created_date: datetime

class PermissionWithRoles(Permission):
    """Permission with associated roles"""
    roles: List[Role] = []

# ============================================================================
# SHARING RULE SCHEMAS
# ============================================================================

class SharingRuleBase(BaseModel):
    """Base Sharing Rule schema"""
    client_id: str = Field(..., description="Associated client ID")
    access_level: str = Field(..., description="Access level granted")
    can_view: bool = Field(default=True, description="Can view permission")
    can_edit: bool = Field(default=False, description="Can edit permission")
    can_delete: bool = Field(default=False, description="Can delete permission")
    start_date: Optional[datetime] = Field(None, description="Access start date")
    end_date: Optional[datetime] = Field(None, description="Access end date")
    status: str = Field(default="Active", description="Sharing rule status")

class SharingRuleCreate(SharingRuleBase):
    """Schema for creating a new sharing rule"""
    user_id: str = Field(..., description="User granted access")
    created_by: str = Field(..., description="User who created the rule")

class SharingRuleUpdate(BaseModel):
    """Schema for updating a sharing rule"""
    access_level: Optional[str] = None
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None
    can_delete: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

class SharingRule(SharingRuleBase, TimestampMixin):
    """Complete Sharing Rule schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    sharing_rule_id: str = Field(..., description="Unique sharing rule identifier")
    user_id: str = Field(..., description="User granted access")
    created_by: str = Field(..., description="User who created the rule")

class SharingRuleWithRelations(SharingRule):
    """Sharing Rule with related entities"""
    user: Optional[User] = None
    created_by_user: Optional[User] = None

# ============================================================================
# LOGON SCHEMAS
# ============================================================================

class LogonBase(BaseModel):
    """Base Logon schema"""
    logon_type: str = Field(default="User", description="Type of logon")
    logon_date_time: datetime = Field(..., description="Logon timestamp")
    logout_date_time: Optional[datetime] = Field(None, description="Logout timestamp")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    session_id: Optional[str] = Field(None, description="Session identifier")
    status: str = Field(default="Active", description="Logon status")
    duration: Optional[int] = Field(None, description="Session duration in minutes")

class LogonCreate(LogonBase):
    """Schema for creating a new logon"""
    user_id: str = Field(..., description="Associated user ID")

class LogonUpdate(BaseModel):
    """Schema for updating a logon"""
    logout_date_time: Optional[datetime] = None
    status: Optional[str] = None
    duration: Optional[int] = None

class Logon(LogonBase):
    """Complete Logon schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    logon_id: str = Field(..., description="Unique logon identifier")
    user_id: str = Field(..., description="Associated user ID")

class LogonWithUser(Logon):
    """Logon with associated user"""
    user: Optional[User] = None

class LogonActivity(Logon):
    """Logon activity (same as Logon for now)"""
    pass

# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class UserSearchParams(BaseModel):
    """Parameters for user search"""
    username: Optional[str] = Field(None, description="Filter by username")
    email: Optional[str] = Field(None, description="Filter by email")
    first_name: Optional[str] = Field(None, description="Filter by first name")
    last_name: Optional[str] = Field(None, description="Filter by last name")
    status: Optional[str] = Field(None, description="Filter by status")
    office_id: Optional[str] = Field(None, description="Filter by office")
    role: Optional[str] = Field(None, description="Filter by role name")

class OfficeSearchParams(BaseModel):
    """Parameters for office search"""
    office_name: Optional[str] = Field(None, description="Filter by office name")
    status: Optional[str] = Field(None, description="Filter by status")
    parent_office_id: Optional[str] = Field(None, description="Filter by parent office")

class RoleSearchParams(BaseModel):
    """Parameters for role search"""
    role_name: Optional[str] = Field(None, description="Filter by role name")
    role_type: Optional[str] = Field(None, description="Filter by role type")
    status: Optional[str] = Field(None, description="Filter by status")

class PermissionSearchParams(BaseModel):
    """Parameters for permission search"""
    permission_name: Optional[str] = Field(None, description="Filter by permission name")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by status")

class SharingRuleSearchParams(BaseModel):
    """Parameters for sharing rule search"""
    user_id: Optional[str] = Field(None, description="Filter by user")
    client_id: Optional[str] = Field(None, description="Filter by client")
    status: Optional[str] = Field(None, description="Filter by status")
    access_level: Optional[str] = Field(None, description="Filter by access level")

class LogonSearchParams(BaseModel):
    """Parameters for logon search"""
    user_id: Optional[str] = Field(None, description="Filter by user")
    logon_type: Optional[str] = Field(None, description="Filter by logon type")
    status: Optional[str] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")

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

class PaginatedUsersResponse(PaginatedResponse):
    """Paginated users response"""
    items: List[User] = []

class PaginatedOfficesResponse(PaginatedResponse):
    """Paginated offices response"""
    items: List[Office] = []

class PaginatedRolesResponse(PaginatedResponse):
    """Paginated roles response"""
    items: List[Role] = []

class PaginatedPermissionsResponse(PaginatedResponse):
    """Paginated permissions response"""
    items: List[Permission] = []

class PaginatedSharingRulesResponse(PaginatedResponse):
    """Paginated sharing rules response"""
    items: List[SharingRule] = []

class PaginatedLogonsResponse(PaginatedResponse):
    """Paginated logons response"""
    items: List[Logon] = []

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class UserResponse(BaseModel):
    """Standard user response"""
    status: str = "success"
    data: User

class OfficeResponse(BaseModel):
    """Standard office response"""
    status: str = "success"
    data: Office

class RoleResponse(BaseModel):
    """Standard role response"""
    status: str = "success"
    data: Role

class PermissionResponse(BaseModel):
    """Standard permission response"""
    status: str = "success"
    data: Permission

class SharingRuleResponse(BaseModel):
    """Standard sharing rule response"""
    status: str = "success"
    data: SharingRule

class LogonResponse(BaseModel):
    """Standard logon response"""
    status: str = "success"
    data: Logon

# ============================================================================
# SUMMARY SCHEMAS
# ============================================================================

class UserSummary(BaseModel):
    """User summary information"""
    user_id: str
    username: str
    full_name: str
    email: str
    status: str
    office_name: Optional[str] = None
    roles: List[str] = []
    last_login: Optional[datetime] = None

class OfficeSummary(BaseModel):
    """Office summary information"""
    office_id: str
    office_name: str
    office_path: Optional[str] = None
    status: str
    total_users: int
    active_users: int
    total_clients: int

class AccessSummary(BaseModel):
    """User access summary"""
    user_id: str
    username: str
    total_permissions: int
    total_clients_accessible: int
    active_sharing_rules: int
    roles: List[str] = []

# Forward references for relationships
UserWithRelations.model_rebuild()
OfficeWithRelations.model_rebuild()
RoleWithRelations.model_rebuild()
PermissionWithRoles.model_rebuild()
SharingRuleWithRelations.model_rebuild()
LogonWithUser.model_rebuild()
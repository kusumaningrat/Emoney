# models/identity.py - Version 1: Identity & Access Management (Schema Compliant)

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

# ============================================================================
# JUNCTION TABLES (Define with proper column naming)
# ============================================================================

# Many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("UserID", String, ForeignKey("users.UserID"), primary_key=True),
    Column("RoleID", String, ForeignKey("roles.RoleID"), primary_key=True),
    extend_existing=True
)

# Many-to-many relationship between roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("RoleID", String, ForeignKey("roles.RoleID"), primary_key=True),
    Column("PermissionID", String, ForeignKey("permissions.PermissionID"), primary_key=True),
    extend_existing=True
)

# ============================================================================
# ENUMS
# ============================================================================

class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"

class OfficeStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class RoleStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class SharingRuleStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    EXPIRED = "Expired"

class LogonStatus(str, enum.Enum):
    ACTIVE = "Active"
    LOGGED_OUT = "LoggedOut"
    EXPIRED = "Expired"

class LogonType(str, enum.Enum):
    USER = "User"
    CLIENT = "Client"
    PORTAL = "Portal"

# ============================================================================
# MODELS - Following eMoney V1 Schema Specification
# ============================================================================

class Office(Base):
    """Office Model - eMoney V1 Schema"""
    __tablename__ = "offices"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    OfficeID = Column("OfficeID", String, primary_key=True, index=True)
    OfficeName = Column("OfficeName", String, nullable=False)
    ParentOfficeID = Column("ParentOfficeID", String, ForeignKey("offices.OfficeID"), nullable=True)
    OfficePath = Column("OfficePath", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=OfficeStatus.ACTIVE.value)
    Address = Column("Address", String, nullable=True)
    City = Column("City", String, nullable=True)
    State = Column("State", String, nullable=True)
    ZipCode = Column("ZipCode", String, nullable=True)
    Phone = Column("Phone", String, nullable=True)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_office = relationship("Office", remote_side=[OfficeID], back_populates="child_offices")
    child_offices = relationship("Office", back_populates="parent_office")
    users = relationship("User", back_populates="office", foreign_keys="User.OfficeID")


class User(Base):
    """User Model - eMoney V1 Schema"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    UserID = Column("UserID", String, primary_key=True, index=True)
    Username = Column("Username", String, unique=True, index=True, nullable=False)
    Email = Column("Email", String, unique=True, index=True, nullable=False)
    FirstName = Column("FirstName", String, nullable=False)
    LastName = Column("LastName", String, nullable=False)
    Status = Column("Status", String, nullable=False, default=UserStatus.ACTIVE.value)
    OfficeID = Column("OfficeID", String, ForeignKey("offices.OfficeID"), nullable=True)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    LastLoginDate = Column("LastLoginDate", DateTime, nullable=True)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    office = relationship("Office", back_populates="users", foreign_keys=[OfficeID])
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sharing_rules_created = relationship("SharingRule", back_populates="created_by_user", foreign_keys="SharingRule.CreatedBy")
    sharing_rules_assigned = relationship("SharingRule", back_populates="user", foreign_keys="SharingRule.UserID")
    logons = relationship("Logon", back_populates="user")


class Role(Base):
    """Role Model - eMoney V1 Schema"""
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    RoleID = Column("RoleID", String, primary_key=True, index=True)
    RoleName = Column("RoleName", String, unique=True, nullable=False)
    Description = Column("Description", String, nullable=True)
    RoleType = Column("RoleType", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=RoleStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission Model - eMoney V1 Schema"""
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    PermissionID = Column("PermissionID", String, primary_key=True, index=True)
    PermissionName = Column("PermissionName", String, nullable=False)
    PermissionCode = Column("PermissionCode", String, unique=True, nullable=False)
    Category = Column("Category", String, nullable=True)
    Description = Column("Description", String, nullable=True)
    Status = Column("Status", String, nullable=False, default="Active")
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class SharingRule(Base):
    """SharingRule Model - eMoney V1 Schema"""
    __tablename__ = "sharing_rules"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    SharingRuleID = Column("SharingRuleID", String, primary_key=True, index=True)
    UserID = Column("UserID", String, ForeignKey("users.UserID"), nullable=False)
    ClientID = Column("ClientID", String, nullable=False)  # Foreign key to Client in V2
    AccessLevel = Column("AccessLevel", String, nullable=False)
    CanView = Column("CanView", Boolean, default=True)
    CanEdit = Column("CanEdit", Boolean, default=False)
    CanDelete = Column("CanDelete", Boolean, default=False)
    StartDate = Column("StartDate", DateTime, nullable=True)
    EndDate = Column("EndDate", DateTime, nullable=True)
    Status = Column("Status", String, nullable=False, default=SharingRuleStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = Column("CreatedBy", String, ForeignKey("users.UserID"), nullable=False)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sharing_rules_assigned", foreign_keys=[UserID])
    created_by_user = relationship("User", back_populates="sharing_rules_created", foreign_keys=[CreatedBy])


class Logon(Base):
    """Logon Model - eMoney V1 Schema"""
    __tablename__ = "logons"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    LogonID = Column("LogonID", String, primary_key=True, index=True)
    UserID = Column("UserID", String, ForeignKey("users.UserID"), nullable=False)
    LogonType = Column("LogonType", String, nullable=False, default=LogonType.USER.value)
    LogonDateTime = Column("LogonDateTime", DateTime, nullable=False, default=datetime.utcnow)
    LogoutDateTime = Column("LogoutDateTime", DateTime, nullable=True)
    IPAddress = Column("IPAddress", String, nullable=True)
    UserAgent = Column("UserAgent", String, nullable=True)
    SessionID = Column("SessionID", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=LogonStatus.ACTIVE.value)
    Duration = Column("Duration", Integer, nullable=True)  # Duration in minutes
    
    # Relationships
    user = relationship("User", back_populates="logons")
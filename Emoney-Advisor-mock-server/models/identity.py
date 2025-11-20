from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

# ============================================================================
# JUNCTION TABLES (Define AFTER the models they reference)
# ============================================================================

# Many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.user_id"), primary_key=True),
    Column("role_id", String, ForeignKey("roles.role_id"), primary_key=True),
    extend_existing=True
)

# Many-to-many relationship between roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String, ForeignKey("roles.role_id"), primary_key=True),
    Column("permission_id", String, ForeignKey("permissions.permission_id"), primary_key=True),
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
# MODELS
# ============================================================================

class Office(Base):
    """Office Model - Must be defined before User"""
    __tablename__ = "offices"
    __table_args__ = {'extend_existing': True}
    
    office_id = Column(String, primary_key=True, index=True)
    office_name = Column(String, nullable=False)
    parent_office_id = Column(String, ForeignKey("offices.office_id"), nullable=True)
    office_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default=OfficeStatus.ACTIVE.value)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_office = relationship("Office", remote_side=[office_id], back_populates="child_offices")
    child_offices = relationship("Office", back_populates="parent_office")
    users = relationship("User", back_populates="office", foreign_keys="User.office_id")


class User(Base):
    """User Model"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default=UserStatus.ACTIVE.value)
    office_id = Column(String, ForeignKey("offices.office_id"), nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login_date = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    office = relationship("Office", back_populates="users", foreign_keys=[office_id])
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sharing_rules_created = relationship("SharingRule", back_populates="created_by_user", foreign_keys="SharingRule.created_by")
    sharing_rules_assigned = relationship("SharingRule", back_populates="user", foreign_keys="SharingRule.user_id")
    logons = relationship("Logon", back_populates="user")


class Role(Base):
    """Role Model"""
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    role_id = Column(String, primary_key=True, index=True)
    role_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    role_type = Column(String, nullable=True)
    status = Column(String, nullable=False, default=RoleStatus.ACTIVE.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission Model"""
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    
    permission_id = Column(String, primary_key=True, index=True)
    permission_name = Column(String, nullable=False)
    permission_code = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class SharingRule(Base):
    """SharingRule Model"""
    __tablename__ = "sharing_rules"
    __table_args__ = {'extend_existing': True}
    
    sharing_rule_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    client_id = Column(String, nullable=False)  # Foreign key to Client in V2
    access_level = Column(String, nullable=False)
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default=SharingRuleStatus.ACTIVE.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sharing_rules_assigned", foreign_keys=[user_id])
    created_by_user = relationship("User", back_populates="sharing_rules_created", foreign_keys=[created_by])


class Logon(Base):
    """Logon Model"""
    __tablename__ = "logons"
    __table_args__ = {'extend_existing': True}
    
    logon_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    logon_type = Column(String, nullable=False, default=LogonType.USER.value)
    logon_date_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    logout_date_time = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default=LogonStatus.ACTIVE.value)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    
    # Relationships
    user = relationship("User", back_populates="logons")
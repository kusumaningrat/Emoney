from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, Table
from sqlalchemy.orm import relationship as sqlalchemy_relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from database import Base

# Many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id")),
    Column("role_id", String, ForeignKey("roles.id")),
    extend_existing=True  # Added to prevent duplicate table errors
)

class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"

class LogonStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    firm_id = Column(String, ForeignKey("firms.id"))
    # Removed workspace_id column
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    title = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    firm = sqlalchemy_relationship("Firm", back_populates="users")
    roles = sqlalchemy_relationship("Role", secondary=user_roles, back_populates="users")
    clients_owned = sqlalchemy_relationship("models.clients.Client", foreign_keys="models.clients.Client.owning_advisor", back_populates="advisor")
    client_created = sqlalchemy_relationship("models.clients.Client", foreign_keys="models.clients.Client.created_by")
    client_updated = sqlalchemy_relationship("models.clients.Client", foreign_keys="models.clients.Client.updated_by")
    logons = sqlalchemy_relationship("Logon", back_populates="user", foreign_keys="Logon.user_id")
    # Removed workspace relationship

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    users = sqlalchemy_relationship("User", secondary=user_roles, back_populates="roles")
    permissions = sqlalchemy_relationship("Permission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    role_id = Column(String, ForeignKey("roles.id"))
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)  # create, read, update, delete
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    role = sqlalchemy_relationship("Role", back_populates="permissions")

class Firm(Base):
    __tablename__ = "firms"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    users = sqlalchemy_relationship("User", back_populates="firm")
    clients = sqlalchemy_relationship("models.clients.Client", back_populates="firm")

class Logon(Base):
    __tablename__ = "logons"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    username = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    user = sqlalchemy_relationship("User", foreign_keys=[user_id], back_populates="logons")
    client = sqlalchemy_relationship("models.clients.Client", foreign_keys=[client_id], back_populates="logons")

class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Active")
    users_limit = Column(Integer)
    storage_limit = Column(Integer)
    storage_used = Column(Integer, default=0)
    custom_domain = Column(String)
    features = Column(String)  # JSON string
    branding = Column(String)  # JSON string
    subscription = Column(String)  # JSON string
    settings = Column(String)  # JSON string
    api_keys = Column(String)  # JSON string
    security = Column(String)  # JSON string
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Removed users relationship referencing workspace_id

class Advisor(Base):
    __tablename__ = "advisors"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    firm_id = Column(String, ForeignKey("firms.id"), nullable=True)
    title = Column(String, nullable=False)
    specialties = Column(String)  # JSON string
    credentials = Column(String)  # JSON string
    experience_years = Column(Integer)
    client_count = Column(Integer)
    aum = Column(Integer)
    service_model = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper references
    user = sqlalchemy_relationship("User", foreign_keys=[user_id])
    workspace = sqlalchemy_relationship("Workspace", foreign_keys=[workspace_id])
    firm = sqlalchemy_relationship("Firm", foreign_keys=[firm_id])
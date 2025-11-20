from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class ClientStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PROSPECT = "Prospect"
    ARCHIVED = "Archived"

class MaritalStatus(str, enum.Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"

class Gender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "PreferNotToSay"

class HouseholdStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class ContactType(str, enum.Enum):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    EMERGENCY = "Emergency"
    BUSINESS = "Business"

class RelationshipType(str, enum.Enum):
    SPOUSE = "Spouse"
    PARENT = "Parent"
    CHILD = "Child"
    SIBLING = "Sibling"
    PARTNER = "Partner"
    DEPENDENT = "Dependent"
    REFERRAL = "Referral"
    OTHER = "Other"

# ============================================================================
# MODELS
# ============================================================================

class Household(Base):
    """Household Model - Must be defined before Client"""
    __tablename__ = "households"
    __table_args__ = {'extend_existing': True}
    
    household_id = Column(String, primary_key=True, index=True)
    household_name = Column(String, nullable=False)
    primary_client_id = Column(String, nullable=True)  # Will be FK after Client is defined
    net_worth = Column(Float, nullable=True, default=0.0)
    status = Column(String, nullable=False, default=HouseholdStatus.ACTIVE.value)
    risk_tolerance = Column(String, nullable=True)  # Conservative, Moderate, Aggressive
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - defined after Client model
    # members will be back-populated from Client
    members = relationship("Client", back_populates="household", foreign_keys="Client.household_id")


class Client(Base):
    """Client Model"""
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    client_id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    status = Column(String, nullable=False, default=ClientStatus.ACTIVE.value)
    
    # Foreign Keys
    household_id = Column(String, ForeignKey("households.household_id"), nullable=True)
    spouse_id = Column(String, ForeignKey("spouses.spouse_id"), nullable=True)
    advisor_id = Column(String, nullable=True)  # Reference to advisor user
    owning_user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    office_id = Column(String, ForeignKey("offices.office_id"), nullable=True)
    firm_id = Column(String, nullable=True)
    
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    household = relationship("Household", back_populates="members", foreign_keys=[household_id])
    spouse = relationship("Spouse", back_populates="clients", foreign_keys=[spouse_id], uselist=False)
    contacts = relationship("Contact", back_populates="client", cascade="all, delete-orphan")
    
    # Relationships to V1 models (no back_populates since we don't modify V1)
    owning_user = relationship("User", foreign_keys=[owning_user_id], viewonly=True)
    office = relationship("Office", foreign_keys=[office_id], viewonly=True)
    
    # Self-referential relationships through Relationship table
    relationships_as_client = relationship(
        "Relationship",
        foreign_keys="Relationship.client_id",
        back_populates="client"
    )
    relationships_as_related = relationship(
        "Relationship",
        foreign_keys="Relationship.related_client_id",
        back_populates="related_client"
    )


class Contact(Base):
    """Contact Model"""
    __tablename__ = "contacts"
    __table_args__ = {'extend_existing': True}
    
    contact_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    contact_type = Column(String, nullable=False, default=ContactType.PRIMARY.value)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True, default="US")
    preferred_method = Column(String, nullable=True)  # Email, Phone, Mail
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")


class Spouse(Base):
    """Spouse Model"""
    __tablename__ = "spouses"
    __table_args__ = {'extend_existing': True}
    
    spouse_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="spouse", foreign_keys=[client_id])


class Relationship(Base):
    """Relationship Model - Maps relationships between clients"""
    __tablename__ = "relationships"
    __table_args__ = {'extend_existing': True}
    
    relationship_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    related_client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    relationship_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", foreign_keys=[client_id], back_populates="relationships_as_client")
    related_client = relationship("Client", foreign_keys=[related_client_id], back_populates="relationships_as_related")
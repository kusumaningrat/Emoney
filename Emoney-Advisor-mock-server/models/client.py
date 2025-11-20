# models/client.py - Version 2: Client & Household Management (Working Version)

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
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

class ContactType(str, enum.Enum):
    PRIMARY = "Primary"
    EMERGENCY = "Emergency"
    BENEFICIARY = "Beneficiary"
    ATTORNEY = "Attorney"
    ACCOUNTANT = "Accountant"
    OTHER = "Other"

class PreferredMethod(str, enum.Enum):
    EMAIL = "Email"
    PHONE = "Phone"
    MAIL = "Mail"
    TEXT = "Text"

class RiskTolerance(str, enum.Enum):
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"
    VERY_AGGRESSIVE = "VeryAggressive"

class RelationshipType(str, enum.Enum):
    SPOUSE = "Spouse"
    CHILD = "Child"
    PARENT = "Parent"
    SIBLING = "Sibling"
    REFERRAL = "Referral"
    BUSINESS_PARTNER = "BusinessPartner"
    OTHER = "Other"

# ============================================================================
# MODELS - Following eMoney V2 Schema Specification
# ============================================================================

class Household(Base):
    """Household Model - eMoney V2 Schema"""
    __tablename__ = "households"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    HouseholdID = Column("HouseholdID", String, primary_key=True, index=True)
    HouseholdName = Column("HouseholdName", String, nullable=False)
    PrimaryClientID = Column("PrimaryClientID", String, nullable=True)  # No ForeignKey for now
    NetWorth = Column("NetWorth", Numeric(18, 2), nullable=True, default=0.00)
    Status = Column("Status", String, nullable=False, default=ClientStatus.ACTIVE.value)
    RiskTolerance = Column("RiskTolerance", String, nullable=True, default=RiskTolerance.MODERATE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Simple one-way relationship only
    members = relationship("Client", back_populates="household", foreign_keys="Client.HouseholdID")


class Client(Base):
    """Client Model - eMoney V2 Schema"""
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    ClientID = Column("ClientID", String, primary_key=True, index=True)
    FirstName = Column("FirstName", String, nullable=False)
    LastName = Column("LastName", String, nullable=False)
    MiddleName = Column("MiddleName", String, nullable=True)
    Email = Column("Email", String, unique=True, index=True, nullable=True)
    Phone = Column("Phone", String, nullable=True)
    DateOfBirth = Column("DateOfBirth", Date, nullable=True)
    Gender = Column("Gender", String, nullable=True)
    MaritalStatus = Column("MaritalStatus", String, nullable=True, default=MaritalStatus.SINGLE.value)
    Status = Column("Status", String, nullable=False, default=ClientStatus.ACTIVE.value)
    HouseholdID = Column("HouseholdID", String, ForeignKey("households.HouseholdID"), nullable=True)
    SpouseID = Column("SpouseID", String, nullable=True)  # Remove ForeignKey to avoid circular reference
    AdvisorID = Column("AdvisorID", String, nullable=True)
    OwningUserID = Column("OwningUserID", String, ForeignKey("users.UserID"), nullable=True)
    OfficeID = Column("OfficeID", String, ForeignKey("offices.OfficeID"), nullable=True)
    FirmID = Column("FirmID", String, nullable=True)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Simplified to avoid circular references
    household = relationship("Household", back_populates="members", foreign_keys=[HouseholdID])
    spouse = relationship("Spouse", back_populates="client", foreign_keys="Spouse.ClientID")
    owning_user = relationship("User", foreign_keys=[OwningUserID])
    office = relationship("Office", foreign_keys=[OfficeID])
    contacts = relationship("Contact", back_populates="client", foreign_keys="Contact.ClientID")
    # Self-referencing relationship for family connections
    relationships_as_client = relationship("Relationship", back_populates="client", foreign_keys="Relationship.ClientID")
    relationships_as_related = relationship("Relationship", back_populates="related_client", foreign_keys="Relationship.RelatedClientID")


class Spouse(Base):
    """Spouse Model - eMoney V2 Schema"""
    __tablename__ = "spouses"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    SpouseID = Column("SpouseID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    FirstName = Column("FirstName", String, nullable=False)
    LastName = Column("LastName", String, nullable=False)
    MiddleName = Column("MiddleName", String, nullable=True)
    Email = Column("Email", String, nullable=True)
    Phone = Column("Phone", String, nullable=True)
    DateOfBirth = Column("DateOfBirth", Date, nullable=True)
    Gender = Column("Gender", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=ClientStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="spouse", foreign_keys=[ClientID])


class Contact(Base):
    """Contact Model - eMoney V2 Schema"""
    __tablename__ = "contacts"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    ContactID = Column("ContactID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    ContactType = Column("ContactType", String, nullable=False, default=ContactType.PRIMARY.value)
    FirstName = Column("FirstName", String, nullable=False)
    LastName = Column("LastName", String, nullable=False)
    Email = Column("Email", String, nullable=True)
    Phone = Column("Phone", String, nullable=True)
    Address = Column("Address", String, nullable=True)
    City = Column("City", String, nullable=True)
    State = Column("State", String, nullable=True)
    ZipCode = Column("ZipCode", String, nullable=True)
    Country = Column("Country", String, nullable=True, default="US")
    PreferredMethod = Column("PreferredMethod", String, nullable=True, default=PreferredMethod.EMAIL.value)
    Status = Column("Status", String, nullable=False, default=ClientStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")


class Relationship(Base):
    """Relationship Model - eMoney V2 Schema"""
    __tablename__ = "relationships"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    RelationshipID = Column("RelationshipID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    RelatedClientID = Column("RelatedClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    RelationshipType = Column("RelationshipType", String, nullable=False, default=RelationshipType.OTHER.value)
    Description = Column("Description", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=ClientStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="relationships_as_client", foreign_keys=[ClientID])
    related_client = relationship("Client", back_populates="relationships_as_related", foreign_keys=[RelatedClientID])
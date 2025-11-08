from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship as sqlalchemy_relationship
from database import Base
from datetime import datetime
from .enums import MaritalStatus, ClientStatus, OwnershipType


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    firm_id = Column(String, ForeignKey("firms.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    marital_status = Column(String, nullable=False)
    previous_marriages = Column(Boolean, default=False)
    date_of_birth = Column(Date, nullable=False)
    owning_advisor = Column(String, ForeignKey("users.id"))
    external_id = Column(String, index=True)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Updated relationship reference
    firm = sqlalchemy_relationship("models.users.Firm", back_populates="clients")
    
    # The rest of the relationships remain the same
    spouse = sqlalchemy_relationship("Spouse", back_populates="client", uselist=False)
    plans = sqlalchemy_relationship("FinancialPlan", back_populates="client")
    contacts = sqlalchemy_relationship("Contact", back_populates="client")
    household_memberships = sqlalchemy_relationship("HouseholdMember", back_populates="client")
    accounts = sqlalchemy_relationship("Account", back_populates="client")
    assets = sqlalchemy_relationship("Asset", back_populates="client")
    liabilities = sqlalchemy_relationship("Liability", back_populates="client")
    income_sources = sqlalchemy_relationship("Income", back_populates="client")
    expenses = sqlalchemy_relationship("Expense", back_populates="client")
    vault_documents = sqlalchemy_relationship("VaultDocument", back_populates="client")
    notes = sqlalchemy_relationship("Note", back_populates="client")
    tasks = sqlalchemy_relationship("Task", back_populates="client")
    logons = sqlalchemy_relationship("Logon", back_populates="client", foreign_keys="Logon.client_id")
    estates = sqlalchemy_relationship("Estate", back_populates="client")
    retirement_plans = sqlalchemy_relationship("RetirementPlan", back_populates="client")
    insurances = sqlalchemy_relationship("Insurance", back_populates="client")
    spending_records = sqlalchemy_relationship("Spending", back_populates="client")
    alerts = sqlalchemy_relationship("Alert", back_populates="client")
    taxes = sqlalchemy_relationship("Tax", back_populates="client")
    relationships = sqlalchemy_relationship("Relationship", back_populates="client", foreign_keys="Relationship.client_id")
    
    # Fixed User relationships - use the exact overlap names from the warning
    advisor = sqlalchemy_relationship(
        "User", 
        foreign_keys=[owning_advisor],
        overlaps="creator,updater"
    )
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="advisor,updater,client_created"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="advisor,creator,client_updated"
    )

class Spouse(Base):
    __tablename__ = "spouses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    date_of_birth = Column(Date, nullable=False)
    previous_marriages = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Fixed
    client = sqlalchemy_relationship("Client", back_populates="spouse")
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="updater"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="creator"
    )

class Household(Base):
    __tablename__ = "households"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    primary_client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    assigned_to = Column(String, ForeignKey("users.id"))
    status = Column(String, default="Active")
    address = Column(JSON)
    total_aum = Column(Numeric(precision=15, scale=2))
    annual_revenue = Column(Numeric(precision=15, scale=2))
    client_since = Column(Date)
    servicing_model = Column(String)
    review_frequency = Column(String)
    next_review_date = Column(Date)
    primary_advisor = Column(String, ForeignKey("users.id"))
    secondary_advisor = Column(String, ForeignKey("users.id"))
    service_team = Column(JSON)
    accounts = Column(JSON)
    goals = Column(JSON)
    financial_plan = Column(String)
    notes = Column(String)
    tags = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Fixed
    primary_client = sqlalchemy_relationship("Client", foreign_keys=[primary_client_id])
    household_members = sqlalchemy_relationship("HouseholdMember", back_populates="household")
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="updater,owner,primary_advisor_rel,secondary_advisor_rel"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="creator,owner,primary_advisor_rel,secondary_advisor_rel"
    )
    owner = sqlalchemy_relationship(
        "User", 
        foreign_keys=[assigned_to],
        overlaps="creator,updater,primary_advisor_rel,secondary_advisor_rel"
    )
    primary_advisor_rel = sqlalchemy_relationship(
        "User", 
        foreign_keys=[primary_advisor],
        overlaps="creator,updater,owner,secondary_advisor_rel"
    )
    secondary_advisor_rel = sqlalchemy_relationship(
        "User", 
        foreign_keys=[secondary_advisor],
        overlaps="creator,updater,owner,primary_advisor_rel"
    )

class HouseholdMember(Base):
    __tablename__ = "household_members"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    household_id = Column(String, ForeignKey("households.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)  # Child, Parent, Other
    date_of_birth = Column(Date)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Fixed
    household = sqlalchemy_relationship("Household", back_populates="household_members")
    client = sqlalchemy_relationship("Client", back_populates="household_memberships")
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="updater"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="creator"
    )

class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    related_client_id = Column(String, ForeignKey("clients.id"))
    relationship_type = Column(String, nullable=False)  # Family, Professional, Business
    description = Column(String)
    notes = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = sqlalchemy_relationship("Client", foreign_keys=[client_id], back_populates="relationships")
    related_client = sqlalchemy_relationship("Client", foreign_keys=[related_client_id])
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="updater"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="creator"
    )

class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    type = Column(String, nullable=False)  # Primary, Work, Emergency
    address_line1 = Column(String)
    address_line2 = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    email = Column(String)
    phone = Column(String)
    is_preferred = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Fixed
    client = sqlalchemy_relationship("Client", back_populates="contacts")
    creator = sqlalchemy_relationship(
        "User", 
        foreign_keys=[created_by],
        overlaps="updater"
    )
    updater = sqlalchemy_relationship(
        "User", 
        foreign_keys=[updated_by],
        overlaps="creator"
    )
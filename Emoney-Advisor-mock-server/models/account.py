# models/account.py - Version 4: Account Management (Schema Compliant)

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class AccountStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CLOSED = "Closed"
    SUSPENDED = "Suspended"

class AccountCategory(str, enum.Enum):
    INVESTMENT = "Investment"
    RETIREMENT = "Retirement"
    CASH = "Cash"
    INSURANCE = "Insurance"
    TRUST = "Trust"
    CREDIT = "Credit"
    OTHER = "Other"

class OwnerType(str, enum.Enum):
    INDIVIDUAL = "Individual"
    JOINT = "Joint"
    TRUST = "Trust"
    ENTITY = "Entity"

# ============================================================================
# MODELS - Following eMoney V4 Schema Specification
# ============================================================================

class AccountType(Base):
    """AccountType Model - eMoney V4 Schema"""
    __tablename__ = "account_types"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    AccountTypeID = Column("AccountTypeID", String, primary_key=True, index=True)
    TypeName = Column("TypeName", String, nullable=False)
    Category = Column("Category", String, nullable=True)
    Description = Column("Description", String, nullable=True)
    IsTaxDeferred = Column("IsTaxDeferred", Boolean, default=False, nullable=False)
    IsTaxable = Column("IsTaxable", Boolean, default=True, nullable=False)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="account_type")


class Account(Base):
    """Account Model - eMoney V4 Schema"""
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    AccountID = Column("AccountID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    HouseholdID = Column("HouseholdID", String, ForeignKey("households.HouseholdID"), nullable=True)
    AccountNumber = Column("AccountNumber", String, nullable=True)
    AccountName = Column("AccountName", String, nullable=False)
    AccountTypeID = Column("AccountTypeID", String, ForeignKey("account_types.AccountTypeID"), nullable=False)
    Balance = Column("Balance", Numeric(18, 2), nullable=True, default=0.00)
    AsOfDate = Column("AsOfDate", Date, nullable=True)
    CustodianName = Column("CustodianName", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=AccountStatus.ACTIVE.value)
    IsManaged = Column("IsManaged", Boolean, default=False, nullable=False)
    IsTaxable = Column("IsTaxable", Boolean, default=True, nullable=False)
    OwnerType = Column("OwnerType", String, nullable=True, default=OwnerType.INDIVIDUAL.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", foreign_keys=[ClientID])
    household = relationship("Household", foreign_keys=[HouseholdID])
    account_type = relationship("AccountType", back_populates="accounts")
    assets = relationship("Asset", back_populates="account")
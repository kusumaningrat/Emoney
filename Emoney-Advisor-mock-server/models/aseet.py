from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class AccountStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CLOSED = "Closed"

class AccountCategory(str, enum.Enum):
    RETIREMENT = "Retirement"
    INVESTMENT = "Investment"
    BANKING = "Banking"
    INSURANCE = "Insurance"
    OTHER = "Other"

class OwnerType(str, enum.Enum):
    INDIVIDUAL = "Individual"
    JOINT = "Joint"
    TRUST = "Trust"
    BUSINESS = "Business"
    IRA = "IRA"
    ROTH_IRA = "RothIRA"

class AssetStatus(str, enum.Enum):
    ACTIVE = "Active"
    SOLD = "Sold"
    TRANSFERRED = "Transferred"

class RiskLevel(str, enum.Enum):
    CONSERVATIVE = "Conservative"
    MODERATE_CONSERVATIVE = "ModerateConservative"
    MODERATE = "Moderate"
    MODERATE_AGGRESSIVE = "ModerateAggressive"
    AGGRESSIVE = "Aggressive"

class LiabilityType(str, enum.Enum):
    MORTGAGE = "Mortgage"
    AUTO_LOAN = "AutoLoan"
    STUDENT_LOAN = "StudentLoan"
    PERSONAL_LOAN = "PersonalLoan"
    CREDIT_CARD = "CreditCard"
    LINE_OF_CREDIT = "LineOfCredit"
    OTHER = "Other"

class LiabilityStatus(str, enum.Enum):
    ACTIVE = "Active"
    PAID_OFF = "PaidOff"
    DEFAULTED = "Defaulted"
    REFINANCED = "Refinanced"

# ============================================================================
# MODELS - Order matters to avoid circular dependencies
# ============================================================================

class AccountType(Base):
    """AccountType Model - Must be defined before Account"""
    __tablename__ = "account_types"
    __table_args__ = {'extend_existing': True}
    
    account_type_id = Column(String, primary_key=True, index=True)
    type_name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, default=AccountCategory.OTHER.value)
    description = Column(Text, nullable=True)
    is_tax_deferred = Column(Boolean, default=False)
    is_taxable = Column(Boolean, default=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="account_type")


class AssetClass(Base):
    """AssetClass Model - Must be defined before Asset"""
    __tablename__ = "asset_classes"
    __table_args__ = {'extend_existing': True}
    
    asset_class_id = Column(String, primary_key=True, index=True)
    class_name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    risk_level = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    assets = relationship("Asset", back_populates="asset_class")


class Account(Base):
    """Account Model"""
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}
    
    account_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    household_id = Column(String, ForeignKey("households.household_id"), nullable=True)
    account_number = Column(String, nullable=True)
    account_name = Column(String, nullable=False)
    account_type_id = Column(String, ForeignKey("account_types.account_type_id"), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    as_of_date = Column(Date, nullable=False, default=datetime.utcnow)
    custodian_name = Column(String, nullable=True)
    status = Column(String, nullable=False, default=AccountStatus.ACTIVE.value)
    is_managed = Column(Boolean, default=False)
    is_taxable = Column(Boolean, default=True)
    owner_type = Column(String, nullable=True, default=OwnerType.INDIVIDUAL.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to V2 models (viewonly, no back_populates)
    client = relationship("Client", foreign_keys=[client_id], viewonly=True)
    household = relationship("Household", foreign_keys=[household_id], viewonly=True)
    
    # V4 Internal Relationships
    account_type = relationship("AccountType", back_populates="accounts")
    assets = relationship("Asset", back_populates="account", cascade="all, delete-orphan")


class Asset(Base):
    """Asset Model - Holdings/Securities"""
    __tablename__ = "assets"
    __table_args__ = {'extend_existing': True}
    
    asset_id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    security_name = Column(String, nullable=False)
    symbol = Column(String, nullable=True, index=True)
    cusip = Column(String, nullable=True, index=True)
    asset_class_id = Column(String, ForeignKey("asset_classes.asset_class_id"), nullable=True)
    shares = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False, default=0.0)
    value = Column(Float, nullable=False, default=0.0)
    cost_basis = Column(Float, nullable=True, default=0.0)
    unrealized_gain = Column(Float, nullable=True, default=0.0)
    unrealized_gain_percent = Column(Float, nullable=True, default=0.0)
    as_of_date = Column(Date, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default=AssetStatus.ACTIVE.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="assets")
    asset_class = relationship("AssetClass", back_populates="assets")


class Liability(Base):
    """Liability Model - Debts and Loans"""
    __tablename__ = "liabilities"
    __table_args__ = {'extend_existing': True}
    
    liability_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    household_id = Column(String, ForeignKey("households.household_id"), nullable=True)
    liability_name = Column(String, nullable=False)
    liability_type = Column(String, nullable=False, default=LiabilityType.OTHER.value)
    current_balance = Column(Float, nullable=False, default=0.0)
    original_amount = Column(Float, nullable=True, default=0.0)
    interest_rate = Column(Float, nullable=True, default=0.0)
    monthly_payment = Column(Float, nullable=True, default=0.0)
    maturity_date = Column(Date, nullable=True)
    lender = Column(String, nullable=True)
    status = Column(String, nullable=False, default=LiabilityStatus.ACTIVE.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to V2 models (viewonly, no back_populates)
    client = relationship("Client", foreign_keys=[client_id], viewonly=True)
    household = relationship("Household", foreign_keys=[household_id], viewonly=True)
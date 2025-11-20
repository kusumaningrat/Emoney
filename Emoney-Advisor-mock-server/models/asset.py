# models/asset.py - Version 4: Asset Management (Schema Compliant)

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class AssetStatus(str, enum.Enum):
    ACTIVE = "Active"
    SOLD = "Sold"
    PENDING = "Pending"
    RESTRICTED = "Restricted"

class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "VeryHigh"

class LiabilityType(str, enum.Enum):
    MORTGAGE = "Mortgage"
    AUTO_LOAN = "AutoLoan"
    CREDIT_CARD = "CreditCard"
    STUDENT_LOAN = "StudentLoan"
    PERSONAL_LOAN = "PersonalLoan"
    LINE_OF_CREDIT = "LineOfCredit"
    OTHER = "Other"

class LiabilityStatus(str, enum.Enum):
    ACTIVE = "Active"
    PAID_OFF = "PaidOff"
    DEFAULT = "Default"
    CLOSED = "Closed"

# ============================================================================
# MODELS - Following eMoney V4 Schema Specification
# ============================================================================

class AssetClass(Base):
    """AssetClass Model - eMoney V4 Schema"""
    __tablename__ = "asset_classes"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    AssetClassID = Column("AssetClassID", String, primary_key=True, index=True)
    ClassName = Column("ClassName", String, nullable=False)
    Category = Column("Category", String, nullable=True)
    Description = Column("Description", String, nullable=True)
    RiskLevel = Column("RiskLevel", String, nullable=True, default=RiskLevel.MODERATE.value)
    Status = Column("Status", String, nullable=False, default="Active")
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    assets = relationship("Asset", back_populates="asset_class")


class Asset(Base):
    """Asset Model - eMoney V4 Schema"""
    __tablename__ = "assets"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    AssetID = Column("AssetID", String, primary_key=True, index=True)
    AccountID = Column("AccountID", String, ForeignKey("accounts.AccountID"), nullable=False)
    SecurityName = Column("SecurityName", String, nullable=False)
    Symbol = Column("Symbol", String, nullable=True)
    CUSIP = Column("CUSIP", String, nullable=True)
    AssetClassID = Column("AssetClassID", String, ForeignKey("asset_classes.AssetClassID"), nullable=True)
    Shares = Column("Shares", Numeric(18, 6), nullable=True, default=0.000000)
    Price = Column("Price", Numeric(18, 4), nullable=True, default=0.0000)
    Value = Column("Value", Numeric(18, 2), nullable=True, default=0.00)
    CostBasis = Column("CostBasis", Numeric(18, 2), nullable=True, default=0.00)
    UnrealizedGain = Column("UnrealizedGain", Numeric(18, 2), nullable=True, default=0.00)
    UnrealizedGainPercent = Column("UnrealizedGainPercent", Numeric(5, 2), nullable=True, default=0.00)
    AsOfDate = Column("AsOfDate", Date, nullable=True)
    Status = Column("Status", String, nullable=False, default=AssetStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="assets")
    asset_class = relationship("AssetClass", back_populates="assets")


class Liability(Base):
    """Liability Model - eMoney V4 Schema"""
    __tablename__ = "liabilities"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    LiabilityID = Column("LiabilityID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    HouseholdID = Column("HouseholdID", String, ForeignKey("households.HouseholdID"), nullable=True)
    LiabilityName = Column("LiabilityName", String, nullable=False)
    LiabilityType = Column("LiabilityType", String, nullable=False, default=LiabilityType.OTHER.value)
    CurrentBalance = Column("CurrentBalance", Numeric(18, 2), nullable=True, default=0.00)
    OriginalAmount = Column("OriginalAmount", Numeric(18, 2), nullable=True, default=0.00)
    # FIXED: Changed from Numeric(5, 4) to Numeric(6, 4) to accommodate interest rates up to 99.9999%
    InterestRate = Column("InterestRate", Numeric(6, 4), nullable=True, default=0.0000)
    MonthlyPayment = Column("MonthlyPayment", Numeric(18, 2), nullable=True, default=0.00)
    MaturityDate = Column("MaturityDate", Date, nullable=True)
    Lender = Column("Lender", String, nullable=True)
    Status = Column("Status", String, nullable=False, default=LiabilityStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", foreign_keys=[ClientID])
    household = relationship("Household", foreign_keys=[HouseholdID])
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
from .enums import AccountType, OwnershipType, TaxStatus, LiabilityType, PaymentFrequency
# Import Security from assets.py to avoid duplicate definition
from .assets import Security

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    institution = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    type = Column(String, nullable=False)
    ownership = Column(String, nullable=False)
    tax_status = Column(String)
    is_external = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="accounts")
    assets = relationship("Asset", back_populates="account")
    investments = relationship("Investment", back_populates="account")
    # Updated relationship with consistent naming
    liabilities = relationship(
        "Liability", 
        primaryjoin="Account.id==Liability.account_id",
        back_populates="account"
    )
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Liability(Base):
    __tablename__ = "liabilities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    plan_id = Column(String, ForeignKey("financial_plans.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    original_balance = Column(Float)
    interest_rate = Column(Float, nullable=False)
    payment_amount = Column(Float)
    payment_frequency = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    ownership = Column(String, nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - updated with consistent naming
    client = relationship("Client", back_populates="liabilities")
    account = relationship(
        "Account", 
        primaryjoin="Liability.account_id==Account.id",
        back_populates="liabilities"
    )
    # Relationship to FinancialPlan
    plan = relationship(
        "FinancialPlan",
        foreign_keys=[plan_id],
        back_populates="liabilities"
    )
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class AccountTypeModel(Base):
    __tablename__ = "account_types"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    category = Column(String, nullable=False)  # Asset, Liability
    tax_treatment = Column(String)  # Taxable, Tax-Deferred, Tax-Free
    is_retirement = Column(Boolean, default=False)
    is_qualified = Column(Boolean, default=False)
    is_custodial = Column(Boolean, default=False)
    is_education = Column(Boolean, default=False)
    is_health = Column(Boolean, default=False)
    contribution_limits = Column(JSON)  # Yearly limits, catch-up provisions, etc.
    withdrawal_rules = Column(JSON)  # Early withdrawal penalties, RMDs, etc.
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    security_id = Column(String, ForeignKey("securities.id"))
    name = Column(String, nullable=False)
    ticker = Column(String)
    asset_class = Column(String)
    investment_type = Column(String)  # Stock, Bond, Mutual Fund, ETF, etc.
    shares = Column(Float, default=0.0)
    purchase_price = Column(Float)
    current_price = Column(Float)
    purchase_date = Column(Date)
    cost_basis = Column(Float)
    market_value = Column(Float)
    allocation_percentage = Column(Float)  # Percentage of account
    yield_rate = Column(Float)  # Dividend/Interest yield
    is_core_position = Column(Boolean, default=False)
    notes = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="investments")
    security = relationship("Security", foreign_keys=[security_id])
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
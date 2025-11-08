from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
from .enums import AssetType, OwnershipType

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    plan_id = Column(String, ForeignKey("financial_plans.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    basis = Column(Float)
    growth_rate = Column(Float, default=0.0)
    ownership = Column(String, nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Updated for consistency
    client = relationship("Client", back_populates="assets")
    plan = relationship(
        "FinancialPlan", 
        foreign_keys=[plan_id],
        back_populates="assets"
    )
    account = relationship("Account", back_populates="assets")
    allocations = relationship("Allocation", back_populates="asset")
    holdings = relationship("Holding", back_populates="asset")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class AssetClass(Base):
    __tablename__ = "asset_classes"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(String, ForeignKey("asset_classes.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("AssetClass", remote_side=[id], back_populates="children")
    children = relationship("AssetClass", remote_side=[parent_id], back_populates="parent")
    allocations = relationship("Allocation", back_populates="asset_class")
    securities = relationship("Security", back_populates="asset_class")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    asset_class_id = Column(String, ForeignKey("asset_classes.id"))
    percentage = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="allocations")
    asset_class = relationship("AssetClass", back_populates="allocations")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Security(Base):
    __tablename__ = "securities"
    
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Stock, Bond, ETF, Mutual Fund, Other
    price = Column(Float, nullable=False)
    price_date = Column(Date, nullable=False)
    asset_class_id = Column(String, ForeignKey("asset_classes.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset_class = relationship("AssetClass", back_populates="securities")
    holdings = relationship("Holding", back_populates="security")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    security_id = Column(String, ForeignKey("securities.id"))
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    basis = Column(Float)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="holdings")
    security = relationship("Security", back_populates="holdings")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
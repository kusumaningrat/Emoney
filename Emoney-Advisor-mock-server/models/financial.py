# models/financial.py - Version 3: Financial Planning Core (Schema Compliant)

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class PlanStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DRAFT = "Draft"
    ARCHIVED = "Archived"

class PlanType(str, enum.Enum):
    COMPREHENSIVE = "Comprehensive"
    RETIREMENT = "Retirement"
    EDUCATION = "Education"
    ESTATE = "Estate"
    TAX = "Tax"
    INSURANCE = "Insurance"

class GoalStatus(str, enum.Enum):
    ON_TRACK = "OnTrack"
    AT_RISK = "AtRisk"
    OFF_TRACK = "OffTrack"
    ACHIEVED = "Achieved"
    PAUSED = "Paused"

class GoalType(str, enum.Enum):
    RETIREMENT = "Retirement"
    EDUCATION = "Education"
    HOME_PURCHASE = "HomePurchase"
    EMERGENCY_FUND = "EmergencyFund"
    VACATION = "Vacation"
    DEBT_PAYOFF = "DebtPayoff"
    OTHER = "Other"

class ScenarioType(str, enum.Enum):
    BASE_CASE = "BaseCase"
    OPTIMISTIC = "Optimistic"
    PESSIMISTIC = "Pessimistic"
    WHAT_IF = "WhatIf"

class RetirementReadiness(str, enum.Enum):
    ON_TRACK = "OnTrack"
    BEHIND = "Behind"
    AHEAD = "Ahead"
    UNKNOWN = "Unknown"

# ============================================================================
# MODELS - Following eMoney V3 Schema Specification
# ============================================================================

class FinancialPlan(Base):
    """FinancialPlan Model - eMoney V3 Schema"""
    __tablename__ = "financial_plans"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    PlanID = Column("PlanID", String, primary_key=True, index=True)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    HouseholdID = Column("HouseholdID", String, ForeignKey("households.HouseholdID"), nullable=True)
    PlanName = Column("PlanName", String, nullable=False)
    PlanType = Column("PlanType", String, nullable=False, default=PlanType.COMPREHENSIVE.value)
    Status = Column("Status", String, nullable=False, default=PlanStatus.ACTIVE.value)
    StartDate = Column("StartDate", Date, nullable=True)
    EndDate = Column("EndDate", Date, nullable=True)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    LastReviewed = Column("LastReviewed", DateTime, nullable=True)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    CreatedBy = Column("CreatedBy", String, ForeignKey("users.UserID"), nullable=True)
    RetirementReadiness = Column("RetirementReadiness", String, nullable=True, default=RetirementReadiness.UNKNOWN.value)
    
    # Relationships
    client = relationship("Client", foreign_keys=[ClientID])
    household = relationship("Household", foreign_keys=[HouseholdID])
    created_by_user = relationship("User", foreign_keys=[CreatedBy])
    goals = relationship("Goal", back_populates="financial_plan")
    scenarios = relationship("Scenario", back_populates="financial_plan")
    cash_flows = relationship("CashFlow", back_populates="financial_plan")
    net_worths = relationship("NetWorth", back_populates="financial_plan")


class Goal(Base):
    """Goal Model - eMoney V3 Schema"""
    __tablename__ = "goals"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    GoalID = Column("GoalID", String, primary_key=True, index=True)
    PlanID = Column("PlanID", String, ForeignKey("financial_plans.PlanID"), nullable=False)
    ClientID = Column("ClientID", String, ForeignKey("clients.ClientID"), nullable=False)
    GoalType = Column("GoalType", String, nullable=False, default=GoalType.OTHER.value)
    GoalName = Column("GoalName", String, nullable=False)
    Description = Column("Description", String, nullable=True)
    TargetDate = Column("TargetDate", Date, nullable=True)
    TargetAmount = Column("TargetAmount", Numeric(18, 2), nullable=True)
    CurrentValue = Column("CurrentValue", Numeric(18, 2), nullable=True, default=0.00)
    MonthlyContribution = Column("MonthlyContribution", Numeric(18, 2), nullable=True, default=0.00)
    ProjectedValue = Column("ProjectedValue", Numeric(18, 2), nullable=True, default=0.00)
    FundingPercentage = Column("FundingPercentage", Numeric(5, 2), nullable=True, default=0.00)
    Priority = Column("Priority", Integer, nullable=True, default=1)
    Status = Column("Status", String, nullable=False, default=GoalStatus.ON_TRACK.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="goals")
    client = relationship("Client", foreign_keys=[ClientID])


class Scenario(Base):
    """Scenario Model - eMoney V3 Schema"""
    __tablename__ = "scenarios"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    ScenarioID = Column("ScenarioID", String, primary_key=True, index=True)
    PlanID = Column("PlanID", String, ForeignKey("financial_plans.PlanID"), nullable=False)
    ScenarioName = Column("ScenarioName", String, nullable=False)
    ScenarioType = Column("ScenarioType", String, nullable=False, default=ScenarioType.BASE_CASE.value)
    Description = Column("Description", String, nullable=True)
    Assumptions = Column("Assumptions", JSON, nullable=True)
    Results = Column("Results", JSON, nullable=True)
    Status = Column("Status", String, nullable=False, default=PlanStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="scenarios")


class CashFlow(Base):
    """CashFlow Model - eMoney V3 Schema"""
    __tablename__ = "cash_flows"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    CashFlowID = Column("CashFlowID", String, primary_key=True, index=True)
    PlanID = Column("PlanID", String, ForeignKey("financial_plans.PlanID"), nullable=False)
    Year = Column("Year", Integer, nullable=False)
    Month = Column("Month", Integer, nullable=True)
    TotalIncome = Column("TotalIncome", Numeric(18, 2), nullable=True, default=0.00)
    TotalExpenses = Column("TotalExpenses", Numeric(18, 2), nullable=True, default=0.00)
    NetCashFlow = Column("NetCashFlow", Numeric(18, 2), nullable=True, default=0.00)
    CumulativeCashFlow = Column("CumulativeCashFlow", Numeric(18, 2), nullable=True, default=0.00)
    InflationRate = Column("InflationRate", Numeric(5, 4), nullable=True, default=0.0300)
    Status = Column("Status", String, nullable=False, default=PlanStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="cash_flows")


class NetWorth(Base):
    """NetWorth Model - eMoney V3 Schema"""
    __tablename__ = "net_worths"
    __table_args__ = {'extend_existing': True}
    
    # Primary Fields - Following Schema Specification
    NetWorthID = Column("NetWorthID", String, primary_key=True, index=True)
    PlanID = Column("PlanID", String, ForeignKey("financial_plans.PlanID"), nullable=False)
    HouseholdID = Column("HouseholdID", String, ForeignKey("households.HouseholdID"), nullable=True)
    AsOfDate = Column("AsOfDate", Date, nullable=False)
    TotalAssets = Column("TotalAssets", Numeric(18, 2), nullable=True, default=0.00)
    TotalLiabilities = Column("TotalLiabilities", Numeric(18, 2), nullable=True, default=0.00)
    NetWorth = Column("NetWorth", Numeric(18, 2), nullable=True, default=0.00)
    LiquidAssets = Column("LiquidAssets", Numeric(18, 2), nullable=True, default=0.00)
    InvestedAssets = Column("InvestedAssets", Numeric(18, 2), nullable=True, default=0.00)
    UseAssets = Column("UseAssets", Numeric(18, 2), nullable=True, default=0.00)
    Status = Column("Status", String, nullable=False, default=PlanStatus.ACTIVE.value)
    CreatedDate = Column("CreatedDate", DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column("ModifiedDate", DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="net_worths")
    household = relationship("Household", foreign_keys=[HouseholdID])
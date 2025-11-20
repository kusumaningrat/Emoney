from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
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

class GoalStatus(str, enum.Enum):
    ON_TRACK = "OnTrack"
    OFF_TRACK = "OffTrack"
    ACHIEVED = "Achieved"
    DEFERRED = "Deferred"
    ABANDONED = "Abandoned"

class GoalType(str, enum.Enum):
    RETIREMENT = "Retirement"
    EDUCATION = "Education"
    HOME_PURCHASE = "HomePurchase"
    MAJOR_PURCHASE = "MajorPurchase"
    WEALTH_ACCUMULATION = "WealthAccumulation"
    DEBT_PAYOFF = "DebtPayoff"
    LEGACY = "Legacy"
    OTHER = "Other"

class ScenarioType(str, enum.Enum):
    BASE = "Base"
    BEST_CASE = "BestCase"
    WORST_CASE = "WorstCase"
    CUSTOM = "Custom"

class ScenarioStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class RetirementReadiness(str, enum.Enum):
    ON_TRACK = "OnTrack"
    NEEDS_ATTENTION = "NeedsAttention"
    OFF_TRACK = "OffTrack"
    RETIRED = "Retired"

# ============================================================================
# MODELS
# ============================================================================

class FinancialPlan(Base):
    """Financial Plan Model"""
    __tablename__ = "financial_plans"
    __table_args__ = {'extend_existing': True}
    
    plan_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    household_id = Column(String, ForeignKey("households.household_id"), nullable=True)
    plan_name = Column(String, nullable=False)
    plan_type = Column(String, nullable=True)  # Comprehensive, Retirement, Education, etc.
    status = Column(String, nullable=False, default=PlanStatus.ACTIVE.value)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_reviewed = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    retirement_readiness = Column(String, nullable=True)
    
    # Relationships to V2 models (viewonly, no back_populates)
    client = relationship("Client", foreign_keys=[client_id], viewonly=True)
    household = relationship("Household", foreign_keys=[household_id], viewonly=True)
    
    # Relationship to V1 models (viewonly, no back_populates)
    created_by_user = relationship("User", foreign_keys=[created_by], viewonly=True)
    
    # V3 Internal Relationships
    goals = relationship("Goal", back_populates="plan", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="plan", cascade="all, delete-orphan")
    cash_flows = relationship("CashFlow", back_populates="plan", cascade="all, delete-orphan")
    net_worths = relationship("NetWorth", back_populates="plan", cascade="all, delete-orphan")


class Goal(Base):
    """Goal Model"""
    __tablename__ = "goals"
    __table_args__ = {'extend_existing': True}
    
    goal_id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("financial_plans.plan_id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    goal_type = Column(String, nullable=False, default=GoalType.OTHER.value)
    goal_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(Date, nullable=True)
    target_amount = Column(Float, nullable=True, default=0.0)
    current_value = Column(Float, nullable=True, default=0.0)
    monthly_contribution = Column(Float, nullable=True, default=0.0)
    projected_value = Column(Float, nullable=True, default=0.0)
    funding_percentage = Column(Float, nullable=True, default=0.0)
    priority = Column(Integer, nullable=True, default=5)  # 1-10
    status = Column(String, nullable=False, default=GoalStatus.ON_TRACK.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("FinancialPlan", back_populates="goals")
    
    # Relationship to V2 models (viewonly, no back_populates)
    client = relationship("Client", foreign_keys=[client_id], viewonly=True)


class Scenario(Base):
    """Scenario Model - What-if analysis"""
    __tablename__ = "scenarios"
    __table_args__ = {'extend_existing': True}
    
    scenario_id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("financial_plans.plan_id"), nullable=False)
    scenario_name = Column(String, nullable=False)
    scenario_type = Column(String, nullable=False, default=ScenarioType.CUSTOM.value)
    description = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)  # JSON string of assumptions
    results = Column(Text, nullable=True)  # JSON string of results
    status = Column(String, nullable=False, default=ScenarioStatus.ACTIVE.value)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("FinancialPlan", back_populates="scenarios")


class CashFlow(Base):
    """Cash Flow Model - Projections over time"""
    __tablename__ = "cash_flows"
    __table_args__ = {'extend_existing': True}
    
    cash_flow_id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("financial_plans.plan_id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)  # 1-12, null means annual
    total_income = Column(Float, nullable=False, default=0.0)
    total_expenses = Column(Float, nullable=False, default=0.0)
    net_cash_flow = Column(Float, nullable=False, default=0.0)
    cumulative_cash_flow = Column(Float, nullable=True, default=0.0)
    inflation_rate = Column(Float, nullable=True, default=0.0)
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("FinancialPlan", back_populates="cash_flows")


class NetWorth(Base):
    """Net Worth Model - Snapshots over time"""
    __tablename__ = "net_worths"
    __table_args__ = {'extend_existing': True}
    
    net_worth_id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("financial_plans.plan_id"), nullable=False)
    household_id = Column(String, ForeignKey("households.household_id"), nullable=True)
    as_of_date = Column(Date, nullable=False)
    total_assets = Column(Float, nullable=False, default=0.0)
    total_liabilities = Column(Float, nullable=False, default=0.0)
    net_worth = Column(Float, nullable=False, default=0.0)
    liquid_assets = Column(Float, nullable=True, default=0.0)
    invested_assets = Column(Float, nullable=True, default=0.0)
    use_assets = Column(Float, nullable=True, default=0.0)  # Home, cars, etc.
    status = Column(String, nullable=False, default="Active")
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("FinancialPlan", back_populates="net_worths")
    
    # Relationship to V2 models (viewonly, no back_populates)
    household = relationship("Household", foreign_keys=[household_id], viewonly=True)
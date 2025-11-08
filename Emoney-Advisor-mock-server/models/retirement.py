from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .enums import RetirementPlanStatus

class RetirementPlan(Base):
    __tablename__ = "retirement_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    financial_plan_id = Column(String, ForeignKey("financial_plans.id"), nullable=True)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False)
    current_age = Column(Integer)
    spouse_age = Column(Integer)
    retirement_age = Column(Integer)
    spouse_retirement_age = Column(Integer)
    life_expectancy = Column(Integer)
    spouse_life_expectancy = Column(Integer)
    retirement_assets = Column(Numeric(precision=15, scale=2))
    annual_contributions = Column(Numeric(precision=15, scale=2))
    contribution_increase_rate = Column(Numeric(precision=6, scale=4))
    pre_retirement_return = Column(Numeric(precision=6, scale=4))
    post_retirement_return = Column(Numeric(precision=6, scale=4))
    inflation_rate = Column(Numeric(precision=6, scale=4))
    target_income = Column(Numeric(precision=15, scale=2))
    income_replacement_ratio = Column(Numeric(precision=6, scale=4))
    success_probability = Column(Integer)
    income_sources = Column(JSON)
    retirement_accounts = Column(JSON)
    retirement_shortfall = Column(Numeric(precision=15, scale=2))
    years_to_retirement = Column(Integer)
    required_savings_rate = Column(Numeric(precision=6, scale=4))
    risk_capacity = Column(String)
    strategies = Column(JSON)
    notes = Column(String)
    
    # Relationships
    client = relationship("Client", back_populates="retirement_plans")
    financial_plan = relationship("FinancialPlan", back_populates="retirement_plan")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    pensions = relationship("Pension", back_populates="retirement_plan")
    social_security_benefits = relationship("SocialSecurity", back_populates="retirement_plan")
    rmds = relationship("RMD", back_populates="retirement_plan")

class Pension(Base):
    __tablename__ = "pensions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    retirement_plan_id = Column(String, ForeignKey("retirement_plans.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    type = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    provider = Column(String)
    monthly_benefit = Column(Numeric(precision=15, scale=2))
    annual_benefit = Column(Numeric(precision=15, scale=2))
    start_age = Column(Integer)
    benefit_period = Column(String)
    cola_adjustment = Column(Boolean, default=False)
    cola_rate = Column(Numeric(precision=6, scale=4))
    payment_frequency = Column(String)
    survivor_benefit_percentage = Column(Integer)
    lump_sum_option = Column(Boolean, default=False)
    lump_sum_amount = Column(Numeric(precision=15, scale=2))
    early_retirement_option = Column(Boolean, default=False)
    early_retirement_age = Column(Integer)
    early_retirement_reduction = Column(Numeric(precision=6, scale=4))
    vesting_percentage = Column(Integer)
    years_of_service = Column(Integer)
    pension_max = Column(Numeric(precision=15, scale=2))
    notes = Column(String)
    
    # Relationships
    retirement_plan = relationship("RetirementPlan", back_populates="pensions")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class SocialSecurity(Base):
    __tablename__ = "social_security_benefits"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    retirement_plan_id = Column(String, ForeignKey("retirement_plans.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    recipient = Column(String, nullable=False)
    status = Column(String, nullable=False)
    current_age = Column(Integer)
    pia = Column(Numeric(precision=15, scale=2))
    early_retirement_age = Column(Integer)
    full_retirement_age = Column(Integer)
    maximum_retirement_age = Column(Integer)
    claim_age = Column(Integer)
    monthly_benefit_at_er = Column(Numeric(precision=15, scale=2))
    monthly_benefit_at_fra = Column(Numeric(precision=15, scale=2))
    monthly_benefit_at_max = Column(Numeric(precision=15, scale=2))
    monthly_benefit = Column(Numeric(precision=15, scale=2))
    annual_benefit = Column(Numeric(precision=15, scale=2))
    lifetime_benefit = Column(Numeric(precision=15, scale=2))
    cola_assumption = Column(Numeric(precision=6, scale=4))
    earnings_test_applicable = Column(Boolean, default=False)
    earnings_test_income = Column(Numeric(precision=15, scale=2))
    taxable_percentage = Column(Integer)
    spousal_benefit_eligible = Column(Boolean, default=False)
    spousal_benefit_amount = Column(Numeric(precision=15, scale=2))
    survivor_benefit_eligible = Column(Boolean, default=False)
    survivor_benefit_amount = Column(Numeric(precision=15, scale=2))
    optimization_strategy = Column(String)
    notes = Column(String)
    
    # Relationships
    retirement_plan = relationship("RetirementPlan", back_populates="social_security_benefits")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class RMD(Base):
    __tablename__ = "rmds"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    retirement_plan_id = Column(String, ForeignKey("retirement_plans.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False)
    current_age = Column(Integer)
    rmd_start_age = Column(Integer)
    total_ira_balance = Column(Numeric(precision=15, scale=2))
    current_rmd = Column(Numeric(precision=15, scale=2))
    rmd_accounts = Column(JSON)
    rmd_projection = Column(JSON)
    distribution_strategy = Column(String)
    tax_impact = Column(JSON)
    compliance_status = Column(String)
    previous_distributions = Column(JSON)
    notes = Column(String)
    
    # Relationships
    retirement_plan = relationship("RetirementPlan", back_populates="rmds")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
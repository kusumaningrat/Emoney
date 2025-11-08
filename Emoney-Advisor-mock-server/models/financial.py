from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSON, DateTime, Date, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class FinancialPlan(Base):
    """
    FinancialPlan model for storing financial planning data
    """
    __tablename__ = "financial_plans"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goals = relationship("Goal", back_populates="financial_plan", cascade="all, delete-orphan")
    monte_carlos = relationship("MonteCarlo", back_populates="financial_plan", cascade="all, delete-orphan")
    projections = relationship("Projection", back_populates="financial_plan", cascade="all, delete-orphan")
    retirement_plan = relationship("RetirementPlan", back_populates="financial_plan", uselist=False, cascade="all, delete-orphan")
    cash_flows = relationship("CashFlow", back_populates="financial_plan", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="financial_plan", cascade="all, delete-orphan")
    
    # Relationships for liabilities and assets
    liabilities = relationship(
        "Liability", 
        primaryjoin="FinancialPlan.id==Liability.plan_id", 
        cascade="all, delete-orphan",
        back_populates="plan"
    )
    
    client = relationship(
        "Client", 
        primaryjoin="FinancialPlan.client_id==Client.id",
        back_populates="plans"
    )
    assets = relationship(
        "Asset", 
        primaryjoin="FinancialPlan.id==Asset.plan_id", 
        cascade="all, delete-orphan",
        back_populates="plan"
    )
    
    # Updated relationship for Income (from this file)
    income_items = relationship("PlanIncome", back_populates="financial_plan", cascade="all, delete-orphan")
    
    # Updated relationship for Income from spending.py
    income_sources = relationship(
        "Income", 
        primaryjoin="FinancialPlan.id==Income.plan_id",
        back_populates="plan",
        foreign_keys="[Income.plan_id]"
    )
    
    # Updated relationship for Expense
    expenses = relationship(
        "Expense", 
        primaryjoin="FinancialPlan.id==Expense.plan_id",
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    
    tax_plans = relationship("TaxPlan", back_populates="financial_plan", cascade="all, delete-orphan")
    
    # Updated relationship to use Estate model
    estate_plan = relationship(
        "Estate", 
        back_populates="financial_plan", 
        uselist=False
    )
    
    insurance_plans = relationship("InsurancePlan", back_populates="financial_plan", cascade="all, delete-orphan")

class Scenario(Base):
    """
    Scenario model for storing financial planning scenarios
    """
    __tablename__ = "scenarios"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    status = Column(String, default="active")
    
    # Scenario assumptions and parameters
    retirement_age = Column(Integer)
    life_expectancy = Column(Integer)
    inflation_rate = Column(Float)
    investment_return_rate = Column(Float)
    tax_rate = Column(Float)
    withdrawal_strategy = Column(String)
    social_security_strategy = Column(String)
    parameters = Column(JSON)  # Flexible JSON for additional scenario parameters
    
    # Scenario results
    results_summary = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="scenarios")
    cash_flows = relationship("CashFlow", back_populates="scenario")
    monte_carlos = relationship("MonteCarlo", back_populates="scenario")

class InsurancePlan(Base):
    """
    InsurancePlan model for storing insurance planning data
    """
    __tablename__ = "insurance_plans"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'))
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Insurance-specific fields
    annual_premium_total = Column(Float, default=0.0)
    coverage_summary = Column(JSON)  # Summary of coverage across all policies
    
    # Relationships
    policies = relationship("Policy", back_populates="insurance_plan", cascade="all, delete-orphan")
    financial_plan = relationship("FinancialPlan", back_populates="insurance_plans")

class Policy(Base):
    """
    Policy model for storing individual insurance policies
    """
    __tablename__ = "policies"
    
    id = Column(String, primary_key=True)
    insurance_plan_id = Column(String, ForeignKey('insurance_plans.id'), nullable=False)
    policy_number = Column(String)
    policy_type = Column(String)  # e.g., "Life", "Health", "Auto", "Home", etc.
    insurer = Column(String)
    insured_name = Column(String)
    
    # Policy details
    coverage_amount = Column(Float)
    annual_premium = Column(Float)
    deductible = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    renewal_date = Column(Date)
    beneficiaries = Column(JSON)  # List of beneficiaries if applicable
    
    # Policy document info
    document_location = Column(String)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    insurance_plan = relationship("InsurancePlan", back_populates="policies")

class Goal(Base):
    """
    Goal model for storing financial goals
    """
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date)
    priority = Column(String)
    category = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    financial_plan = relationship("FinancialPlan", back_populates="goals")
    expenses = relationship("Expense", back_populates="goal")

class MonteCarlo(Base):
    """
    MonteCarlo model for storing Monte Carlo simulation results
    """
    __tablename__ = "monte_carlos"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    scenario_id = Column(String, ForeignKey('scenarios.id'), nullable=True)
    success_rate = Column(Float)
    iterations = Column(Integer)
    confidence_interval = Column(Float)
    median_ending_value = Column(Float)
    lowest_percentile_value = Column(Float)
    highest_percentile_value = Column(Float)
    results_detail = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="monte_carlos")
    scenario = relationship("Scenario", back_populates="monte_carlos")

class Projection(Base):
    """
    Projection model for storing financial projections by year
    """
    __tablename__ = "projections"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    year = Column(Integer, nullable=False)
    assets = Column(Float)
    liabilities = Column(Float)
    net_worth = Column(Float)
    income = Column(Float)
    expenses = Column(Float)
    cash_flow = Column(Float)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    financial_plan = relationship("FinancialPlan", back_populates="projections")

# class TaxPlan(Base):
#     """
#     TaxPlan model for storing tax planning data
#     """
#     __tablename__ = "tax_plans"
    
#     id = Column(String, primary_key=True)
#     plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
#     client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    
#     # Tax information
#     current_tax_rate = Column(Float)
#     projected_tax_rate = Column(Float)
#     taxable_income = Column(Float)
#     deductions = Column(Float)
#     tax_credits = Column(Float)
#     estimated_tax_liability = Column(Float)
    
#     # Tax saving strategies stored as JSON
#     tax_saving_strategies = Column(JSON)
    
#     # Timestamps
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     financial_tax_deductions = relationship("FinancialTaxDeduction", back_populates="tax_plan", cascade="all, delete-orphan")
#     tax_credits_rel = relationship("TaxCredit", back_populates="tax_plan", cascade="all, delete-orphan")
#     financial_plan = relationship("FinancialPlan", back_populates="tax_plans")

# class FinancialTaxDeduction(Base):  
#     """
#     FinancialTaxDeduction model for storing tax deduction information in financial plans
#     """
#     __tablename__ = "financial_tax_deductions"
    
#     id = Column(String, primary_key=True)
#     tax_plan_id = Column(String, ForeignKey('tax_plans.id'), nullable=False)
#     name = Column(String, nullable=False)
#     description = Column(Text)
#     amount = Column(Float)
#     category = Column(String)  # e.g., "Standard", "Itemized", etc.
#     is_available = Column(Boolean, default=True)
    
#     # Timestamps
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationship
#     tax_plan = relationship("TaxPlan", back_populates="financial_tax_deductions")

# class TaxCredit(Base):
#     """
#     TaxCredit model for storing tax credit information
#     """
#     __tablename__ = "tax_credits"
    
#     id = Column(String, primary_key=True)
#     tax_plan_id = Column(String, ForeignKey('tax_plans.id'), nullable=False)
#     name = Column(String, nullable=False)
#     description = Column(Text)
#     amount = Column(Float)
#     category = Column(String)  # e.g., "Child Tax Credit", "Education Credit", etc.
#     is_refundable = Column(Boolean, default=False)
#     is_available = Column(Boolean, default=True)
    
#     # Timestamps
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationship
#     tax_plan = relationship("TaxPlan", back_populates="tax_credits_rel")

class CashFlow(Base):
    """
    CashFlow model for storing cash flow information
    """
    __tablename__ = "cash_flows"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    scenario_id = Column(String, ForeignKey('scenarios.id'), nullable=True)
    
    # Income
    salary_income = Column(Float, default=0.0)
    business_income = Column(Float, default=0.0)
    investment_income = Column(Float, default=0.0)
    rental_income = Column(Float, default=0.0)
    other_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    
    # Expenses
    housing_expense = Column(Float, default=0.0)
    utilities_expense = Column(Float, default=0.0)
    food_expense = Column(Float, default=0.0)
    transportation_expense = Column(Float, default=0.0)
    healthcare_expense = Column(Float, default=0.0)
    insurance_expense = Column(Float, default=0.0)
    debt_payments = Column(Float, default=0.0)
    entertainment_expense = Column(Float, default=0.0)
    personal_expense = Column(Float, default=0.0)
    other_expense = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    
    # Net Cash Flow
    net_cash_flow = Column(Float, default=0.0)
    
    # Time period
    period = Column(String)  # e.g., "Monthly", "Annual"
    year = Column(Integer)  # Which year this cash flow represents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_plan = relationship("FinancialPlan", back_populates="cash_flows")
    scenario = relationship("Scenario", back_populates="cash_flows")

class PlanIncome(Base):
    """
    Income model for storing income sources in financial plan models
    Note: This is different from the Income model in spending.py
    """
    __tablename__ = "incomes"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey('financial_plans.id'), nullable=False)
    name = Column(String, nullable=False)
    income_type = Column(String)  # e.g., "Salary", "Dividend", "Rental", etc.
    amount = Column(Float)
    frequency = Column(String)  # e.g., "Monthly", "Annual", etc.
    start_date = Column(Date)
    end_date = Column(Date)
    growth_rate = Column(Float)
    details = Column(JSON)  # Additional details specific to income type
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Updated relationship
    financial_plan = relationship("FinancialPlan", back_populates="income_items")
# tax.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .enums import TaxDocumentType, TaxFilingStatus

class Tax(Base):
    __tablename__ = "taxes"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"))
    tax_year = Column(Integer, nullable=False)
    filing_status = Column(String, nullable=False)
    adjusted_gross_income = Column(Numeric(precision=15, scale=2), nullable=False)
    taxable_income = Column(Numeric(precision=15, scale=2), nullable=False)
    federal_tax = Column(Numeric(precision=15, scale=2), nullable=False)
    state_tax = Column(Numeric(precision=15, scale=2))
    state = Column(String)
    deductions = Column(JSON, nullable=False)
    credits = Column(JSON)
    payments = Column(JSON, nullable=False)
    refund_amount = Column(Numeric(precision=15, scale=2))
    amount_owed = Column(Numeric(precision=15, scale=2))
    filing_date = Column(Date, nullable=False)
    notes = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="taxes")
    documents = relationship("TaxDocument", back_populates="tax")
    tax_payments = relationship("TaxPayment", back_populates="tax")
    tax_deductions = relationship("TaxDeduction", back_populates="tax")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class TaxDocument(Base):
    __tablename__ = "tax_documents"
    
    id = Column(String, primary_key=True, index=True)
    tax_id = Column(String, ForeignKey("taxes.id"))
    document_id = Column(String, ForeignKey("vault_documents.id"))
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    tax_year = Column(Integer, nullable=False)
    form_number = Column(String)
    issuer = Column(String)
    recipient = Column(String)
    issue_date = Column(Date)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tax = relationship("Tax", back_populates="documents")
    document = relationship("VaultDocument", back_populates="tax_documents")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class TaxPayment(Base):
    __tablename__ = "tax_payments"
    
    id = Column(String, primary_key=True, index=True)
    tax_id = Column(String, ForeignKey("taxes.id"))
    payment_type = Column(String, nullable=False)  # Withholding, Estimated, Direct
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    reference_number = Column(String)
    description = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tax = relationship("Tax", back_populates="tax_payments")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class TaxDeduction(Base):
    __tablename__ = "tax_deductions"
    
    id = Column(String, primary_key=True, index=True)
    tax_id = Column(String, ForeignKey("taxes.id"))
    deduction_type = Column(String, nullable=False)  # Standard, Itemized, Business, etc.
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tax = relationship("Tax", back_populates="tax_deductions")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

# ==================== NEW MODELS ====================

class TaxPlan(Base):
    """
    TaxPlan model for storing tax planning strategies and projections
    """
    __tablename__ = "tax_plans"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    plan_id = Column(String, ForeignKey("financial_plans.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    description = Column(String)
    tax_year = Column(Integer, nullable=False)
    filing_status = Column(String, nullable=False)
    projected_income = Column(Numeric(precision=15, scale=2))
    projected_deductions = Column(Numeric(precision=15, scale=2))
    projected_credits = Column(Numeric(precision=15, scale=2))
    estimated_tax_liability = Column(Numeric(precision=15, scale=2))
    effective_tax_rate = Column(Numeric(precision=5, scale=2))
    marginal_tax_rate = Column(Numeric(precision=5, scale=2))
    strategy_notes = Column(String)
    optimization_opportunities = Column(JSON)
    risk_factors = Column(JSON)
    assumptions = Column(JSON)
    status = Column(String, default="draft")
    
    # Relationships
    client = relationship("Client")
    
    financial_plan = relationship("FinancialPlan", back_populates="tax_plans")
    
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    brackets = relationship("TaxBracket", back_populates="tax_plan")
    deductions = relationship("Deduction", back_populates="tax_plan")
    credits = relationship("Credit", back_populates="tax_plan")




    financial_tax_deductions = relationship("FinancialTaxDeduction", back_populates="tax_plan", cascade="all, delete-orphan")
    tax_credits_rel = relationship("TaxCredit", back_populates="tax_plan", cascade="all, delete-orphan")

class TaxBracket(Base):
    """
    TaxBracket model for storing tax bracket information and calculations
    """
    __tablename__ = "tax_brackets"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    tax_plan_id = Column(String, ForeignKey("tax_plans.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    bracket_type = Column(String, nullable=False)  # federal, state, local, fica, medicare
    tax_year = Column(Integer, nullable=False)
    filing_status = Column(String, nullable=False)
    income_min = Column(Numeric(precision=15, scale=2), nullable=False)
    income_max = Column(Numeric(precision=15, scale=2))
    rate = Column(Numeric(precision=5, scale=2), nullable=False)
    base_tax = Column(Numeric(precision=15, scale=2))
    taxable_income_in_bracket = Column(Numeric(precision=15, scale=2))
    tax_in_bracket = Column(Numeric(precision=15, scale=2))
    state = Column(String)  # For state tax brackets
    notes = Column(String)
    
    # Relationships
    tax_plan = relationship("TaxPlan", back_populates="brackets")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Deduction(Base):
    """
    Deduction model for storing tax deduction planning and tracking
    """
    __tablename__ = "deductions"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    tax_plan_id = Column(String, ForeignKey("tax_plans.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    description = Column(String)
    deduction_type = Column(String, nullable=False)  # standard, itemized, above_line, business
    category = Column(String, nullable=False)  # mortgage_interest, charitable, medical, state_tax, etc.
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    max_allowed = Column(Numeric(precision=15, scale=2))
    phase_out_start = Column(Numeric(precision=15, scale=2))
    phase_out_end = Column(Numeric(precision=15, scale=2))
    is_recurring = Column(Boolean, default=False)
    frequency = Column(String)  # monthly, quarterly, annual
    start_date = Column(Date)
    end_date = Column(Date)
    documentation_required = Column(Boolean, default=True)
    documentation_status = Column(String)  # complete, incomplete, pending
    tax_year = Column(Integer)
    notes = Column(String)
    limitations = Column(JSON)
    qualifications = Column(JSON)
    
    # Relationships
    tax_plan = relationship("TaxPlan", back_populates="deductions")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Credit(Base):
    """
    Credit model for storing tax credit planning and tracking
    """
    __tablename__ = "credits"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    tax_plan_id = Column(String, ForeignKey("tax_plans.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    description = Column(String)
    credit_type = Column(String, nullable=False)  # nonrefundable, refundable, partially_refundable
    category = Column(String, nullable=False)  # child_tax, earned_income, education, energy, etc.
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    max_allowed = Column(Numeric(precision=15, scale=2))
    is_refundable = Column(Boolean, default=False)
    refundable_percentage = Column(Numeric(precision=5, scale=2))
    phase_out_start = Column(Numeric(precision=15, scale=2))
    phase_out_end = Column(Numeric(precision=15, scale=2))
    income_limit = Column(Numeric(precision=15, scale=2))
    carryforward_allowed = Column(Boolean, default=False)
    carryforward_years = Column(Integer)
    carryforward_amount = Column(Numeric(precision=15, scale=2))
    is_recurring = Column(Boolean, default=False)
    frequency = Column(String)  # annual, one_time
    eligibility_requirements = Column(JSON)
    documentation_required = Column(Boolean, default=True)
    documentation_status = Column(String)  # complete, incomplete, pending
    tax_year = Column(Integer)
    notes = Column(String)
    qualifications = Column(JSON)
    
    # Relationships
    tax_plan = relationship("TaxPlan", back_populates="credits")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")



class FinancialTaxDeduction(Base):  
    """
    FinancialTaxDeduction model for storing tax deduction information in financial plans
    """
    __tablename__ = "financial_tax_deductions"
    
    id = Column(String, primary_key=True)
    tax_plan_id = Column(String, ForeignKey('tax_plans.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)  # Changed from Text to String
    amount = Column(Numeric(precision=15, scale=2))  # Changed from Float
    category = Column(String)  # e.g., "Standard", "Itemized", etc.
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    tax_plan = relationship("TaxPlan", back_populates="financial_tax_deductions")

class TaxCredit(Base):
    """
    TaxCredit model for storing tax credit information
    """
    __tablename__ = "tax_credits"
    
    id = Column(String, primary_key=True)
    tax_plan_id = Column(String, ForeignKey('tax_plans.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)  # Changed from Text to String
    amount = Column(Numeric(precision=15, scale=2))  # Changed from Float
    category = Column(String)  # e.g., "Child Tax Credit", "Education Credit", etc.
    is_refundable = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    tax_plan = relationship("TaxPlan", back_populates="tax_credits_rel")
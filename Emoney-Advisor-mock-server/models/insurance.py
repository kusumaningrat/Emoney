from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .enums import InsuranceType, InsuranceStatus

class Insurance(Base):
    __tablename__ = "insurances"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False)
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    total_coverage = Column(Numeric(precision=15, scale=2))
    annual_premiums = Column(Numeric(precision=15, scale=2))
    coverage_score = Column(Integer)
    coverage_gaps = Column(JSON)
    recommendations = Column(JSON)
    notes = Column(String)
    
    # Relationships
    client = relationship("Client", back_populates="insurances")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    policies = relationship("InsurancePolicy", back_populates="insurance")

class InsurancePolicy(Base):
    """
    InsurancePolicy model for storing insurance policies in the insurance management system
    """
    __tablename__ = "insurance_policies"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    insurance_id = Column(String, ForeignKey("insurances.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    policy_type = Column(String, nullable=False)
    policy_subtype = Column(String, nullable=False)
    policy_number = Column(String)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date)
    term = Column(String)
    premium_amount = Column(Numeric(precision=15, scale=2))
    premium_frequency = Column(String)
    coverage_amount = Column(Numeric(precision=15, scale=2))
    insured = Column(JSON)
    owner = Column(String)
    beneficiaries = Column(JSON)
    renewal_type = Column(String)
    payment_method = Column(String)
    agent_name = Column(String)
    agent_contact = Column(String)
    underwriting_class = Column(String)
    policy_features = Column(JSON)
    notes = Column(String)
    
    # Relationships
    insurance = relationship("Insurance", back_populates="policies")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    coverages = relationship("Coverage", back_populates="policy")
    premiums = relationship("Premium", back_populates="policy")

class Coverage(Base):
    __tablename__ = "coverages"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    policy_id = Column(String, ForeignKey("insurance_policies.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    coverage_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    coverage_amount = Column(Numeric(precision=15, scale=2))
    deductible = Column(Numeric(precision=15, scale=2))
    coinsurance_percentage = Column(Integer)
    out_of_pocket_max = Column(Numeric(precision=15, scale=2))
    annual_limit = Column(Numeric(precision=15, scale=2))
    lifetime_limit = Column(Numeric(precision=15, scale=2))
    exclusions = Column(JSON)
    waiting_period = Column(Integer)
    elimination_period = Column(Integer)
    benefit_period = Column(String)
    covered_perils = Column(JSON)
    riders = Column(JSON)
    notes = Column(String)
    
    # Relationships
    policy = relationship("InsurancePolicy", back_populates="coverages")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")

class Premium(Base):
    __tablename__ = "premiums"
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    policy_id = Column(String, ForeignKey("insurance_policies.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    premium_type = Column(String, nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    frequency = Column(String, nullable=False)
    due_date = Column(Date)
    paid_date = Column(Date)
    payment_method = Column(String)
    is_paid = Column(Boolean, default=False)
    billing_period_start = Column(Date)
    billing_period_end = Column(Date)
    notes = Column(String)
    
    # Relationships
    policy = relationship("InsurancePolicy", back_populates="premiums")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
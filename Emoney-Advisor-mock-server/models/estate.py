from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship as sqlalchemy_relationship
from database import Base
from datetime import datetime
from .enums import EstateDocumentType, EstateStatus

class Estate(Base):
    __tablename__ = "estates"
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
    complexity = Column(String, nullable=False)
    marital_status = Column(String, nullable=False)
    total_estate_value = Column(Numeric(precision=15, scale=2), nullable=False)
    taxable_estate = Column(Numeric(precision=15, scale=2))
    estimated_tax = Column(Numeric(precision=15, scale=2))
    tax_status = Column(String)
    asset_composition = Column(JSON)
    state_of_residence = Column(String)
    has_will = Column(Boolean, default=False)
    has_trust = Column(Boolean, default=False)
    has_power_of_attorney = Column(Boolean, default=False)
    has_healthcare_directive = Column(Boolean, default=False)
    has_beneficiary_designations = Column(Boolean, default=False)
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    planning_objectives = Column(JSON)
    planning_strategies = Column(JSON)
    documents = Column(JSON)
    advisors = Column(JSON)
    notes = Column(String)
    
    # Relationships
    client = sqlalchemy_relationship("Client", back_populates="estates")
    financial_plan = sqlalchemy_relationship("FinancialPlan", back_populates="estate_plan")
    creator = sqlalchemy_relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = sqlalchemy_relationship("User", foreign_keys=[updated_by], overlaps="creator")
    wills = sqlalchemy_relationship("Will", back_populates="estate")
    trusts = sqlalchemy_relationship("Trust", back_populates="estate")
    beneficiaries = sqlalchemy_relationship("Beneficiary", back_populates="estate")

class Will(Base):
    __tablename__ = "wills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    estate_id = Column(String, ForeignKey("estates.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False)
    type = Column(String, nullable=False)
    execution_date = Column(Date)
    last_updated = Column(Date)
    location = Column(String)
    executor = Column(JSON)
    alternate_executor = Column(JSON)
    guardian_for_minors = Column(JSON)
    specific_bequests = Column(JSON)
    residuary_estate = Column(JSON)
    testamentary_trust = Column(Boolean, default=False)
    no_contest_clause = Column(Boolean, default=False)
    digital_assets = Column(Boolean, default=False)
    pet_provisions = Column(Boolean, default=False)
    charitable_provisions = Column(Boolean, default=False)
    special_instructions = Column(String)
    attorney = Column(JSON)
    document_id = Column(String)
    notes = Column(String)
    
    # Relationships
    estate = sqlalchemy_relationship("Estate", back_populates="wills")
    client = sqlalchemy_relationship("Client")
    creator = sqlalchemy_relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = sqlalchemy_relationship("User", foreign_keys=[updated_by], overlaps="creator")
    beneficiaries = sqlalchemy_relationship("Beneficiary", back_populates="will")

class Trust(Base):
    __tablename__ = "trusts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    estate_id = Column(String, ForeignKey("estates.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    trust_type = Column(String, nullable=False)
    purpose = Column(String)
    execution_date = Column(Date)
    amendment_date = Column(Date)
    location = Column(String)
    grantor = Column(JSON)
    co_grantor = Column(JSON)
    trustee = Column(JSON)
    successor_trustee = Column(JSON)
    is_funded = Column(Boolean, default=False)
    trust_value = Column(Numeric(precision=15, scale=2))
    funding_source = Column(JSON)
    distribution_provisions = Column(JSON)
    spendthrift_provision = Column(Boolean, default=False)
    generation_skipping = Column(Boolean, default=False)
    tax_id = Column(String)
    tax_filing_requirements = Column(JSON)
    attorney = Column(JSON)
    document_id = Column(String)
    notes = Column(String)
    
    # Relationships
    estate = sqlalchemy_relationship("Estate", back_populates="trusts")
    client = sqlalchemy_relationship("Client")
    creator = sqlalchemy_relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = sqlalchemy_relationship("User", foreign_keys=[updated_by], overlaps="creator")
    beneficiaries = sqlalchemy_relationship("Beneficiary", back_populates="trust")

class Beneficiary(Base):
    __tablename__ = "beneficiaries"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    estate_id = Column(String, ForeignKey("estates.id"))
    will_id = Column(String, ForeignKey("wills.id"))
    trust_id = Column(String, ForeignKey("trusts.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    status = Column(String, nullable=False)
    primary = Column(Boolean, default=True)
    contingent = Column(Boolean, default=False)
    percentage = Column(Numeric(precision=5, scale=2), nullable=False)
    priority = Column(Integer, nullable=False)
    asset_types = Column(JSON)
    specific_assets = Column(JSON)
    details = Column(JSON)
    conditions = Column(JSON)
    notes = Column(String)
    
    # Relationships
    estate = sqlalchemy_relationship("Estate", back_populates="beneficiaries")
    will = sqlalchemy_relationship("Will", back_populates="beneficiaries")
    trust = sqlalchemy_relationship("Trust", back_populates="beneficiaries")
    client = sqlalchemy_relationship("Client")
    creator = sqlalchemy_relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = sqlalchemy_relationship("User", foreign_keys=[updated_by], overlaps="creator")
# services/insurance_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.insurance import Insurance, InsurancePolicy, Coverage, Premium
from models.enums import InsuranceStatus
from services.service_base import BaseService
from datetime import datetime
import uuid

class InsuranceService(BaseService[Insurance]):
    def __init__(self, db: Session):
        super().__init__(db, Insurance)
    
    # ==================== Insurance Methods ====================
    
    def get_client_insurances(self, client_id: str):
        """Get all insurance records for a client"""
        insurances = self.db.query(Insurance).filter(Insurance.client_id == client_id).all()
        return [self._insurance_to_dict(insurance) for insurance in insurances]
    
    def get_insurances_by_status(self, status: str):
        """Get all insurance records by status"""
        insurances = self.db.query(Insurance).filter(Insurance.status == status).all()
        return [self._insurance_to_dict(insurance) for insurance in insurances]
    
    def create_insurance(self, insurance_data: Dict[str, Any], user_id: str = None):
        """Create a new insurance record"""
        if 'id' not in insurance_data:
            insurance_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in insurance_data:
            insurance_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in insurance_data:
            insurance_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in insurance_data:
                insurance_data['created_by'] = user_id
                
            if 'updated_by' not in insurance_data:
                insurance_data['updated_by'] = user_id
                
        insurance = Insurance(**insurance_data)
        self.db.add(insurance)
        self.db.commit()
        self.db.refresh(insurance)
        
        return self._insurance_to_dict(insurance)
    
    def update_insurance(self, insurance_id: str, insurance_data: Dict[str, Any], user_id: str = None):
        """Update an existing insurance record"""
        insurance = self.db.query(Insurance).filter(Insurance.id == insurance_id).first()
        if not insurance:
            return None
            
        for key, value in insurance_data.items():
            if hasattr(insurance, key):
                setattr(insurance, key, value)
                
        insurance.updated_at = datetime.utcnow()
        
        if user_id:
            insurance.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(insurance)
        
        return self._insurance_to_dict(insurance)
    
    def get_insurance_summary(self, insurance_id: str):
        """Get summary analytics for an insurance record"""
        insurance = self.db.query(Insurance).filter(Insurance.id == insurance_id).first()
        if not insurance:
            return None
        
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.insurance_id == insurance_id
        ).all()
        
        total_policies = len(policies)
        active_policies = len([p for p in policies if p.status == "active"])
        total_coverage = sum([p.coverage_amount or 0 for p in policies])
        total_premiums = sum([p.premium_amount or 0 for p in policies])
        
        return {
            "insurance_id": insurance_id,
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_coverage": float(total_coverage),
            "total_annual_premiums": float(total_premiums),
            "coverage_score": insurance.coverage_score,
            "coverage_gaps": insurance.coverage_gaps,
            "recommendations": insurance.recommendations
        }
    
    # ==================== Insurance Policy Methods ====================
    
    def get_insurance_policies(self, insurance_id: str):
        """Get all policies for an insurance record"""
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.insurance_id == insurance_id
        ).all()
        return [self._policy_to_dict(policy) for policy in policies]
    
    def get_client_policies(self, client_id: str):
        """Get all policies for a client"""
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.client_id == client_id
        ).all()
        return [self._policy_to_dict(policy) for policy in policies]
    
    def get_policies_by_type(self, policy_type: str):
        """Get all policies by type"""
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.policy_type == policy_type
        ).all()
        return [self._policy_to_dict(policy) for policy in policies]
    
    def get_policy_by_id(self, policy_id: str):
        """Get policy by ID"""
        policy = self.db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            return None
        return self._policy_to_dict(policy)
    
    def create_policy(self, policy_data: Dict[str, Any], user_id: str = None):
        """Create a new insurance policy"""
        if 'id' not in policy_data:
            policy_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in policy_data:
            policy_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in policy_data:
            policy_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in policy_data:
                policy_data['created_by'] = user_id
                
            if 'updated_by' not in policy_data:
                policy_data['updated_by'] = user_id
                
        policy = InsurancePolicy(**policy_data)
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        # Update insurance totals if insurance_id is provided
        if 'insurance_id' in policy_data:
            self.recalculate_insurance_totals(policy_data['insurance_id'])
        
        return self._policy_to_dict(policy)
    
    def update_policy(self, policy_id: str, policy_data: Dict[str, Any], user_id: str = None):
        """Update an existing insurance policy"""
        policy = self.db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            return None
            
        insurance_id = policy.insurance_id
            
        for key, value in policy_data.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
                
        policy.updated_at = datetime.utcnow()
        
        if user_id:
            policy.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(policy)
        
        # Update insurance totals
        self.recalculate_insurance_totals(insurance_id)
        
        return self._policy_to_dict(policy)
    
    def delete_policy(self, policy_id: str):
        """Delete an insurance policy"""
        policy = self.db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            return False
            
        insurance_id = policy.insurance_id
            
        self.db.delete(policy)
        self.db.commit()
        
        # Update insurance totals
        if insurance_id:
            self.recalculate_insurance_totals(insurance_id)
        
        return True
    
    def get_policy_summary(self, policy_id: str):
        """Get summary analytics for a specific policy"""
        policy = self.db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
        if not policy:
            return None
        
        coverages = self.db.query(Coverage).filter(Coverage.policy_id == policy_id).all()
        premiums = self.db.query(Premium).filter(Premium.policy_id == policy_id).all()
        
        total_coverages = len(coverages)
        total_coverage_amount = sum([c.coverage_amount or 0 for c in coverages])
        total_premiums_paid = sum([p.amount for p in premiums if p.is_paid])
        outstanding_premiums = sum([p.amount for p in premiums if not p.is_paid])
        
        return {
            "policy_id": policy_id,
            "policy_name": policy.name,
            "policy_type": policy.policy_type,
            "provider": policy.provider,
            "status": policy.status,
            "total_coverages": total_coverages,
            "total_coverage_amount": float(total_coverage_amount),
            "premium_amount": float(policy.premium_amount or 0),
            "premium_frequency": policy.premium_frequency,
            "total_premiums_paid": float(total_premiums_paid),
            "outstanding_premiums": float(outstanding_premiums)
        }
    
    # ==================== Coverage Methods ====================
    
    def get_policy_coverages(self, policy_id: str):
        """Get all coverages for a policy"""
        coverages = self.db.query(Coverage).filter(Coverage.policy_id == policy_id).all()
        return [self._coverage_to_dict(coverage) for coverage in coverages]
    
    def get_client_coverages(self, client_id: str):
        """Get all coverages for a client"""
        coverages = self.db.query(Coverage).filter(Coverage.client_id == client_id).all()
        return [self._coverage_to_dict(coverage) for coverage in coverages]
    
    def get_coverage_by_id(self, coverage_id: str):
        """Get coverage by ID"""
        coverage = self.db.query(Coverage).filter(Coverage.id == coverage_id).first()
        if not coverage:
            return None
        return self._coverage_to_dict(coverage)
    
    def create_coverage(self, coverage_data: Dict[str, Any], user_id: str = None):
        """Create a new coverage"""
        if 'id' not in coverage_data:
            coverage_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in coverage_data:
            coverage_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in coverage_data:
            coverage_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in coverage_data:
                coverage_data['created_by'] = user_id
                
            if 'updated_by' not in coverage_data:
                coverage_data['updated_by'] = user_id
                
        coverage = Coverage(**coverage_data)
        self.db.add(coverage)
        self.db.commit()
        self.db.refresh(coverage)
        
        return self._coverage_to_dict(coverage)
    
    def update_coverage(self, coverage_id: str, coverage_data: Dict[str, Any], user_id: str = None):
        """Update an existing coverage"""
        coverage = self.db.query(Coverage).filter(Coverage.id == coverage_id).first()
        if not coverage:
            return None
            
        for key, value in coverage_data.items():
            if hasattr(coverage, key):
                setattr(coverage, key, value)
                
        coverage.updated_at = datetime.utcnow()
        
        if user_id:
            coverage.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(coverage)
        
        return self._coverage_to_dict(coverage)
    
    def delete_coverage(self, coverage_id: str):
        """Delete a coverage"""
        coverage = self.db.query(Coverage).filter(Coverage.id == coverage_id).first()
        if not coverage:
            return False
            
        self.db.delete(coverage)
        self.db.commit()
        
        return True
    
    # ==================== Premium Methods ====================
    
    def get_policy_premiums(self, policy_id: str):
        """Get all premiums for a policy"""
        premiums = self.db.query(Premium).filter(Premium.policy_id == policy_id).all()
        return [self._premium_to_dict(premium) for premium in premiums]
    
    def get_client_premiums(self, client_id: str):
        """Get all premiums for a client"""
        premiums = self.db.query(Premium).filter(Premium.client_id == client_id).all()
        return [self._premium_to_dict(premium) for premium in premiums]
    
    def get_unpaid_premiums(self, client_id: str = None):
        """Get all unpaid premiums, optionally filtered by client"""
        query = self.db.query(Premium).filter(Premium.is_paid == False)
        
        if client_id:
            query = query.filter(Premium.client_id == client_id)
        
        premiums = query.all()
        return [self._premium_to_dict(premium) for premium in premiums]
    
    def get_premium_by_id(self, premium_id: str):
        """Get premium by ID"""
        premium = self.db.query(Premium).filter(Premium.id == premium_id).first()
        if not premium:
            return None
        return self._premium_to_dict(premium)
    
    def create_premium(self, premium_data: Dict[str, Any], user_id: str = None):
        """Create a new premium"""
        if 'id' not in premium_data:
            premium_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in premium_data:
            premium_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in premium_data:
            premium_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in premium_data:
                premium_data['created_by'] = user_id
                
            if 'updated_by' not in premium_data:
                premium_data['updated_by'] = user_id
                
        premium = Premium(**premium_data)
        self.db.add(premium)
        self.db.commit()
        self.db.refresh(premium)
        
        return self._premium_to_dict(premium)
    
    def update_premium(self, premium_id: str, premium_data: Dict[str, Any], user_id: str = None):
        """Update an existing premium"""
        premium = self.db.query(Premium).filter(Premium.id == premium_id).first()
        if not premium:
            return None
            
        for key, value in premium_data.items():
            if hasattr(premium, key):
                setattr(premium, key, value)
                
        premium.updated_at = datetime.utcnow()
        
        if user_id:
            premium.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(premium)
        
        return self._premium_to_dict(premium)
    
    def delete_premium(self, premium_id: str):
        """Delete a premium"""
        premium = self.db.query(Premium).filter(Premium.id == premium_id).first()
        if not premium:
            return False
            
        self.db.delete(premium)
        self.db.commit()
        
        return True
    
    def mark_premium_paid(self, premium_id: str, paid_date: datetime = None):
        """Mark a premium as paid"""
        premium = self.db.query(Premium).filter(Premium.id == premium_id).first()
        if not premium:
            return None
            
        premium.is_paid = True
        premium.paid_date = paid_date or datetime.utcnow().date()
        premium.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(premium)
        
        return self._premium_to_dict(premium)
    
    # ==================== Helper Methods ====================
    
    def recalculate_insurance_totals(self, insurance_id: str):
        """Recalculate total coverage and premiums for an insurance record"""
        insurance = self.db.query(Insurance).filter(Insurance.id == insurance_id).first()
        if not insurance:
            return
            
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.insurance_id == insurance_id
        ).all()
        
        total_coverage = sum([p.coverage_amount or 0 for p in policies])
        total_premiums = sum([p.premium_amount or 0 for p in policies])
        
        insurance.total_coverage = total_coverage
        insurance.annual_premiums = total_premiums
        insurance.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    # ==================== Dictionary Conversion Methods ====================
    
    def _insurance_to_dict(self, insurance: Insurance) -> Dict[str, Any]:
        """Helper method to convert Insurance model to dictionary"""
        return {
            "id": insurance.id,
            "workspace_id": insurance.workspace_id,
            "client_id": insurance.client_id,
            "status": insurance.status,
            "last_review_date": insurance.last_review_date.isoformat() if insurance.last_review_date else None,
            "next_review_date": insurance.next_review_date.isoformat() if insurance.next_review_date else None,
            "total_coverage": float(insurance.total_coverage) if insurance.total_coverage is not None else None,
            "annual_premiums": float(insurance.annual_premiums) if insurance.annual_premiums is not None else None,
            "coverage_score": insurance.coverage_score,
            "coverage_gaps": insurance.coverage_gaps,
            "recommendations": insurance.recommendations,
            "notes": insurance.notes,
            "created_by": insurance.created_by,
            "updated_by": insurance.updated_by,
            "created_at": insurance.created_at.isoformat() if insurance.created_at else None,
            "updated_at": insurance.updated_at.isoformat() if insurance.updated_at else None
        }
    
    def _policy_to_dict(self, policy: InsurancePolicy) -> Dict[str, Any]:
        """Helper method to convert InsurancePolicy model to dictionary"""
        return {
            "id": policy.id,
            "workspace_id": policy.workspace_id,
            "insurance_id": policy.insurance_id,
            "client_id": policy.client_id,
            "name": policy.name,
            "policy_type": policy.policy_type,
            "policy_subtype": policy.policy_subtype,
            "policy_number": policy.policy_number,
            "provider": policy.provider,
            "status": policy.status,
            "effective_date": policy.effective_date.isoformat() if policy.effective_date else None,
            "expiration_date": policy.expiration_date.isoformat() if policy.expiration_date else None,
            "term": policy.term,
            "premium_amount": float(policy.premium_amount) if policy.premium_amount is not None else None,
            "premium_frequency": policy.premium_frequency,
            "coverage_amount": float(policy.coverage_amount) if policy.coverage_amount is not None else None,
            "insured": policy.insured,
            "owner": policy.owner,
            "beneficiaries": policy.beneficiaries,
            "renewal_type": policy.renewal_type,
            "payment_method": policy.payment_method,
            "agent_name": policy.agent_name,
            "agent_contact": policy.agent_contact,
            "underwriting_class": policy.underwriting_class,
            "policy_features": policy.policy_features,
            "notes": policy.notes,
            "created_by": policy.created_by,
            "updated_by": policy.updated_by,
            "created_at": policy.created_at.isoformat() if policy.created_at else None,
            "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
        }
    
    def _coverage_to_dict(self, coverage: Coverage) -> Dict[str, Any]:
        """Helper method to convert Coverage model to dictionary"""
        return {
            "id": coverage.id,
            "workspace_id": coverage.workspace_id,
            "policy_id": coverage.policy_id,
            "client_id": coverage.client_id,
            "coverage_type": coverage.coverage_type,
            "name": coverage.name,
            "description": coverage.description,
            "coverage_amount": float(coverage.coverage_amount) if coverage.coverage_amount is not None else None,
            "deductible": float(coverage.deductible) if coverage.deductible is not None else None,
            "coinsurance_percentage": coverage.coinsurance_percentage,
            "out_of_pocket_max": float(coverage.out_of_pocket_max) if coverage.out_of_pocket_max is not None else None,
            "annual_limit": float(coverage.annual_limit) if coverage.annual_limit is not None else None,
            "lifetime_limit": float(coverage.lifetime_limit) if coverage.lifetime_limit is not None else None,
            "exclusions": coverage.exclusions,
            "waiting_period": coverage.waiting_period,
            "elimination_period": coverage.elimination_period,
            "benefit_period": coverage.benefit_period,
            "covered_perils": coverage.covered_perils,
            "riders": coverage.riders,
            "notes": coverage.notes,
            "created_by": coverage.created_by,
            "updated_by": coverage.updated_by,
            "created_at": coverage.created_at.isoformat() if coverage.created_at else None,
            "updated_at": coverage.updated_at.isoformat() if coverage.updated_at else None
        }
    
    def _premium_to_dict(self, premium: Premium) -> Dict[str, Any]:
        """Helper method to convert Premium model to dictionary"""
        return {
            "id": premium.id,
            "workspace_id": premium.workspace_id,
            "policy_id": premium.policy_id,
            "client_id": premium.client_id,
            "premium_type": premium.premium_type,
            "amount": float(premium.amount) if premium.amount is not None else None,
            "frequency": premium.frequency,
            "due_date": premium.due_date.isoformat() if premium.due_date else None,
            "paid_date": premium.paid_date.isoformat() if premium.paid_date else None,
            "payment_method": premium.payment_method,
            "is_paid": premium.is_paid,
            "billing_period_start": premium.billing_period_start.isoformat() if premium.billing_period_start else None,
            "billing_period_end": premium.billing_period_end.isoformat() if premium.billing_period_end else None,
            "notes": premium.notes,
            "created_by": premium.created_by,
            "updated_by": premium.updated_by,
            "created_at": premium.created_at.isoformat() if premium.created_at else None,
            "updated_at": premium.updated_at.isoformat() if premium.updated_at else None
        }
# services/estate_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.estate import Estate, Will, Trust, Beneficiary
from services.service_base import BaseService
from datetime import datetime
import uuid

class EstateService(BaseService[Estate]):
    def __init__(self, db: Session):
        super().__init__(db, Estate)
    
    def get_client_estates(self, client_id: str):
        """Get all estates for a client"""
        estates = self.db.query(Estate).filter(Estate.client_id == client_id).all()
        return [self._estate_to_dict(estate) for estate in estates]
    
    def get_estate_wills(self, estate_id: str):
        """Get all wills for an estate"""
        wills = self.db.query(Will).filter(Will.estate_id == estate_id).all()
        return [self._will_to_dict(will) for will in wills]
    
    def get_estate_trusts(self, estate_id: str):
        """Get all trusts for an estate"""
        trusts = self.db.query(Trust).filter(Trust.estate_id == estate_id).all()
        return [self._trust_to_dict(trust) for trust in trusts]
    
    def get_estate_beneficiaries(self, estate_id: str):
        """Get all beneficiaries for an estate"""
        beneficiaries = self.db.query(Beneficiary).filter(Beneficiary.estate_id == estate_id).all()
        return [self._beneficiary_to_dict(beneficiary) for beneficiary in beneficiaries]
    
    def get_will_beneficiaries(self, will_id: str):
        """Get all beneficiaries for a will"""
        beneficiaries = self.db.query(Beneficiary).filter(Beneficiary.will_id == will_id).all()
        return [self._beneficiary_to_dict(beneficiary) for beneficiary in beneficiaries]
    
    def get_trust_beneficiaries(self, trust_id: str):
        """Get all beneficiaries for a trust"""
        beneficiaries = self.db.query(Beneficiary).filter(Beneficiary.trust_id == trust_id).all()
        return [self._beneficiary_to_dict(beneficiary) for beneficiary in beneficiaries]
    
    def create_estate(self, estate_data: Dict[str, Any], user_id: str = None):
        """Create a new estate"""
        if 'id' not in estate_data:
            estate_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in estate_data:
            estate_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in estate_data:
            estate_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in estate_data:
                estate_data['created_by'] = user_id
                
            if 'updated_by' not in estate_data:
                estate_data['updated_by'] = user_id
        
        estate = Estate(**estate_data)
        self.db.add(estate)
        self.db.commit()
        self.db.refresh(estate)
        
        return self._estate_to_dict(estate)
    
    def update_estate(self, estate_id: str, estate_data: Dict[str, Any], user_id: str = None):
        """Update an existing estate"""
        estate = self.db.query(Estate).filter(Estate.id == estate_id).first()
        if not estate:
            return None
            
        for key, value in estate_data.items():
            if hasattr(estate, key):
                setattr(estate, key, value)
                
        estate.updated_at = datetime.utcnow()
        
        if user_id:
            estate.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(estate)
        
        return self._estate_to_dict(estate)
    
    def delete_estate(self, estate_id: str):
        """Delete an estate and all related entities"""
        estate = self.db.query(Estate).filter(Estate.id == estate_id).first()
        if not estate:
            return False
        
        # Delete associated entities
        self.db.query(Beneficiary).filter(Beneficiary.estate_id == estate_id).delete()
        self.db.query(Will).filter(Will.estate_id == estate_id).delete()
        self.db.query(Trust).filter(Trust.estate_id == estate_id).delete()
        
        # Delete the estate itself
        self.db.delete(estate)
        self.db.commit()
        
        return True
    
    def create_will(self, will_data: Dict[str, Any], user_id: str = None):
        """Create a new will"""
        if 'id' not in will_data:
            will_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in will_data:
            will_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in will_data:
            will_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in will_data:
                will_data['created_by'] = user_id
                
            if 'updated_by' not in will_data:
                will_data['updated_by'] = user_id
        
        # If this is a new will for the estate, update the estate
        if 'estate_id' in will_data:
            estate = self.db.query(Estate).filter(Estate.id == will_data['estate_id']).first()
            if estate and not estate.has_will:
                estate.has_will = True
                self.db.commit()
        
        will = Will(**will_data)
        self.db.add(will)
        self.db.commit()
        self.db.refresh(will)
        
        return self._will_to_dict(will)
    
    def update_will(self, will_id: str, will_data: Dict[str, Any], user_id: str = None):
        """Update an existing will"""
        will = self.db.query(Will).filter(Will.id == will_id).first()
        if not will:
            return None
            
        for key, value in will_data.items():
            if hasattr(will, key):
                setattr(will, key, value)
                
        will.updated_at = datetime.utcnow()
        
        if user_id:
            will.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(will)
        
        return self._will_to_dict(will)
    
    def delete_will(self, will_id: str):
        """Delete a will and its beneficiaries"""
        will = self.db.query(Will).filter(Will.id == will_id).first()
        if not will:
            return False
        
        # Delete associated beneficiaries
        self.db.query(Beneficiary).filter(Beneficiary.will_id == will_id).delete()
        
        # Store estate_id for later
        estate_id = will.estate_id
        
        # Delete the will
        self.db.delete(will)
        self.db.commit()
        
        # Check if the estate has any remaining wills and update has_will flag if needed
        if estate_id:
            remaining_wills = self.db.query(Will).filter(Will.estate_id == estate_id).count()
            if remaining_wills == 0:
                estate = self.db.query(Estate).filter(Estate.id == estate_id).first()
                if estate:
                    estate.has_will = False
                    self.db.commit()
        
        return True
    
    def create_trust(self, trust_data: Dict[str, Any], user_id: str = None):
        """Create a new trust"""
        if 'id' not in trust_data:
            trust_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in trust_data:
            trust_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in trust_data:
            trust_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in trust_data:
                trust_data['created_by'] = user_id
                
            if 'updated_by' not in trust_data:
                trust_data['updated_by'] = user_id
        
        # If this is a new trust for the estate, update the estate
        if 'estate_id' in trust_data:
            estate = self.db.query(Estate).filter(Estate.id == trust_data['estate_id']).first()
            if estate and not estate.has_trust:
                estate.has_trust = True
                self.db.commit()
        
        trust = Trust(**trust_data)
        self.db.add(trust)
        self.db.commit()
        self.db.refresh(trust)
        
        return self._trust_to_dict(trust)
    
    def update_trust(self, trust_id: str, trust_data: Dict[str, Any], user_id: str = None):
        """Update an existing trust"""
        trust = self.db.query(Trust).filter(Trust.id == trust_id).first()
        if not trust:
            return None
            
        for key, value in trust_data.items():
            if hasattr(trust, key):
                setattr(trust, key, value)
                
        trust.updated_at = datetime.utcnow()
        
        if user_id:
            trust.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(trust)
        
        return self._trust_to_dict(trust)
    
    def delete_trust(self, trust_id: str):
        """Delete a trust and its beneficiaries"""
        trust = self.db.query(Trust).filter(Trust.id == trust_id).first()
        if not trust:
            return False
        
        # Delete associated beneficiaries
        self.db.query(Beneficiary).filter(Beneficiary.trust_id == trust_id).delete()
        
        # Store estate_id for later
        estate_id = trust.estate_id
        
        # Delete the trust
        self.db.delete(trust)
        self.db.commit()
        
        # Check if the estate has any remaining trusts and update has_trust flag if needed
        if estate_id:
            remaining_trusts = self.db.query(Trust).filter(Trust.estate_id == estate_id).count()
            if remaining_trusts == 0:
                estate = self.db.query(Estate).filter(Estate.id == estate_id).first()
                if estate:
                    estate.has_trust = False
                    self.db.commit()
        
        return True
    
    def create_beneficiary(self, beneficiary_data: Dict[str, Any], user_id: str = None):
        """Create a new beneficiary"""
        if 'id' not in beneficiary_data:
            beneficiary_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in beneficiary_data:
            beneficiary_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in beneficiary_data:
            beneficiary_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in beneficiary_data:
                beneficiary_data['created_by'] = user_id
                
            if 'updated_by' not in beneficiary_data:
                beneficiary_data['updated_by'] = user_id
        
        # If this is a new beneficiary for the estate, update the estate
        if 'estate_id' in beneficiary_data:
            estate = self.db.query(Estate).filter(Estate.id == beneficiary_data['estate_id']).first()
            if estate and not estate.has_beneficiary_designations:
                estate.has_beneficiary_designations = True
                self.db.commit()
        
        beneficiary = Beneficiary(**beneficiary_data)
        self.db.add(beneficiary)
        self.db.commit()
        self.db.refresh(beneficiary)
        
        return self._beneficiary_to_dict(beneficiary)
    
    def update_beneficiary(self, beneficiary_id: str, beneficiary_data: Dict[str, Any], user_id: str = None):
        """Update an existing beneficiary"""
        beneficiary = self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        if not beneficiary:
            return None
            
        for key, value in beneficiary_data.items():
            if hasattr(beneficiary, key):
                setattr(beneficiary, key, value)
                
        beneficiary.updated_at = datetime.utcnow()
        
        if user_id:
            beneficiary.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(beneficiary)
        
        return self._beneficiary_to_dict(beneficiary)
    
    def delete_beneficiary(self, beneficiary_id: str):
        """Delete a beneficiary"""
        beneficiary = self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        if not beneficiary:
            return False
        
        # Store estate_id for later
        estate_id = beneficiary.estate_id
        
        # Delete the beneficiary
        self.db.delete(beneficiary)
        self.db.commit()
        
        # Check if the estate has any remaining beneficiaries and update has_beneficiary_designations flag if needed
        if estate_id:
            remaining_beneficiaries = self.db.query(Beneficiary).filter(Beneficiary.estate_id == estate_id).count()
            if remaining_beneficiaries == 0:
                estate = self.db.query(Estate).filter(Estate.id == estate_id).first()
                if estate:
                    estate.has_beneficiary_designations = False
                    self.db.commit()
        
        return True
    
    def _estate_to_dict(self, estate: Estate) -> Dict[str, Any]:
        """Helper method to convert Estate model to dictionary"""
        return {
            "id": estate.id,
            "workspace_id": estate.workspace_id,
            "client_id": estate.client_id,
            "financial_plan_id": estate.financial_plan_id,
            "status": estate.status,
            "complexity": estate.complexity,
            "marital_status": estate.marital_status,
            "total_estate_value": float(estate.total_estate_value) if estate.total_estate_value else None,
            "taxable_estate": float(estate.taxable_estate) if estate.taxable_estate else None,
            "estimated_tax": float(estate.estimated_tax) if estate.estimated_tax else None,
            "tax_status": estate.tax_status,
            "asset_composition": estate.asset_composition,
            "state_of_residence": estate.state_of_residence,
            "has_will": estate.has_will,
            "has_trust": estate.has_trust,
            "has_power_of_attorney": estate.has_power_of_attorney,
            "has_healthcare_directive": estate.has_healthcare_directive,
            "has_beneficiary_designations": estate.has_beneficiary_designations,
            "last_review_date": estate.last_review_date.isoformat() if estate.last_review_date else None,
            "next_review_date": estate.next_review_date.isoformat() if estate.next_review_date else None,
            "planning_objectives": estate.planning_objectives,
            "planning_strategies": estate.planning_strategies,
            "documents": estate.documents,
            "advisors": estate.advisors,
            "notes": estate.notes,
            "created_by": estate.created_by,
            "updated_by": estate.updated_by,
            "created_at": estate.created_at.isoformat() if estate.created_at else None,
            "updated_at": estate.updated_at.isoformat() if estate.updated_at else None
        }
    
    def _will_to_dict(self, will: Will) -> Dict[str, Any]:
        """Helper method to convert Will model to dictionary"""
        return {
            "id": will.id,
            "workspace_id": will.workspace_id,
            "estate_id": will.estate_id,
            "client_id": will.client_id,
            "status": will.status,
            "type": will.type,
            "execution_date": will.execution_date.isoformat() if will.execution_date else None,
            "last_updated": will.last_updated.isoformat() if will.last_updated else None,
            "location": will.location,
            "executor": will.executor,
            "alternate_executor": will.alternate_executor,
            "guardian_for_minors": will.guardian_for_minors,
            "specific_bequests": will.specific_bequests,
            "residuary_estate": will.residuary_estate,
            "testamentary_trust": will.testamentary_trust,
            "no_contest_clause": will.no_contest_clause,
            "digital_assets": will.digital_assets,
            "pet_provisions": will.pet_provisions,
            "charitable_provisions": will.charitable_provisions,
            "special_instructions": will.special_instructions,
            "attorney": will.attorney,
            "document_id": will.document_id,
            "notes": will.notes,
            "created_by": will.created_by,
            "updated_by": will.updated_by,
            "created_at": will.created_at.isoformat() if will.created_at else None,
            "updated_at": will.updated_at.isoformat() if will.updated_at else None
        }
    
    def _trust_to_dict(self, trust: Trust) -> Dict[str, Any]:
        """Helper method to convert Trust model to dictionary"""
        return {
            "id": trust.id,
            "workspace_id": trust.workspace_id,
            "estate_id": trust.estate_id,
            "client_id": trust.client_id,
            "name": trust.name,
            "status": trust.status,
            "trust_type": trust.trust_type,
            "purpose": trust.purpose,
            "execution_date": trust.execution_date.isoformat() if trust.execution_date else None,
            "amendment_date": trust.amendment_date.isoformat() if trust.amendment_date else None,
            "location": trust.location,
            "grantor": trust.grantor,
            "co_grantor": trust.co_grantor,
            "trustee": trust.trustee,
            "successor_trustee": trust.successor_trustee,
            "is_funded": trust.is_funded,
            "trust_value": float(trust.trust_value) if trust.trust_value else None,
            "funding_source": trust.funding_source,
            "distribution_provisions": trust.distribution_provisions,
            "spendthrift_provision": trust.spendthrift_provision,
            "generation_skipping": trust.generation_skipping,
            "tax_id": trust.tax_id,
            "tax_filing_requirements": trust.tax_filing_requirements,
            "attorney": trust.attorney,
            "document_id": trust.document_id,
            "notes": trust.notes,
            "created_by": trust.created_by,
            "updated_by": trust.updated_by,
            "created_at": trust.created_at.isoformat() if trust.created_at else None,
            "updated_at": trust.updated_at.isoformat() if trust.updated_at else None
        }
    
    def _beneficiary_to_dict(self, beneficiary: Beneficiary) -> Dict[str, Any]:
        """Helper method to convert Beneficiary model to dictionary"""
        return {
            "id": beneficiary.id,
            "workspace_id": beneficiary.workspace_id,
            "estate_id": beneficiary.estate_id,
            "will_id": beneficiary.will_id,
            "trust_id": beneficiary.trust_id,
            "client_id": beneficiary.client_id,
            "name": beneficiary.name,
            "type": beneficiary.type,
            "relationship": beneficiary.relationship,
            "status": beneficiary.status,
            "primary": beneficiary.primary,
            "contingent": beneficiary.contingent,
            "percentage": float(beneficiary.percentage) if beneficiary.percentage else None,
            "priority": beneficiary.priority,
            "asset_types": beneficiary.asset_types,
            "specific_assets": beneficiary.specific_assets,
            "details": beneficiary.details,
            "conditions": beneficiary.conditions,
            "notes": beneficiary.notes,
            "created_by": beneficiary.created_by,
            "updated_by": beneficiary.updated_by,
            "created_at": beneficiary.created_at.isoformat() if beneficiary.created_at else None,
            "updated_at": beneficiary.updated_at.isoformat() if beneficiary.updated_at else None
        }
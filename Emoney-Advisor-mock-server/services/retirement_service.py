# services/retirement_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.retirement import RetirementPlan, Pension, SocialSecurity, RMD
from services.service_base import BaseService
from datetime import datetime
import uuid

class RetirementService(BaseService[RetirementPlan]):
    def __init__(self, db: Session):
        super().__init__(db, RetirementPlan)
    
    def get_client_retirement_plans(self, client_id: str):
        """Get all retirement plans for a client"""
        plans = self.db.query(RetirementPlan).filter(RetirementPlan.client_id == client_id).all()
        return [self._retirement_plan_to_dict(plan) for plan in plans]
    
    def get_retirement_pensions(self, plan_id: str):
        """Get all pensions for a retirement plan"""
        pensions = self.db.query(Pension).filter(Pension.retirement_plan_id == plan_id).all()
        return [self._pension_to_dict(pension) for pension in pensions]
    
    def get_retirement_social_security(self, plan_id: str):
        """Get all social security benefits for a retirement plan"""
        benefits = self.db.query(SocialSecurity).filter(SocialSecurity.retirement_plan_id == plan_id).all()
        return [self._social_security_to_dict(benefit) for benefit in benefits]
    
    def get_retirement_rmds(self, plan_id: str):
        """Get all RMDs for a retirement plan"""
        rmds = self.db.query(RMD).filter(RMD.retirement_plan_id == plan_id).all()
        return [self._rmd_to_dict(rmd) for rmd in rmds]
    
    # Added methods for RetirementPlan
    def create_retirement_plan(self, plan_data: Dict[str, Any], user_id: str = None):
        """Create a new retirement plan"""
        if 'id' not in plan_data:
            plan_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in plan_data:
            plan_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in plan_data:
            plan_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in plan_data:
                plan_data['created_by'] = user_id
                
            if 'updated_by' not in plan_data:
                plan_data['updated_by'] = user_id
        
        plan = RetirementPlan(**plan_data)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return self._retirement_plan_to_dict(plan)
    
    def update_retirement_plan(self, plan_id: str, plan_data: Dict[str, Any], user_id: str = None):
        """Update an existing retirement plan"""
        plan = self.db.query(RetirementPlan).filter(RetirementPlan.id == plan_id).first()
        if not plan:
            return None
            
        for key, value in plan_data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
                
        plan.updated_at = datetime.utcnow()
        
        if user_id:
            plan.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(plan)
        
        return self._retirement_plan_to_dict(plan)
    
    def delete_retirement_plan(self, plan_id: str):
        """Delete a retirement plan and all associated entities"""
        plan = self.db.query(RetirementPlan).filter(RetirementPlan.id == plan_id).first()
        if not plan:
            return False
        
        # Delete related entities
        self.db.query(Pension).filter(Pension.retirement_plan_id == plan_id).delete()
        self.db.query(SocialSecurity).filter(SocialSecurity.retirement_plan_id == plan_id).delete()
        self.db.query(RMD).filter(RMD.retirement_plan_id == plan_id).delete()
        
        self.db.delete(plan)
        self.db.commit()
        
        return True
    
    def create_pension(self, pension_data: Dict[str, Any], user_id: str = None):
        """Create a new pension"""
        if 'id' not in pension_data:
            pension_data['id'] = str(uuid.uuid4())
        
        if hasattr(Pension, 'created_at') and 'created_at' not in pension_data:
            pension_data['created_at'] = datetime.utcnow()
            
        if hasattr(Pension, 'updated_at') and 'updated_at' not in pension_data:
            pension_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(Pension, 'created_by') and 'created_by' not in pension_data:
                pension_data['created_by'] = user_id
                
            if hasattr(Pension, 'updated_by') and 'updated_by' not in pension_data:
                pension_data['updated_by'] = user_id
                
        # Calculate monthly/annual benefit if one is provided but not the other
        if 'monthly_benefit' in pension_data and 'annual_benefit' not in pension_data:
            pension_data['annual_benefit'] = pension_data['monthly_benefit'] * 12
        elif 'annual_benefit' in pension_data and 'monthly_benefit' not in pension_data:
            pension_data['monthly_benefit'] = pension_data['annual_benefit'] / 12
        
        pension = Pension(**pension_data)
        self.db.add(pension)
        self.db.commit()
        self.db.refresh(pension)
        
        return self._pension_to_dict(pension)
    
    # Added update and delete methods for Pension
    def update_pension(self, pension_id: str, pension_data: Dict[str, Any], user_id: str = None):
        """Update an existing pension"""
        pension = self.db.query(Pension).filter(Pension.id == pension_id).first()
        if not pension:
            return None
            
        for key, value in pension_data.items():
            if hasattr(pension, key):
                setattr(pension, key, value)
        
        # Update annual/monthly benefit if one is changed but not the other
        if 'monthly_benefit' in pension_data and 'annual_benefit' not in pension_data:
            pension.annual_benefit = pension.monthly_benefit * 12
        elif 'annual_benefit' in pension_data and 'monthly_benefit' not in pension_data:
            pension.monthly_benefit = pension.annual_benefit / 12
                
        pension.updated_at = datetime.utcnow()
        
        if user_id:
            pension.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(pension)
        
        return self._pension_to_dict(pension)
    
    def delete_pension(self, pension_id: str):
        """Delete a pension"""
        pension = self.db.query(Pension).filter(Pension.id == pension_id).first()
        if not pension:
            return False
        
        self.db.delete(pension)
        self.db.commit()
        
        return True
    
    def create_social_security(self, ss_data: Dict[str, Any], user_id: str = None):
        """Create a new social security benefit"""
        if 'id' not in ss_data:
            ss_data['id'] = str(uuid.uuid4())
        
        if hasattr(SocialSecurity, 'created_at') and 'created_at' not in ss_data:
            ss_data['created_at'] = datetime.utcnow()
            
        if hasattr(SocialSecurity, 'updated_at') and 'updated_at' not in ss_data:
            ss_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(SocialSecurity, 'created_by') and 'created_by' not in ss_data:
                ss_data['created_by'] = user_id
                
            if hasattr(SocialSecurity, 'updated_by') and 'updated_by' not in ss_data:
                ss_data['updated_by'] = user_id
        
        # Calculate monthly/annual benefit if one is provided but not the other
        if 'monthly_benefit' in ss_data and 'annual_benefit' not in ss_data:
            ss_data['annual_benefit'] = ss_data['monthly_benefit'] * 12
        elif 'annual_benefit' in ss_data and 'monthly_benefit' not in ss_data:
            ss_data['monthly_benefit'] = ss_data['annual_benefit'] / 12
            
        ss = SocialSecurity(**ss_data)
        self.db.add(ss)
        self.db.commit()
        self.db.refresh(ss)
        
        return self._social_security_to_dict(ss)
    
    # Added update and delete methods for SocialSecurity
    def update_social_security(self, ss_id: str, ss_data: Dict[str, Any], user_id: str = None):
        """Update an existing social security benefit"""
        ss = self.db.query(SocialSecurity).filter(SocialSecurity.id == ss_id).first()
        if not ss:
            return None
            
        for key, value in ss_data.items():
            if hasattr(ss, key):
                setattr(ss, key, value)
        
        # Update annual/monthly benefit if one is changed but not the other
        if 'monthly_benefit' in ss_data and 'annual_benefit' not in ss_data:
            ss.annual_benefit = ss.monthly_benefit * 12
        elif 'annual_benefit' in ss_data and 'monthly_benefit' not in ss_data:
            ss.monthly_benefit = ss.annual_benefit / 12
                
        ss.updated_at = datetime.utcnow()
        
        if user_id:
            ss.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(ss)
        
        return self._social_security_to_dict(ss)
    
    def delete_social_security(self, ss_id: str):
        """Delete a social security benefit"""
        ss = self.db.query(SocialSecurity).filter(SocialSecurity.id == ss_id).first()
        if not ss:
            return False
        
        self.db.delete(ss)
        self.db.commit()
        
        return True
    
    def create_rmd(self, rmd_data: Dict[str, Any], user_id: str = None):
        """Create a new RMD"""
        if 'id' not in rmd_data:
            rmd_data['id'] = str(uuid.uuid4())
        
        if hasattr(RMD, 'created_at') and 'created_at' not in rmd_data:
            rmd_data['created_at'] = datetime.utcnow()
            
        if hasattr(RMD, 'updated_at') and 'updated_at' not in rmd_data:
            rmd_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(RMD, 'created_by') and 'created_by' not in rmd_data:
                rmd_data['created_by'] = user_id
                
            if hasattr(RMD, 'updated_by') and 'updated_by' not in rmd_data:
                rmd_data['updated_by'] = user_id
        
        rmd = RMD(**rmd_data)
        self.db.add(rmd)
        self.db.commit()
        self.db.refresh(rmd)
        
        return self._rmd_to_dict(rmd)
    
    # Added update and delete methods for RMD
    def update_rmd(self, rmd_id: str, rmd_data: Dict[str, Any], user_id: str = None):
        """Update an existing RMD"""
        rmd = self.db.query(RMD).filter(RMD.id == rmd_id).first()
        if not rmd:
            return None
            
        for key, value in rmd_data.items():
            if hasattr(rmd, key):
                setattr(rmd, key, value)
                
        rmd.updated_at = datetime.utcnow()
        
        if user_id:
            rmd.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(rmd)
        
        return self._rmd_to_dict(rmd)
    
    def delete_rmd(self, rmd_id: str):
        """Delete an RMD"""
        rmd = self.db.query(RMD).filter(RMD.id == rmd_id).first()
        if not rmd:
            return False
        
        self.db.delete(rmd)
        self.db.commit()
        
        return True
    
    # Helper methods to convert entities to dictionaries
    def _retirement_plan_to_dict(self, plan: RetirementPlan) -> Dict[str, Any]:
        """Helper method to convert RetirementPlan model to dictionary"""
        return {
            "id": plan.id,
            "workspace_id": plan.workspace_id,
            "client_id": plan.client_id,
            "financial_plan_id": plan.financial_plan_id,
            "status": plan.status,
            "current_age": plan.current_age,
            "spouse_age": plan.spouse_age,
            "retirement_age": plan.retirement_age,
            "spouse_retirement_age": plan.spouse_retirement_age,
            "life_expectancy": plan.life_expectancy,
            "spouse_life_expectancy": plan.spouse_life_expectancy,
            "retirement_assets": float(plan.retirement_assets) if plan.retirement_assets else None,
            "annual_contributions": float(plan.annual_contributions) if plan.annual_contributions else None,
            "contribution_increase_rate": float(plan.contribution_increase_rate) if plan.contribution_increase_rate else None,
            "pre_retirement_return": float(plan.pre_retirement_return) if plan.pre_retirement_return else None,
            "post_retirement_return": float(plan.post_retirement_return) if plan.post_retirement_return else None,
            "inflation_rate": float(plan.inflation_rate) if plan.inflation_rate else None,
            "target_income": float(plan.target_income) if plan.target_income else None,
            "income_replacement_ratio": float(plan.income_replacement_ratio) if plan.income_replacement_ratio else None,
            "success_probability": plan.success_probability,
            "income_sources": plan.income_sources,
            "retirement_accounts": plan.retirement_accounts,
            "retirement_shortfall": float(plan.retirement_shortfall) if plan.retirement_shortfall else None,
            "years_to_retirement": plan.years_to_retirement,
            "required_savings_rate": float(plan.required_savings_rate) if plan.required_savings_rate else None,
            "risk_capacity": plan.risk_capacity,
            "strategies": plan.strategies,
            "notes": plan.notes,
            "created_by": plan.created_by,
            "updated_by": plan.updated_by,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }
    
    def _pension_to_dict(self, pension: Pension) -> Dict[str, Any]:
        """Helper method to convert Pension model to dictionary"""
        return {
            "id": pension.id,
            "workspace_id": pension.workspace_id,
            "client_id": pension.client_id,
            "retirement_plan_id": pension.retirement_plan_id,
            "name": pension.name,
            "status": pension.status,
            "type": pension.type,
            "recipient": pension.recipient,
            "provider": pension.provider,
            "monthly_benefit": float(pension.monthly_benefit) if pension.monthly_benefit else None,
            "annual_benefit": float(pension.annual_benefit) if pension.annual_benefit else None,
            "start_age": pension.start_age,
            "benefit_period": pension.benefit_period,
            "cola_adjustment": pension.cola_adjustment,
            "cola_rate": float(pension.cola_rate) if pension.cola_rate else None,
            "payment_frequency": pension.payment_frequency,
            "survivor_benefit_percentage": pension.survivor_benefit_percentage,
            "lump_sum_option": pension.lump_sum_option,
            "lump_sum_amount": float(pension.lump_sum_amount) if pension.lump_sum_amount else None,
            "early_retirement_option": pension.early_retirement_option,
            "early_retirement_age": pension.early_retirement_age,
            "early_retirement_reduction": float(pension.early_retirement_reduction) if pension.early_retirement_reduction else None,
            "vesting_percentage": pension.vesting_percentage,
            "years_of_service": pension.years_of_service,
            "pension_max": float(pension.pension_max) if pension.pension_max else None,
            "notes": pension.notes,
            "created_by": pension.created_by,
            "updated_by": pension.updated_by,
            "created_at": pension.created_at.isoformat() if pension.created_at else None,
            "updated_at": pension.updated_at.isoformat() if pension.updated_at else None
        }
    
    def _social_security_to_dict(self, ss: SocialSecurity) -> Dict[str, Any]:
        """Helper method to convert SocialSecurity model to dictionary"""
        return {
            "id": ss.id,
            "workspace_id": ss.workspace_id,
            "client_id": ss.client_id,
            "retirement_plan_id": ss.retirement_plan_id,
            "recipient": ss.recipient,
            "status": ss.status,
            "current_age": ss.current_age,
            "pia": float(ss.pia) if ss.pia else None,
            "early_retirement_age": ss.early_retirement_age,
            "full_retirement_age": ss.full_retirement_age,
            "maximum_retirement_age": ss.maximum_retirement_age,
            "claim_age": ss.claim_age,
            "monthly_benefit_at_er": float(ss.monthly_benefit_at_er) if ss.monthly_benefit_at_er else None,
            "monthly_benefit_at_fra": float(ss.monthly_benefit_at_fra) if ss.monthly_benefit_at_fra else None,
            "monthly_benefit_at_max": float(ss.monthly_benefit_at_max) if ss.monthly_benefit_at_max else None,
            "monthly_benefit": float(ss.monthly_benefit) if ss.monthly_benefit else None,
            "annual_benefit": float(ss.annual_benefit) if ss.annual_benefit else None,
            "lifetime_benefit": float(ss.lifetime_benefit) if ss.lifetime_benefit else None,
            "cola_assumption": float(ss.cola_assumption) if ss.cola_assumption else None,
            "earnings_test_applicable": ss.earnings_test_applicable,
            "earnings_test_income": float(ss.earnings_test_income) if ss.earnings_test_income else None,
            "taxable_percentage": ss.taxable_percentage,
            "spousal_benefit_eligible": ss.spousal_benefit_eligible,
            "spousal_benefit_amount": float(ss.spousal_benefit_amount) if ss.spousal_benefit_amount else None,
            "survivor_benefit_eligible": ss.survivor_benefit_eligible,
            "survivor_benefit_amount": float(ss.survivor_benefit_amount) if ss.survivor_benefit_amount else None,
            "optimization_strategy": ss.optimization_strategy,
            "notes": ss.notes,
            "created_by": ss.created_by,
            "updated_by": ss.updated_by,
            "created_at": ss.created_at.isoformat() if ss.created_at else None,
            "updated_at": ss.updated_at.isoformat() if ss.updated_at else None
        }
    
    def _rmd_to_dict(self, rmd: RMD) -> Dict[str, Any]:
        """Helper method to convert RMD model to dictionary"""
        return {
            "id": rmd.id,
            "workspace_id": rmd.workspace_id,
            "client_id": rmd.client_id,
            "retirement_plan_id": rmd.retirement_plan_id,
            "status": rmd.status,
            "current_age": rmd.current_age,
            "rmd_start_age": rmd.rmd_start_age,
            "total_ira_balance": float(rmd.total_ira_balance) if rmd.total_ira_balance else None,
            "current_rmd": float(rmd.current_rmd) if rmd.current_rmd else None,
            "rmd_accounts": rmd.rmd_accounts,
            "rmd_projection": rmd.rmd_projection,
            "distribution_strategy": rmd.distribution_strategy,
            "tax_impact": rmd.tax_impact,
            "compliance_status": rmd.compliance_status,
            "previous_distributions": rmd.previous_distributions,
            "notes": rmd.notes,
            "created_by": rmd.created_by,
            "updated_by": rmd.updated_by,
            "created_at": rmd.created_at.isoformat() if rmd.created_at else None,
            "updated_at": rmd.updated_at.isoformat() if rmd.updated_at else None
        }
# services/tax_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.tax import Tax, TaxDocument, TaxPayment, TaxDeduction, TaxPlan, TaxBracket, Deduction, Credit
from services.service_base import BaseService
from datetime import datetime
import uuid

class TaxService(BaseService[Tax]):
    def __init__(self, db: Session):
        super().__init__(db, Tax)
    
    # ==================== Tax Methods ====================
    
    def get_client_taxes(self, client_id: str):
        """Get all tax records for a client"""
        taxes = self.db.query(Tax).filter(Tax.client_id == client_id).all()
        return [self._tax_to_dict(tax) for tax in taxes]
    
    def get_tax_by_year(self, client_id: str, tax_year: int):
        """Get tax record for a client by year"""
        tax = self.db.query(Tax).filter(Tax.client_id == client_id, Tax.tax_year == tax_year).first()
        if not tax:
            return None
        return self._tax_to_dict(tax)
    
    def create_tax(self, tax_data: Dict[str, Any], user_id: str = None):
        """Create a new tax record"""
        if 'id' not in tax_data:
            tax_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in tax_data:
            tax_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in tax_data:
            tax_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in tax_data:
                tax_data['created_by'] = user_id
                
            if 'updated_by' not in tax_data:
                tax_data['updated_by'] = user_id
        
        # Check if a tax record already exists for this client and year
        if 'client_id' in tax_data and 'tax_year' in tax_data:
            existing_tax = self.db.query(Tax).filter(
                Tax.client_id == tax_data['client_id'],
                Tax.tax_year == tax_data['tax_year']
            ).first()
            
            if existing_tax:
                return self.update_tax(existing_tax.id, tax_data, user_id)
        
        tax = Tax(**tax_data)
        self.db.add(tax)
        self.db.commit()
        self.db.refresh(tax)
        
        return self._tax_to_dict(tax)
    
    def update_tax(self, tax_id: str, tax_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax record"""
        tax = self.db.query(Tax).filter(Tax.id == tax_id).first()
        if not tax:
            return None
            
        for key, value in tax_data.items():
            if hasattr(tax, key):
                setattr(tax, key, value)
                
        tax.updated_at = datetime.utcnow()
        
        if user_id:
            tax.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(tax)
        
        return self._tax_to_dict(tax)
    
    def delete_tax(self, tax_id: str):
        """Delete a tax record and all related entities"""
        tax = self.db.query(Tax).filter(Tax.id == tax_id).first()
        if not tax:
            return False
        
        # Delete related entities
        self.db.query(TaxDocument).filter(TaxDocument.tax_id == tax_id).delete()
        self.db.query(TaxPayment).filter(TaxPayment.tax_id == tax_id).delete()
        self.db.query(TaxDeduction).filter(TaxDeduction.tax_id == tax_id).delete()
        
        # Delete the tax record itself
        self.db.delete(tax)
        self.db.commit()
        
        return True
    
    # ==================== Tax Document Methods ====================
    
    def get_tax_documents(self, tax_id: str):
        """Get all documents for a tax record"""
        documents = self.db.query(TaxDocument).filter(TaxDocument.tax_id == tax_id).all()
        return [self._tax_document_to_dict(document) for document in documents]
    
    def get_document_by_id(self, document_id: str):
        """Get a specific tax document by ID"""
        document = self.db.query(TaxDocument).filter(TaxDocument.id == document_id).first()
        if not document:
            return None
        return self._tax_document_to_dict(document)
    
    def create_tax_document(self, document_data: Dict[str, Any], user_id: str = None):
        """Create a new tax document"""
        if 'id' not in document_data:
            document_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in document_data:
            document_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in document_data:
            document_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in document_data:
                document_data['created_by'] = user_id
                
            if 'updated_by' not in document_data:
                document_data['updated_by'] = user_id
        
        document = TaxDocument(**document_data)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return self._tax_document_to_dict(document)
    
    def update_tax_document(self, document_id: str, document_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax document"""
        document = self.db.query(TaxDocument).filter(TaxDocument.id == document_id).first()
        if not document:
            return None
            
        for key, value in document_data.items():
            if hasattr(document, key):
                setattr(document, key, value)
                
        document.updated_at = datetime.utcnow()
        
        if user_id:
            document.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(document)
        
        return self._tax_document_to_dict(document)
    
    def delete_tax_document(self, document_id: str):
        """Delete a tax document"""
        document = self.db.query(TaxDocument).filter(TaxDocument.id == document_id).first()
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    # ==================== Tax Payment Methods ====================
    
    def get_tax_payments(self, tax_id: str):
        """Get all payments for a tax record"""
        payments = self.db.query(TaxPayment).filter(TaxPayment.tax_id == tax_id).all()
        return [self._tax_payment_to_dict(payment) for payment in payments]
    
    def get_payment_by_id(self, payment_id: str):
        """Get a specific tax payment by ID"""
        payment = self.db.query(TaxPayment).filter(TaxPayment.id == payment_id).first()
        if not payment:
            return None
        return self._tax_payment_to_dict(payment)
    
    def create_tax_payment(self, payment_data: Dict[str, Any], user_id: str = None):
        """Create a new tax payment"""
        if 'id' not in payment_data:
            payment_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in payment_data:
            payment_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in payment_data:
            payment_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in payment_data:
                payment_data['created_by'] = user_id
                
            if 'updated_by' not in payment_data:
                payment_data['updated_by'] = user_id
        
        payment = TaxPayment(**payment_data)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        # Update total payments in parent tax record
        if 'tax_id' in payment_data:
            self._update_tax_payments_total(payment_data['tax_id'])
        
        return self._tax_payment_to_dict(payment)
    
    def update_tax_payment(self, payment_id: str, payment_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax payment"""
        payment = self.db.query(TaxPayment).filter(TaxPayment.id == payment_id).first()
        if not payment:
            return None
            
        for key, value in payment_data.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
                
        payment.updated_at = datetime.utcnow()
        
        if user_id:
            payment.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(payment)
        
        # Update total payments in parent tax record
        self._update_tax_payments_total(payment.tax_id)
        
        return self._tax_payment_to_dict(payment)
    
    def delete_tax_payment(self, payment_id: str):
        """Delete a tax payment"""
        payment = self.db.query(TaxPayment).filter(TaxPayment.id == payment_id).first()
        if not payment:
            return False
        
        # Store tax_id for updating totals after deletion
        tax_id = payment.tax_id
        
        self.db.delete(payment)
        self.db.commit()
        
        # Update total payments in parent tax record
        self._update_tax_payments_total(tax_id)
        
        return True
    
    # ==================== Tax Deduction Methods ====================
    
    def get_tax_deductions(self, tax_id: str):
        """Get all deductions for a tax record"""
        deductions = self.db.query(TaxDeduction).filter(TaxDeduction.tax_id == tax_id).all()
        return [self._tax_deduction_to_dict(deduction) for deduction in deductions]
    
    def get_tax_deduction_by_id(self, deduction_id: str):
        """Get a specific tax deduction by ID"""
        deduction = self.db.query(TaxDeduction).filter(TaxDeduction.id == deduction_id).first()
        if not deduction:
            return None
        return self._tax_deduction_to_dict(deduction)
    
    def create_tax_deduction(self, deduction_data: Dict[str, Any], user_id: str = None):
        """Create a new tax deduction"""
        if 'id' not in deduction_data:
            deduction_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in deduction_data:
            deduction_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in deduction_data:
            deduction_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in deduction_data:
                deduction_data['created_by'] = user_id
                
            if 'updated_by' not in deduction_data:
                deduction_data['updated_by'] = user_id
        
        deduction = TaxDeduction(**deduction_data)
        self.db.add(deduction)
        self.db.commit()
        self.db.refresh(deduction)
        
        # Update deductions summary in parent tax record
        if 'tax_id' in deduction_data:
            self._update_tax_deductions_summary(deduction_data['tax_id'])
        
        return self._tax_deduction_to_dict(deduction)
    
    def update_tax_deduction(self, deduction_id: str, deduction_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax deduction"""
        deduction = self.db.query(TaxDeduction).filter(TaxDeduction.id == deduction_id).first()
        if not deduction:
            return None
            
        for key, value in deduction_data.items():
            if hasattr(deduction, key):
                setattr(deduction, key, value)
                
        deduction.updated_at = datetime.utcnow()
        
        if user_id:
            deduction.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(deduction)
        
        # Update deductions summary in parent tax record
        self._update_tax_deductions_summary(deduction.tax_id)
        
        return self._tax_deduction_to_dict(deduction)
    
    def delete_tax_deduction(self, deduction_id: str):
        """Delete a tax deduction"""
        deduction = self.db.query(TaxDeduction).filter(TaxDeduction.id == deduction_id).first()
        if not deduction:
            return False
        
        # Store tax_id for updating deductions summary after deletion
        tax_id = deduction.tax_id
        
        self.db.delete(deduction)
        self.db.commit()
        
        # Update deductions summary in parent tax record
        self._update_tax_deductions_summary(tax_id)
        
        return True
    
    # ==================== Tax Plan Methods ====================
    
    def get_client_tax_plans(self, client_id: str):
        """Get all tax plans for a client"""
        tax_plans = self.db.query(TaxPlan).filter(TaxPlan.client_id == client_id).all()
        return [self._tax_plan_to_dict(plan) for plan in tax_plans]
    
    def get_tax_plan_by_id(self, plan_id: str):
        """Get a specific tax plan by ID"""
        plan = self.db.query(TaxPlan).filter(TaxPlan.id == plan_id).first()
        if not plan:
            return None
        return self._tax_plan_to_dict(plan)
    
    def get_tax_plan_by_year(self, client_id: str, tax_year: int):
        """Get tax plan for a client by year"""
        plan = self.db.query(TaxPlan).filter(
            TaxPlan.client_id == client_id,
            TaxPlan.tax_year == tax_year
        ).first()
        if not plan:
            return None
        return self._tax_plan_to_dict(plan)
    
    def create_tax_plan(self, plan_data: Dict[str, Any], user_id: str = None):
        """Create a new tax plan"""
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
        
        plan = TaxPlan(**plan_data)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return self._tax_plan_to_dict(plan)
    
    def update_tax_plan(self, plan_id: str, plan_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax plan"""
        plan = self.db.query(TaxPlan).filter(TaxPlan.id == plan_id).first()
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
        
        return self._tax_plan_to_dict(plan)
    
    def delete_tax_plan(self, plan_id: str):
        """Delete a tax plan and all related entities"""
        plan = self.db.query(TaxPlan).filter(TaxPlan.id == plan_id).first()
        if not plan:
            return False
        
        # Delete related entities
        self.db.query(TaxBracket).filter(TaxBracket.tax_plan_id == plan_id).delete()
        self.db.query(Deduction).filter(Deduction.tax_plan_id == plan_id).delete()
        self.db.query(Credit).filter(Credit.tax_plan_id == plan_id).delete()
        
        # Delete the plan itself
        self.db.delete(plan)
        self.db.commit()
        
        return True
    
    # ==================== Tax Bracket Methods ====================
    
    def get_tax_plan_brackets(self, tax_plan_id: str):
        """Get all tax brackets for a tax plan"""
        brackets = self.db.query(TaxBracket).filter(TaxBracket.tax_plan_id == tax_plan_id).all()
        return [self._tax_bracket_to_dict(bracket) for bracket in brackets]
    
    def get_tax_bracket_by_id(self, bracket_id: str):
        """Get a specific tax bracket by ID"""
        bracket = self.db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
        if not bracket:
            return None
        return self._tax_bracket_to_dict(bracket)
    
    def create_tax_bracket(self, bracket_data: Dict[str, Any], user_id: str = None):
        """Create a new tax bracket"""
        if 'id' not in bracket_data:
            bracket_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in bracket_data:
            bracket_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in bracket_data:
            bracket_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in bracket_data:
                bracket_data['created_by'] = user_id
                
            if 'updated_by' not in bracket_data:
                bracket_data['updated_by'] = user_id
        
        bracket = TaxBracket(**bracket_data)
        self.db.add(bracket)
        self.db.commit()
        self.db.refresh(bracket)
        
        return self._tax_bracket_to_dict(bracket)
    
    def update_tax_bracket(self, bracket_id: str, bracket_data: Dict[str, Any], user_id: str = None):
        """Update an existing tax bracket"""
        bracket = self.db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
        if not bracket:
            return None
            
        for key, value in bracket_data.items():
            if hasattr(bracket, key):
                setattr(bracket, key, value)
                
        bracket.updated_at = datetime.utcnow()
        
        if user_id:
            bracket.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(bracket)
        
        return self._tax_bracket_to_dict(bracket)
    
    def delete_tax_bracket(self, bracket_id: str):
        """Delete a tax bracket"""
        bracket = self.db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
        if not bracket:
            return False
        
        self.db.delete(bracket)
        self.db.commit()
        
        return True
    
    # ==================== Deduction Methods (Planning) ====================
    
    def get_tax_plan_deductions(self, tax_plan_id: str):
        """Get all deductions for a tax plan"""
        deductions = self.db.query(Deduction).filter(Deduction.tax_plan_id == tax_plan_id).all()
        return [self._deduction_to_dict(deduction) for deduction in deductions]
    
    def get_client_deductions(self, client_id: str):
        """Get all deductions for a client"""
        deductions = self.db.query(Deduction).filter(Deduction.client_id == client_id).all()
        return [self._deduction_to_dict(deduction) for deduction in deductions]
    
    def get_deduction_by_id(self, deduction_id: str):
        """Get a specific deduction by ID"""
        deduction = self.db.query(Deduction).filter(Deduction.id == deduction_id).first()
        if not deduction:
            return None
        return self._deduction_to_dict(deduction)
    
    def create_deduction(self, deduction_data: Dict[str, Any], user_id: str = None):
        """Create a new deduction"""
        if 'id' not in deduction_data:
            deduction_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in deduction_data:
            deduction_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in deduction_data:
            deduction_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in deduction_data:
                deduction_data['created_by'] = user_id
                
            if 'updated_by' not in deduction_data:
                deduction_data['updated_by'] = user_id
        
        deduction = Deduction(**deduction_data)
        self.db.add(deduction)
        self.db.commit()
        self.db.refresh(deduction)
        
        # Update tax plan totals if tax_plan_id is provided
        if 'tax_plan_id' in deduction_data:
            self._update_tax_plan_projections(deduction_data['tax_plan_id'])
        
        return self._deduction_to_dict(deduction)
    
    def update_deduction(self, deduction_id: str, deduction_data: Dict[str, Any], user_id: str = None):
        """Update an existing deduction"""
        deduction = self.db.query(Deduction).filter(Deduction.id == deduction_id).first()
        if not deduction:
            return None
            
        tax_plan_id = deduction.tax_plan_id
            
        for key, value in deduction_data.items():
            if hasattr(deduction, key):
                setattr(deduction, key, value)
                
        deduction.updated_at = datetime.utcnow()
        
        if user_id:
            deduction.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(deduction)
        
        # Update tax plan totals
        if tax_plan_id:
            self._update_tax_plan_projections(tax_plan_id)
        
        return self._deduction_to_dict(deduction)
    
    def delete_deduction(self, deduction_id: str):
        """Delete a deduction"""
        deduction = self.db.query(Deduction).filter(Deduction.id == deduction_id).first()
        if not deduction:
            return False
        
        tax_plan_id = deduction.tax_plan_id
        
        self.db.delete(deduction)
        self.db.commit()
        
        # Update tax plan totals
        if tax_plan_id:
            self._update_tax_plan_projections(tax_plan_id)
        
        return True
    
    # ==================== Credit Methods ====================
    
    def get_tax_plan_credits(self, tax_plan_id: str):
        """Get all credits for a tax plan"""
        credits = self.db.query(Credit).filter(Credit.tax_plan_id == tax_plan_id).all()
        return [self._credit_to_dict(credit) for credit in credits]
    
    def get_client_credits(self, client_id: str):
        """Get all credits for a client"""
        credits = self.db.query(Credit).filter(Credit.client_id == client_id).all()
        return [self._credit_to_dict(credit) for credit in credits]
    
    def get_credit_by_id(self, credit_id: str):
        """Get a specific credit by ID"""
        credit = self.db.query(Credit).filter(Credit.id == credit_id).first()
        if not credit:
            return None
        return self._credit_to_dict(credit)
    
    def create_credit(self, credit_data: Dict[str, Any], user_id: str = None):
        """Create a new credit"""
        if 'id' not in credit_data:
            credit_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in credit_data:
            credit_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in credit_data:
            credit_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in credit_data:
                credit_data['created_by'] = user_id
                
            if 'updated_by' not in credit_data:
                credit_data['updated_by'] = user_id
        
        credit = Credit(**credit_data)
        self.db.add(credit)
        self.db.commit()
        self.db.refresh(credit)
        
        # Update tax plan totals if tax_plan_id is provided
        if 'tax_plan_id' in credit_data:
            self._update_tax_plan_projections(credit_data['tax_plan_id'])
        
        return self._credit_to_dict(credit)
    
    def update_credit(self, credit_id: str, credit_data: Dict[str, Any], user_id: str = None):
        """Update an existing credit"""
        credit = self.db.query(Credit).filter(Credit.id == credit_id).first()
        if not credit:
            return None
            
        tax_plan_id = credit.tax_plan_id
            
        for key, value in credit_data.items():
            if hasattr(credit, key):
                setattr(credit, key, value)
                
        credit.updated_at = datetime.utcnow()
        
        if user_id:
            credit.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(credit)
        
        # Update tax plan totals
        if tax_plan_id:
            self._update_tax_plan_projections(tax_plan_id)
        
        return self._credit_to_dict(credit)
    
    def delete_credit(self, credit_id: str):
        """Delete a credit"""
        credit = self.db.query(Credit).filter(Credit.id == credit_id).first()
        if not credit:
            return False
        
        tax_plan_id = credit.tax_plan_id
        
        self.db.delete(credit)
        self.db.commit()
        
        # Update tax plan totals
        if tax_plan_id:
            self._update_tax_plan_projections(tax_plan_id)
        
        return True
    
    # ==================== Helper Methods ====================
    
    def _update_tax_payments_total(self, tax_id: str):
        """Update the payments JSON in the tax record"""
        tax = self.db.query(Tax).filter(Tax.id == tax_id).first()
        if not tax:
            return
        
        # Get all payments for this tax record
        payments = self.db.query(TaxPayment).filter(TaxPayment.tax_id == tax_id).all()
        
        # Group payments by type
        payment_summary = {}
        total_payments = 0
        
        for payment in payments:
            payment_type = payment.payment_type
            amount = float(payment.amount) if payment.amount is not None else 0
            
            if payment_type not in payment_summary:
                payment_summary[payment_type] = 0
                
            payment_summary[payment_type] += amount
            total_payments += amount
        
        # Add total to summary
        deduction_summary['total'] = total_deductions
        
        # Update the tax record
        tax.deductions = deduction_summary
        
        # Recalculate taxable income if we have AGI
        if tax.adjusted_gross_income is not None:
            tax.taxable_income = max(0, float(tax.adjusted_gross_income) - total_deductions)
            
        self.db.commit()
    
    def _update_tax_plan_projections(self, tax_plan_id: str):
        """Update projected totals in tax plan"""
        plan = self.db.query(TaxPlan).filter(TaxPlan.id == tax_plan_id).first()
        if not plan:
            return
        
        # Get all deductions for this plan
        deductions = self.db.query(Deduction).filter(Deduction.tax_plan_id == tax_plan_id).all()
        total_deductions = sum([float(d.amount or 0) for d in deductions])
        
        # Get all credits for this plan
        credits = self.db.query(Credit).filter(Credit.tax_plan_id == tax_plan_id).all()
        total_credits = sum([float(c.amount or 0) for c in credits])
        
        # Update plan
        plan.projected_deductions = total_deductions
        plan.projected_credits = total_credits
        
        # Recalculate estimated tax liability if we have projected income
        if plan.projected_income is not None:
            taxable_income = max(0, float(plan.projected_income) - total_deductions)
            # This is a simplified calculation - in reality would use brackets
            estimated_tax = taxable_income * 0.22  # Placeholder rate
            plan.estimated_tax_liability = max(0, estimated_tax - total_credits)
            
            # Calculate effective tax rate
            if float(plan.projected_income) > 0:
                plan.effective_tax_rate = (float(plan.estimated_tax_liability) / float(plan.projected_income)) * 100
        
        plan.updated_at = datetime.utcnow()
        self.db.commit()
    
    # ==================== Dictionary Conversion Methods ====================
    
    def _tax_to_dict(self, tax: Tax) -> Dict[str, Any]:
        """Helper method to convert Tax model to dictionary"""
        return {
            "id": tax.id,
            "client_id": tax.client_id,
            "tax_year": tax.tax_year,
            "filing_status": tax.filing_status,
            "adjusted_gross_income": float(tax.adjusted_gross_income) if tax.adjusted_gross_income else None,
            "taxable_income": float(tax.taxable_income) if tax.taxable_income else None,
            "federal_tax": float(tax.federal_tax) if tax.federal_tax else None,
            "state_tax": float(tax.state_tax) if tax.state_tax else None,
            "state": tax.state,
            "deductions": tax.deductions,
            "credits": tax.credits,
            "payments": tax.payments,
            "refund_amount": float(tax.refund_amount) if tax.refund_amount else None,
            "amount_owed": float(tax.amount_owed) if tax.amount_owed else None,
            "filing_date": tax.filing_date.isoformat() if tax.filing_date else None,
            "notes": tax.notes,
            "created_by": tax.created_by,
            "updated_by": tax.updated_by,
            "created_at": tax.created_at.isoformat() if tax.created_at else None,
            "updated_at": tax.updated_at.isoformat() if tax.updated_at else None
        }
    
    def _tax_document_to_dict(self, document: TaxDocument) -> Dict[str, Any]:
        """Helper method to convert TaxDocument model to dictionary"""
        return {
            "id": document.id,
            "tax_id": document.tax_id,
            "document_id": document.document_id,
            "type": document.type,
            "name": document.name,
            "description": document.description,
            "tax_year": document.tax_year,
            "form_number": document.form_number,
            "issuer": document.issuer,
            "recipient": document.recipient,
            "issue_date": document.issue_date.isoformat() if document.issue_date else None,
            "created_by": document.created_by,
            "updated_by": document.updated_by,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
    
    def _tax_payment_to_dict(self, payment: TaxPayment) -> Dict[str, Any]:
        """Helper method to convert TaxPayment model to dictionary"""
        return {
            "id": payment.id,
            "tax_id": payment.tax_id,
            "payment_type": payment.payment_type,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "amount": float(payment.amount) if payment.amount else None,
            "reference_number": payment.reference_number,
            "description": payment.description,
            "created_by": payment.created_by,
            "updated_by": payment.updated_by,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
        }
    
    def _tax_deduction_to_dict(self, deduction: TaxDeduction) -> Dict[str, Any]:
        """Helper method to convert TaxDeduction model to dictionary"""
        return {
            "id": deduction.id,
            "tax_id": deduction.tax_id,
            "deduction_type": deduction.deduction_type,
            "category": deduction.category,
            "description": deduction.description,
            "amount": float(deduction.amount) if deduction.amount else None,
            "created_by": deduction.created_by,
            "updated_by": deduction.updated_by,
            "created_at": deduction.created_at.isoformat() if deduction.created_at else None,
            "updated_at": deduction.updated_at.isoformat() if deduction.updated_at else None
        }
    
    def _tax_plan_to_dict(self, plan: TaxPlan) -> Dict[str, Any]:
        """Helper method to convert TaxPlan model to dictionary"""
        return {
            "id": plan.id,
            "workspace_id": plan.workspace_id,
            "client_id": plan.client_id,
            "plan_id": plan.plan_id,
            "name": plan.name,
            "description": plan.description,
            "tax_year": plan.tax_year,
            "filing_status": plan.filing_status,
            "projected_income": float(plan.projected_income) if plan.projected_income is not None else None,
            "projected_deductions": float(plan.projected_deductions) if plan.projected_deductions is not None else None,
            "projected_credits": float(plan.projected_credits) if plan.projected_credits is not None else None,
            "estimated_tax_liability": float(plan.estimated_tax_liability) if plan.estimated_tax_liability is not None else None,
            "effective_tax_rate": float(plan.effective_tax_rate) if plan.effective_tax_rate is not None else None,
            "marginal_tax_rate": float(plan.marginal_tax_rate) if plan.marginal_tax_rate is not None else None,
            "strategy_notes": plan.strategy_notes,
            "optimization_opportunities": plan.optimization_opportunities,
            "risk_factors": plan.risk_factors,
            "assumptions": plan.assumptions,
            "status": plan.status,
            "created_by": plan.created_by,
            "updated_by": plan.updated_by,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }
    
    def _tax_bracket_to_dict(self, bracket: TaxBracket) -> Dict[str, Any]:
        """Helper method to convert TaxBracket model to dictionary"""
        return {
            "id": bracket.id,
            "workspace_id": bracket.workspace_id,
            "tax_plan_id": bracket.tax_plan_id,
            "client_id": bracket.client_id,
            "bracket_type": bracket.bracket_type,
            "tax_year": bracket.tax_year,
            "filing_status": bracket.filing_status,
            "income_min": float(bracket.income_min) if bracket.income_min is not None else None,
            "income_max": float(bracket.income_max) if bracket.income_max is not None else None,
            "rate": float(bracket.rate) if bracket.rate is not None else None,
            "base_tax": float(bracket.base_tax) if bracket.base_tax is not None else None,
            "taxable_income_in_bracket": float(bracket.taxable_income_in_bracket) if bracket.taxable_income_in_bracket is not None else None,
            "tax_in_bracket": float(bracket.tax_in_bracket) if bracket.tax_in_bracket is not None else None,
            "state": bracket.state,
            "notes": bracket.notes,
            "created_by": bracket.created_by,
            "updated_by": bracket.updated_by,
            "created_at": bracket.created_at.isoformat() if bracket.created_at else None,
            "updated_at": bracket.updated_at.isoformat() if bracket.updated_at else None
        }
    
    def _deduction_to_dict(self, deduction: Deduction) -> Dict[str, Any]:
        """Helper method to convert Deduction model to dictionary"""
        return {
            "id": deduction.id,
            "workspace_id": deduction.workspace_id,
            "tax_plan_id": deduction.tax_plan_id,
            "client_id": deduction.client_id,
            "name": deduction.name,
            "description": deduction.description,
            "deduction_type": deduction.deduction_type,
            "category": deduction.category,
            "amount": float(deduction.amount) if deduction.amount is not None else None,
            "max_allowed": float(deduction.max_allowed) if deduction.max_allowed is not None else None,
            "phase_out_start": float(deduction.phase_out_start) if deduction.phase_out_start is not None else None,
            "phase_out_end": float(deduction.phase_out_end) if deduction.phase_out_end is not None else None,
            "is_recurring": deduction.is_recurring,
            "frequency": deduction.frequency,
            "start_date": deduction.start_date.isoformat() if deduction.start_date else None,
            "end_date": deduction.end_date.isoformat() if deduction.end_date else None,
            "documentation_required": deduction.documentation_required,
            "documentation_status": deduction.documentation_status,
            "tax_year": deduction.tax_year,
            "notes": deduction.notes,
            "limitations": deduction.limitations,
            "qualifications": deduction.qualifications,
            "created_by": deduction.created_by,
            "updated_by": deduction.updated_by,
            "created_at": deduction.created_at.isoformat() if deduction.created_at else None,
            "updated_at": deduction.updated_at.isoformat() if deduction.updated_at else None
        }
    
    def _credit_to_dict(self, credit: Credit) -> Dict[str, Any]:
        """Helper method to convert Credit model to dictionary"""
        return {
            "id": credit.id,
            "workspace_id": credit.workspace_id,
            "tax_plan_id": credit.tax_plan_id,
            "client_id": credit.client_id,
            "name": credit.name,
            "description": credit.description,
            "credit_type": credit.credit_type,
            "category": credit.category,
            "amount": float(credit.amount) if credit.amount is not None else None,
            "max_allowed": float(credit.max_allowed) if credit.max_allowed is not None else None,
            "is_refundable": credit.is_refundable,
            "refundable_percentage": float(credit.refundable_percentage) if credit.refundable_percentage is not None else None,
            "phase_out_start": float(credit.phase_out_start) if credit.phase_out_start is not None else None,
            "phase_out_end": float(credit.phase_out_end) if credit.phase_out_end is not None else None,
            "income_limit": float(credit.income_limit) if credit.income_limit is not None else None,
            "carryforward_allowed": credit.carryforward_allowed,
            "carryforward_years": credit.carryforward_years,
            "carryforward_amount": float(credit.carryforward_amount) if credit.carryforward_amount is not None else None,
            "is_recurring": credit.is_recurring,
            "frequency": credit.frequency,
            "eligibility_requirements": credit.eligibility_requirements,
            "documentation_required": credit.documentation_required,
            "documentation_status": credit.documentation_status,
            "tax_year": credit.tax_year,
            "notes": credit.notes,
            "qualifications": credit.qualifications,
            "created_by": credit.created_by,
            "updated_by": credit.updated_by,
            "created_at": credit.created_at.isoformat() if credit.created_at else None,
            "updated_at": credit.updated_at.isoformat() if credit.updated_at else None
        }
        
        # Update the tax record
        tax.payments = payment_summary
        
        # Recalculate refund or amount owed
        total_tax = float(tax.federal_tax or 0) + float(tax.state_tax or 0)
        if total_payments > total_tax:
            tax.refund_amount = total_payments - total_tax
            tax.amount_owed = 0
        else:
            tax.amount_owed = total_tax - total_payments
            tax.refund_amount = 0
            
        self.db.commit()
    
    def _update_tax_deductions_summary(self, tax_id: str):
        """Update the deductions JSON in the tax record"""
        tax = self.db.query(Tax).filter(Tax.id == tax_id).first()
        if not tax:
            return
        
        # Get all deductions for this tax record
        deductions = self.db.query(TaxDeduction).filter(TaxDeduction.tax_id == tax_id).all()
        
        # Group deductions by type and category
        deduction_summary = {}
        total_deductions = 0
        
        for deduction in deductions:
            deduction_type = deduction.deduction_type
            category = deduction.category
            amount = float(deduction.amount) if deduction.amount is not None else 0
            
            if deduction_type not in deduction_summary:
                deduction_summary[deduction_type] = {}
                
            if category not in deduction_summary[deduction_type]:
                deduction_summary[deduction_type][category] = 0
                
            deduction_summary[deduction_type][category] += amount
            total_deductions += amount
        
        # Add total to summary
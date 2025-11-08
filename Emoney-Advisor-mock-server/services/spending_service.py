# services/spending_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.spending import Spending, Budget, Income, Expense, BudgetCategory
from services.service_base import BaseService
from datetime import datetime
import uuid

class SpendingService(BaseService[Spending]):
    def __init__(self, db: Session):
        super().__init__(db, Spending)
    
    def get_client_spending(self, client_id: str):
        """Get all spending records for a client"""
        records = self.db.query(Spending).filter(Spending.client_id == client_id).all()
        return [self._spending_to_dict(record) for record in records]
    
    def get_spending_budgets(self, spending_id: str):
        """Get all budgets for a spending record"""
        budgets = self.db.query(Budget).filter(Budget.spending_id == spending_id).all()
        return [self._budget_to_dict(budget) for budget in budgets]
    
    def get_budget_categories(self, budget_id: str):
        """Get all categories for a budget"""
        categories = self.db.query(BudgetCategory).filter(BudgetCategory.budget_id == budget_id).all()
        return [self._category_to_dict(category) for category in categories]
    
    def get_spending_incomes(self, spending_id: str):
        """Get all income sources for a spending record"""
        incomes = self.db.query(Income).filter(Income.spending_id == spending_id).all()
        return [self._income_to_dict(income) for income in incomes]
    
    def get_spending_expenses(self, spending_id: str):
        """Get all expenses for a spending record"""
        expenses = self.db.query(Expense).filter(Expense.spending_id == spending_id).all()
        return [self._expense_to_dict(expense) for expense in expenses]
    
    def get_client_incomes(self, client_id: str):
        """Get all income sources for a client"""
        incomes = self.db.query(Income).filter(Income.client_id == client_id).all()
        return [self._income_to_dict(income) for income in incomes]
    
    def get_client_expenses(self, client_id: str):
        """Get all expenses for a client"""
        expenses = self.db.query(Expense).filter(Expense.client_id == client_id).all()
        return [self._expense_to_dict(expense) for expense in expenses]
    
    def create_budget(self, budget_data: Dict[str, Any], user_id: str = None):
        """Create a new budget"""
        if 'id' not in budget_data:
            budget_data['id'] = str(uuid.uuid4())
        
        if hasattr(Budget, 'created_at') and 'created_at' not in budget_data:
            budget_data['created_at'] = datetime.utcnow()
            
        if hasattr(Budget, 'updated_at') and 'updated_at' not in budget_data:
            budget_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(Budget, 'created_by') and 'created_by' not in budget_data:
                budget_data['created_by'] = user_id
                
            if hasattr(Budget, 'updated_by') and 'updated_by' not in budget_data:
                budget_data['updated_by'] = user_id
        
        budget = Budget(**budget_data)
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        return self._budget_to_dict(budget)
    
    def create_income(self, income_data: Dict[str, Any], user_id: str = None):
        """Create a new income source"""
        if 'id' not in income_data:
            income_data['id'] = str(uuid.uuid4())
        
        if hasattr(Income, 'created_at') and 'created_at' not in income_data:
            income_data['created_at'] = datetime.utcnow()
            
        if hasattr(Income, 'updated_at') and 'updated_at' not in income_data:
            income_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(Income, 'created_by') and 'created_by' not in income_data:
                income_data['created_by'] = user_id
                
            if hasattr(Income, 'updated_by') and 'updated_by' not in income_data:
                income_data['updated_by'] = user_id
        
        income = Income(**income_data)
        self.db.add(income)
        self.db.commit()
        self.db.refresh(income)
        
        return self._income_to_dict(income)
    
    def create_expense(self, expense_data: Dict[str, Any], user_id: str = None):
        """Create a new expense"""
        if 'id' not in expense_data:
            expense_data['id'] = str(uuid.uuid4())
        
        if hasattr(Expense, 'created_at') and 'created_at' not in expense_data:
            expense_data['created_at'] = datetime.utcnow()
            
        if hasattr(Expense, 'updated_at') and 'updated_at' not in expense_data:
            expense_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if hasattr(Expense, 'created_by') and 'created_by' not in expense_data:
                expense_data['created_by'] = user_id
                
            if hasattr(Expense, 'updated_by') and 'updated_by' not in expense_data:
                expense_data['updated_by'] = user_id
        
        expense = Expense(**expense_data)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        
        return self._expense_to_dict(expense)
    
    def _spending_to_dict(self, spending: Spending) -> Dict[str, Any]:
        """Helper method to convert Spending model to dictionary"""
        return {
            "id": spending.id,
            "workspace_id": spending.workspace_id,
            "client_id": spending.client_id,
            "status": spending.status,
            "annual_income": float(spending.annual_income) if spending.annual_income else None,
            "annual_expenses": float(spending.annual_expenses) if spending.annual_expenses else None,
            "annual_savings": float(spending.annual_savings) if spending.annual_savings else None,
            "monthly_income": float(spending.monthly_income) if spending.monthly_income else None,
            "monthly_expenses": float(spending.monthly_expenses) if spending.monthly_expenses else None,
            "monthly_savings": float(spending.monthly_savings) if spending.monthly_savings else None,
            "savings_rate": float(spending.savings_rate) if spending.savings_rate else None,
            "expense_to_income_ratio": float(spending.expense_to_income_ratio) if spending.expense_to_income_ratio else None,
            "cash_flow_status": spending.cash_flow_status,
            "last_update": spending.last_update.isoformat() if spending.last_update else None,
            "sync_status": spending.sync_status,
            "expense_categories": spending.expense_categories,
            "linked_accounts": spending.linked_accounts,
            "analysis": spending.analysis,
            "notes": spending.notes,
            "created_by": spending.created_by,
            "updated_by": spending.updated_by,
            "created_at": spending.created_at.isoformat() if spending.created_at else None,
            "updated_at": spending.updated_at.isoformat() if spending.updated_at else None
        }
    
    def _budget_to_dict(self, budget: Budget) -> Dict[str, Any]:
        """Helper method to convert Budget model to dictionary"""
        return {
            "id": budget.id,
            "workspace_id": budget.workspace_id,
            "spending_id": budget.spending_id,
            "client_id": budget.client_id,
            "name": budget.name,
            "status": budget.status,
            "period_type": budget.period_type,
            "start_date": budget.start_date.isoformat() if budget.start_date else None,
            "end_date": budget.end_date.isoformat() if budget.end_date else None,
            "total_income": float(budget.total_income) if budget.total_income else None,
            "total_expenses": float(budget.total_expenses) if budget.total_expenses else None,
            "total_savings": float(budget.total_savings) if budget.total_savings else None,
            "allocations": budget.allocations,
            "category_limits": budget.category_limits,
            "progress": budget.progress,
            "auto_categorization": budget.auto_categorization,
            "notifications": budget.notifications,
            "notes": budget.notes,
            "created_by": budget.created_by,
            "updated_by": budget.updated_by,
            "created_at": budget.created_at.isoformat() if budget.created_at else None,
            "updated_at": budget.updated_at.isoformat() if budget.updated_at else None
        }
    
    def _category_to_dict(self, category: BudgetCategory) -> Dict[str, Any]:
        """Helper method to convert BudgetCategory model to dictionary"""
        return {
            "id": category.id,
            "budget_id": category.budget_id,
            "name": category.name,
            "description": category.description,
            "amount": float(category.amount) if category.amount is not None else None,
            "created_by": category.created_by,
            "updated_by": category.updated_by,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        }
    
    def _income_to_dict(self, income: Income) -> Dict[str, Any]:
        """Helper method to convert Income model to dictionary"""
        return {
            "id": income.id,
            "workspace_id": income.workspace_id,
            "spending_id": income.spending_id,
            "client_id": income.client_id,
            "plan_id": income.plan_id,
            "name": income.name,
            "income_type": income.income_type,
            "status": income.status,
            "frequency": income.frequency,
            "annual_amount": float(income.annual_amount) if income.annual_amount else None,
            "monthly_amount": float(income.monthly_amount) if income.monthly_amount else None,
            "amount_per_payment": float(income.amount_per_payment) if income.amount_per_payment else None,
            "payment_day": income.payment_day,
            "start_date": income.start_date.isoformat() if income.start_date else None,
            "end_date": income.end_date.isoformat() if income.end_date else None,
            "growth_rate": float(income.growth_rate) if income.growth_rate else None,
            "income_source": income.income_source,
            "taxable": income.taxable,
            "tax_rate": float(income.tax_rate) if income.tax_rate else None,
            "notes": income.notes,
            "created_by": income.created_by,
            "updated_by": income.updated_by,
            "created_at": income.created_at.isoformat() if income.created_at else None,
            "updated_at": income.updated_at.isoformat() if income.updated_at else None
        }
    
    def _expense_to_dict(self, expense: Expense) -> Dict[str, Any]:
        """Helper method to convert Expense model to dictionary"""
        return {
            "id": expense.id,
            "workspace_id": expense.workspace_id,
            "spending_id": expense.spending_id,
            "client_id": expense.client_id,
            "plan_id": expense.plan_id,
            "goal_id": expense.goal_id,
            "name": expense.name,
            "category": expense.category,
            "status": expense.status,
            "frequency": expense.frequency,
            "annual_amount": float(expense.annual_amount) if expense.annual_amount else None,
            "monthly_amount": float(expense.monthly_amount) if expense.monthly_amount else None,
            "amount_per_payment": float(expense.amount_per_payment) if expense.amount_per_payment else None,
            "payment_day": expense.payment_day,
            "start_date": expense.start_date.isoformat() if expense.start_date else None,
            "end_date": expense.end_date.isoformat() if expense.end_date else None,
            "growth_rate": float(expense.growth_rate) if expense.growth_rate else None,
            "auto_payment": expense.auto_payment,
            "payment_method": expense.payment_method,
            "is_tax_deductible": expense.is_tax_deductible,
            "expense_source": expense.expense_source,
            "is_discretionary": expense.is_discretionary,
            "is_goal": expense.is_goal,
            "notes": expense.notes,
            "created_by": expense.created_by,
            "updated_by": expense.updated_by,
            "created_at": expense.created_at.isoformat() if expense.created_at else None,
            "updated_at": expense.updated_at.isoformat() if expense.updated_at else None
        }
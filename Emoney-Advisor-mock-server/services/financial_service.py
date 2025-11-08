# services/financial_plan_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.financial import FinancialPlan, Goal, MonteCarlo, Projection, Scenario, CashFlow
from services.service_base import BaseService
from datetime import datetime
import uuid

class FinancialPlanService(BaseService[FinancialPlan]):
    def __init__(self, db: Session):
        super().__init__(db, FinancialPlan)
    
    def get_client_plans(self, client_id: str):
        """Get all financial plans for a client"""
        plans = self.db.query(FinancialPlan).filter(FinancialPlan.client_id == client_id).all()
        return [self._plan_to_dict(plan) for plan in plans]
    
    def get_plan_goals(self, plan_id: str):
        """Get all goals for a financial plan"""
        goals = self.db.query(Goal).filter(Goal.plan_id == plan_id).all()
        return [self._goal_to_dict(goal) for goal in goals]
    
    def get_plan_monte_carlos(self, plan_id: str):
        """Get all Monte Carlo simulations for a financial plan"""
        simulations = self.db.query(MonteCarlo).filter(MonteCarlo.plan_id == plan_id).all()
        return [self._monte_carlo_to_dict(sim) for sim in simulations]
    
    def get_plan_projections(self, plan_id: str):
        """Get all projections for a financial plan"""
        projections = self.db.query(Projection).filter(Projection.plan_id == plan_id).all()
        return [self._projection_to_dict(proj) for proj in projections]
    
    def get_plan_scenarios(self, plan_id: str):
        """Get all scenarios for a financial plan"""
        scenarios = self.db.query(Scenario).filter(Scenario.plan_id == plan_id).all()
        return [self._scenario_to_dict(scenario) for scenario in scenarios]
    
    def get_scenario_by_id(self, scenario_id: str):
        """Get a specific scenario by ID"""
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return None
        return self._scenario_to_dict(scenario)
    
    def get_scenario_cash_flows(self, scenario_id: str):
        """Get all cash flows for a specific scenario"""
        cash_flows = self.db.query(CashFlow).filter(CashFlow.scenario_id == scenario_id).all()
        return [self._cash_flow_to_dict(cf) for cf in cash_flows]
    
    def get_scenario_monte_carlos(self, scenario_id: str):
        """Get all Monte Carlo simulations for a specific scenario"""
        simulations = self.db.query(MonteCarlo).filter(MonteCarlo.scenario_id == scenario_id).all()
        return [self._monte_carlo_to_dict(sim) for sim in simulations]
    
    def create_scenario(self, scenario_data: Dict[str, Any], user_id: str = None):
        """Create a new scenario"""
        if 'id' not in scenario_data:
            scenario_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in scenario_data and hasattr(Scenario, 'created_at'):
            scenario_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in scenario_data and hasattr(Scenario, 'updated_at'):
            scenario_data['updated_at'] = datetime.utcnow()
            
        # If this is set as the default scenario, unset any other defaults for this plan
        if scenario_data.get('is_default', False):
            plan_id = scenario_data.get('plan_id')
            if plan_id:
                existing_defaults = self.db.query(Scenario).filter(
                    Scenario.plan_id == plan_id,
                    Scenario.is_default == True
                ).all()
                for default in existing_defaults:
                    default.is_default = False
        
        scenario = Scenario(**scenario_data)
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        
        return self._scenario_to_dict(scenario)
    
    def update_scenario(self, scenario_id: str, scenario_data: Dict[str, Any], user_id: str = None):
        """Update an existing scenario"""
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return None
        
        # If is_default is being set to True, unset any other defaults for this plan
        if 'is_default' in scenario_data and scenario_data['is_default'] and not scenario.is_default:
            existing_defaults = self.db.query(Scenario).filter(
                Scenario.plan_id == scenario.plan_id,
                Scenario.is_default == True,
                Scenario.id != scenario_id
            ).all()
            for default in existing_defaults:
                default.is_default = False
            
        for key, value in scenario_data.items():
            if hasattr(scenario, key):
                setattr(scenario, key, value)
                
        if hasattr(scenario, 'updated_at'):
            scenario.updated_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(scenario)
        
        return self._scenario_to_dict(scenario)
    
    def delete_scenario(self, scenario_id: str):
        """Delete a scenario"""
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return False
            
        # If this is a default scenario, we need to potentially set another one as default
        if scenario.is_default:
            other_scenario = self.db.query(Scenario).filter(
                Scenario.plan_id == scenario.plan_id,
                Scenario.id != scenario_id
            ).first()
            
            if other_scenario:
                other_scenario.is_default = True
        
        self.db.delete(scenario)
        self.db.commit()
        
        return True
    
    def create_goal(self, goal_data: Dict[str, Any], user_id: str = None):
        """Create a new goal"""
        if 'id' not in goal_data:
            goal_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in goal_data and hasattr(Goal, 'created_at'):
            goal_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in goal_data and hasattr(Goal, 'updated_at'):
            goal_data['updated_at'] = datetime.utcnow()
            
        goal = Goal(**goal_data)
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        
        return self._goal_to_dict(goal)
    
    def update_goal(self, goal_id: str, goal_data: Dict[str, Any], user_id: str = None):
        """Update an existing goal"""
        goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None
            
        for key, value in goal_data.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
                
        if hasattr(goal, 'updated_at'):
            goal.updated_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(goal)
        
        return self._goal_to_dict(goal)

    # Cash Flow Methods
    def create_cash_flow(self, cash_flow_data: Dict[str, Any], user_id: str = None):
        """Create a new cash flow"""
        if 'id' not in cash_flow_data:
            cash_flow_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in cash_flow_data and hasattr(CashFlow, 'created_at'):
            cash_flow_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in cash_flow_data and hasattr(CashFlow, 'updated_at'):
            cash_flow_data['updated_at'] = datetime.utcnow()
        
        # Calculate net cash flow if not provided
        if 'net_cash_flow' not in cash_flow_data:
            total_income = cash_flow_data.get('total_income', 0.0)
            total_expenses = cash_flow_data.get('total_expenses', 0.0)
            cash_flow_data['net_cash_flow'] = total_income - total_expenses
        
        # Calculate total income if not provided
        if 'total_income' not in cash_flow_data:
            cash_flow_data['total_income'] = sum([
                cash_flow_data.get('salary_income', 0.0),
                cash_flow_data.get('business_income', 0.0),
                cash_flow_data.get('investment_income', 0.0),
                cash_flow_data.get('rental_income', 0.0),
                cash_flow_data.get('other_income', 0.0)
            ])
        
        # Calculate total expenses if not provided
        if 'total_expenses' not in cash_flow_data:
            cash_flow_data['total_expenses'] = sum([
                cash_flow_data.get('housing_expense', 0.0),
                cash_flow_data.get('utilities_expense', 0.0),
                cash_flow_data.get('food_expense', 0.0),
                cash_flow_data.get('transportation_expense', 0.0),
                cash_flow_data.get('healthcare_expense', 0.0),
                cash_flow_data.get('insurance_expense', 0.0),
                cash_flow_data.get('debt_payments', 0.0),
                cash_flow_data.get('entertainment_expense', 0.0),
                cash_flow_data.get('personal_expense', 0.0),
                cash_flow_data.get('other_expense', 0.0)
            ])
            
        cash_flow = CashFlow(**cash_flow_data)
        self.db.add(cash_flow)
        self.db.commit()
        self.db.refresh(cash_flow)
        
        return self._cash_flow_to_dict(cash_flow)

    def update_cash_flow(self, cash_flow_id: str, cash_flow_data: Dict[str, Any], user_id: str = None):
        """Update an existing cash flow"""
        cash_flow = self.db.query(CashFlow).filter(CashFlow.id == cash_flow_id).first()
        if not cash_flow:
            return None
            
        # Update individual fields
        for key, value in cash_flow_data.items():
            if hasattr(cash_flow, key):
                setattr(cash_flow, key, value)
        
        # Recalculate totals if individual income or expense components were updated
        income_components = ['salary_income', 'business_income', 'investment_income', 'rental_income', 'other_income']
        expense_components = ['housing_expense', 'utilities_expense', 'food_expense', 'transportation_expense', 
                             'healthcare_expense', 'insurance_expense', 'debt_payments', 'entertainment_expense', 
                             'personal_expense', 'other_expense']
        
        # Check if any income components were updated
        income_updated = any(key in cash_flow_data for key in income_components)
        # Check if any expense components were updated
        expense_updated = any(key in cash_flow_data for key in expense_components)
        
        # Recalculate total income if any income component was updated
        if income_updated and 'total_income' not in cash_flow_data:
            cash_flow.total_income = sum([
                cash_flow.salary_income or 0.0,
                cash_flow.business_income or 0.0,
                cash_flow.investment_income or 0.0,
                cash_flow.rental_income or 0.0,
                cash_flow.other_income or 0.0
            ])
        
        # Recalculate total expenses if any expense component was updated
        if expense_updated and 'total_expenses' not in cash_flow_data:
            cash_flow.total_expenses = sum([
                cash_flow.housing_expense or 0.0,
                cash_flow.utilities_expense or 0.0,
                cash_flow.food_expense or 0.0,
                cash_flow.transportation_expense or 0.0,
                cash_flow.healthcare_expense or 0.0,
                cash_flow.insurance_expense or 0.0,
                cash_flow.debt_payments or 0.0,
                cash_flow.entertainment_expense or 0.0,
                cash_flow.personal_expense or 0.0,
                cash_flow.other_expense or 0.0
            ])
        
        # Recalculate net cash flow if either total income or total expenses were updated
        if (income_updated or 'total_income' in cash_flow_data or 
            expense_updated or 'total_expenses' in cash_flow_data) and 'net_cash_flow' not in cash_flow_data:
            cash_flow.net_cash_flow = cash_flow.total_income - cash_flow.total_expenses
        
        # Update timestamp
        if hasattr(cash_flow, 'updated_at'):
            cash_flow.updated_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(cash_flow)
        
        return self._cash_flow_to_dict(cash_flow)

    def delete_cash_flow(self, cash_flow_id: str):
        """Delete a cash flow"""
        cash_flow = self.db.query(CashFlow).filter(CashFlow.id == cash_flow_id).first()
        if not cash_flow:
            return False
            
        self.db.delete(cash_flow)
        self.db.commit()
        
        return True

    def get_cash_flows_by_plan(self, plan_id: str):
        """Get all cash flows for a financial plan"""
        cash_flows = self.db.query(CashFlow).filter(CashFlow.plan_id == plan_id).all()
        return [self._cash_flow_to_dict(cf) for cf in cash_flows]

    def get_cash_flow_by_id(self, cash_flow_id: str):
        """Get a specific cash flow by ID"""
        cash_flow = self.db.query(CashFlow).filter(CashFlow.id == cash_flow_id).first()
        if not cash_flow:
            return None
        return self._cash_flow_to_dict(cash_flow)
    
    def _plan_to_dict(self, plan: FinancialPlan) -> Dict[str, Any]:
        """Helper method to convert FinancialPlan model to dictionary"""
        return {
            "id": plan.id,
            "client_id": plan.client_id,
            "name": plan.name,
            "description": plan.description,
            "status": plan.status,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }
    
    def _goal_to_dict(self, goal: Goal) -> Dict[str, Any]:
        """Helper method to convert Goal model to dictionary"""
        return {
            "id": goal.id,
            "plan_id": goal.plan_id,
            "name": goal.name,
            "description": goal.description,
            "target_amount": float(goal.target_amount) if goal.target_amount is not None else None,
            "current_amount": float(goal.current_amount) if goal.current_amount is not None else None,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "priority": goal.priority,
            "category": goal.category,
            "created_at": goal.created_at.isoformat() if goal.created_at else None,
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
        }
    
    def _monte_carlo_to_dict(self, monte_carlo: MonteCarlo) -> Dict[str, Any]:
        """Helper method to convert MonteCarlo model to dictionary"""
        return {
            "id": monte_carlo.id,
            "plan_id": monte_carlo.plan_id,
            "scenario_id": monte_carlo.scenario_id,
            "success_rate": float(monte_carlo.success_rate) if monte_carlo.success_rate is not None else None,
            "iterations": monte_carlo.iterations,
            "confidence_interval": float(monte_carlo.confidence_interval) if monte_carlo.confidence_interval is not None else None,
            "median_ending_value": float(monte_carlo.median_ending_value) if monte_carlo.median_ending_value is not None else None,
            "lowest_percentile_value": float(monte_carlo.lowest_percentile_value) if monte_carlo.lowest_percentile_value is not None else None,
            "highest_percentile_value": float(monte_carlo.highest_percentile_value) if monte_carlo.highest_percentile_value is not None else None,
            "results_detail": monte_carlo.results_detail,
            "created_at": monte_carlo.created_at.isoformat() if monte_carlo.created_at else None,
            "updated_at": monte_carlo.updated_at.isoformat() if monte_carlo.updated_at else None
        }
    
    def _projection_to_dict(self, projection: Projection) -> Dict[str, Any]:
        """Helper method to convert Projection model to dictionary"""
        return {
            "id": projection.id,
            "plan_id": projection.plan_id,
            "year": projection.year,
            "assets": float(projection.assets) if projection.assets is not None else None,
            "liabilities": float(projection.liabilities) if projection.liabilities is not None else None,
            "net_worth": float(projection.net_worth) if projection.net_worth is not None else None,
            "income": float(projection.income) if projection.income is not None else None,
            "expenses": float(projection.expenses) if projection.expenses is not None else None,
            "cash_flow": float(projection.cash_flow) if projection.cash_flow is not None else None,
            "created_at": projection.created_at.isoformat() if projection.created_at else None
        }
    
    def _scenario_to_dict(self, scenario: Scenario) -> Dict[str, Any]:
        """Helper method to convert Scenario model to dictionary"""
        return {
            "id": scenario.id,
            "plan_id": scenario.plan_id,
            "name": scenario.name,
            "description": scenario.description,
            "is_default": scenario.is_default,
            "status": scenario.status,
            "retirement_age": scenario.retirement_age,
            "life_expectancy": scenario.life_expectancy,
            "inflation_rate": float(scenario.inflation_rate) if scenario.inflation_rate is not None else None,
            "investment_return_rate": float(scenario.investment_return_rate) if scenario.investment_return_rate is not None else None,
            "tax_rate": float(scenario.tax_rate) if scenario.tax_rate is not None else None,
            "withdrawal_strategy": scenario.withdrawal_strategy,
            "social_security_strategy": scenario.social_security_strategy,
            "parameters": scenario.parameters,
            "results_summary": scenario.results_summary,
            "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
            "updated_at": scenario.updated_at.isoformat() if scenario.updated_at else None
        }
    
    def _cash_flow_to_dict(self, cash_flow: CashFlow) -> Dict[str, Any]:
        """Helper method to convert CashFlow model to dictionary"""
        return {
            "id": cash_flow.id,
            "plan_id": cash_flow.plan_id,
            "scenario_id": cash_flow.scenario_id,
            "salary_income": float(cash_flow.salary_income) if cash_flow.salary_income is not None else None,
            "business_income": float(cash_flow.business_income) if cash_flow.business_income is not None else None,
            "investment_income": float(cash_flow.investment_income) if cash_flow.investment_income is not None else None,
            "rental_income": float(cash_flow.rental_income) if cash_flow.rental_income is not None else None,
            "other_income": float(cash_flow.other_income) if cash_flow.other_income is not None else None,
            "total_income": float(cash_flow.total_income) if cash_flow.total_income is not None else None,
            "housing_expense": float(cash_flow.housing_expense) if cash_flow.housing_expense is not None else None,
            "utilities_expense": float(cash_flow.utilities_expense) if cash_flow.utilities_expense is not None else None,
            "food_expense": float(cash_flow.food_expense) if cash_flow.food_expense is not None else None,
            "transportation_expense": float(cash_flow.transportation_expense) if cash_flow.transportation_expense is not None else None,
            "healthcare_expense": float(cash_flow.healthcare_expense) if cash_flow.healthcare_expense is not None else None,
            "insurance_expense": float(cash_flow.insurance_expense) if cash_flow.insurance_expense is not None else None,
            "debt_payments": float(cash_flow.debt_payments) if cash_flow.debt_payments is not None else None,
            "entertainment_expense": float(cash_flow.entertainment_expense) if cash_flow.entertainment_expense is not None else None,
            "personal_expense": float(cash_flow.personal_expense) if cash_flow.personal_expense is not None else None,
            "other_expense": float(cash_flow.other_expense) if cash_flow.other_expense is not None else None,
            "total_expenses": float(cash_flow.total_expenses) if cash_flow.total_expenses is not None else None,
            "net_cash_flow": float(cash_flow.net_cash_flow) if cash_flow.net_cash_flow is not None else None,
            "period": cash_flow.period,
            "year": cash_flow.year,
            "created_at": cash_flow.created_at.isoformat() if cash_flow.created_at else None,
            "updated_at": cash_flow.updated_at.isoformat() if cash_flow.updated_at else None
        }
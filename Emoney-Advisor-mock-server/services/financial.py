# services/financial.py - Version 3: Financial Planning Services

from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from models.financial import (
    FinancialPlan, Goal, Scenario, CashFlow, NetWorth
)


class FinancialPlanService:
    """Service for Financial Plan operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, household_id: Optional[str] = None,
                status: Optional[str] = None, plan_type: Optional[str] = None) -> List[FinancialPlan]:
        """Get all financial plans with pagination and optional filters"""
        query = db.query(FinancialPlan)
        if client_id:
            query = query.filter(FinancialPlan.client_id == client_id)
        if household_id:
            query = query.filter(FinancialPlan.household_id == household_id)
        if status:
            query = query.filter(FinancialPlan.status == status)
        if plan_type:
            query = query.filter(FinancialPlan.plan_type == plan_type)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, plan_id: str, include_goals: bool = False, 
                  include_scenarios: bool = False) -> Optional[FinancialPlan]:
        """Get financial plan by ID with optional related data"""
        query = db.query(FinancialPlan).options(
            joinedload(FinancialPlan.client),
            joinedload(FinancialPlan.household)
        )
        if include_goals:
            query = query.options(joinedload(FinancialPlan.goals))
        if include_scenarios:
            query = query.options(joinedload(FinancialPlan.scenarios))
        return query.filter(FinancialPlan.plan_id == plan_id).first()
    
    def get_plan_goals(self, db: Session, plan_id: str, status: Optional[str] = None) -> List[Goal]:
        """Get all goals for a specific financial plan"""
        query = db.query(Goal).filter(Goal.plan_id == plan_id)
        if status:
            query = query.filter(Goal.status == status)
        return query.order_by(Goal.priority, Goal.target_date).all()
    
    def get_plan_scenarios(self, db: Session, plan_id: str, 
                          scenario_type: Optional[str] = None) -> List[Scenario]:
        """Get all scenarios for a specific financial plan"""
        query = db.query(Scenario).filter(Scenario.plan_id == plan_id)
        if scenario_type:
            query = query.filter(Scenario.scenario_type == scenario_type)
        return query.order_by(Scenario.created_date).all()
    
    def get_plan_cashflow(self, db: Session, plan_id: str, 
                         start_year: Optional[int] = None, 
                         end_year: Optional[int] = None) -> List[CashFlow]:
        """Get cash flow projections for a specific financial plan"""
        query = db.query(CashFlow).filter(CashFlow.plan_id == plan_id)
        if start_year:
            query = query.filter(CashFlow.year >= start_year)
        if end_year:
            query = query.filter(CashFlow.year <= end_year)
        return query.order_by(CashFlow.year, CashFlow.month).all()
    
    def get_plan_networth(self, db: Session, plan_id: str, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[NetWorth]:
        """Get net worth analysis for a specific financial plan"""
        query = db.query(NetWorth).filter(NetWorth.plan_id == plan_id)
        if start_date:
            query = query.filter(NetWorth.as_of_date >= start_date)
        if end_date:
            query = query.filter(NetWorth.as_of_date <= end_date)
        return query.order_by(NetWorth.as_of_date).all()


class GoalService:
    """Service for Goal operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, plan_id: Optional[str] = None,
                goal_type: Optional[str] = None, status: Optional[str] = None) -> List[Goal]:
        """Get all goals with pagination and optional filters"""
        query = db.query(Goal)
        if client_id:
            query = query.filter(Goal.client_id == client_id)
        if plan_id:
            query = query.filter(Goal.plan_id == plan_id)
        if goal_type:
            query = query.filter(Goal.goal_type == goal_type)
        if status:
            query = query.filter(Goal.status == status)
        return query.order_by(Goal.priority, Goal.target_date).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, goal_id: str) -> Optional[Goal]:
        """Get goal by ID with plan and client details"""
        return db.query(Goal).options(
            joinedload(Goal.financial_plan),
            joinedload(Goal.client)
        ).filter(Goal.goal_id == goal_id).first()
    
    def get_client_goals(self, db: Session, client_id: str,
                        goal_type: Optional[str] = None, 
                        status: Optional[str] = None) -> List[Goal]:
        """Get all goals for a specific client"""
        query = db.query(Goal).filter(Goal.client_id == client_id)
        if goal_type:
            query = query.filter(Goal.goal_type == goal_type)
        if status:
            query = query.filter(Goal.status == status)
        return query.order_by(Goal.priority, Goal.target_date).all()


class ScenarioService:
    """Service for Scenario operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, scenario_type: Optional[str] = None,
                status: Optional[str] = None) -> List[Scenario]:
        """Get all scenarios with pagination and optional filters"""
        query = db.query(Scenario)
        if plan_id:
            query = query.filter(Scenario.plan_id == plan_id)
        if scenario_type:
            query = query.filter(Scenario.scenario_type == scenario_type)
        if status:
            query = query.filter(Scenario.status == status)
        return query.order_by(Scenario.created_date).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID with financial plan details"""
        return db.query(Scenario).options(
            joinedload(Scenario.financial_plan)
        ).filter(Scenario.scenario_id == scenario_id).first()


class CashFlowService:
    """Service for Cash Flow operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, year: Optional[int] = None,
                status: Optional[str] = None) -> List[CashFlow]:
        """Get all cash flows with pagination and optional filters"""
        query = db.query(CashFlow)
        if plan_id:
            query = query.filter(CashFlow.plan_id == plan_id)
        if year:
            query = query.filter(CashFlow.year == year)
        if status:
            query = query.filter(CashFlow.status == status)
        return query.order_by(CashFlow.year, CashFlow.month).offset(skip).limit(limit).all()
    
    def get_by_plan_id(self, db: Session, plan_id: str,
                      start_year: Optional[int] = None,
                      end_year: Optional[int] = None) -> List[CashFlow]:
        """Get cash flow projections for a specific plan"""
        query = db.query(CashFlow).filter(CashFlow.plan_id == plan_id)
        if start_year:
            query = query.filter(CashFlow.year >= start_year)
        if end_year:
            query = query.filter(CashFlow.year <= end_year)
        return query.order_by(CashFlow.year, CashFlow.month).all()
    
    def get_cashflow_analysis(self, db: Session, plan_id: str) -> dict:
        """Get cash flow analysis summary for a plan"""
        cash_flows = self.get_by_plan_id(db, plan_id)
        if not cash_flows:
            return {}
        
        total_income = sum(cf.total_income or 0 for cf in cash_flows)
        total_expenses = sum(cf.total_expenses or 0 for cf in cash_flows)
        net_cash_flow = total_income - total_expenses
        
        return {
            "plan_id": plan_id,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cash_flow": net_cash_flow,
            "projection_years": len(set(cf.year for cf in cash_flows)),
            "final_cumulative_cash_flow": cash_flows[-1].cumulative_cash_flow if cash_flows else 0
        }


class NetWorthService:
    """Service for Net Worth operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, household_id: Optional[str] = None,
                status: Optional[str] = None) -> List[NetWorth]:
        """Get all net worth records with pagination and optional filters"""
        query = db.query(NetWorth)
        if plan_id:
            query = query.filter(NetWorth.plan_id == plan_id)
        if household_id:
            query = query.filter(NetWorth.household_id == household_id)
        if status:
            query = query.filter(NetWorth.status == status)
        return query.order_by(NetWorth.as_of_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, net_worth_id: str) -> Optional[NetWorth]:
        """Get net worth by ID with plan and household details"""
        return db.query(NetWorth).options(
            joinedload(NetWorth.financial_plan),
            joinedload(NetWorth.household)
        ).filter(NetWorth.net_worth_id == net_worth_id).first()
    
    def get_latest_by_plan(self, db: Session, plan_id: str) -> Optional[NetWorth]:
        """Get the most recent net worth for a plan"""
        return db.query(NetWorth).filter(
            NetWorth.plan_id == plan_id
        ).order_by(NetWorth.as_of_date.desc()).first()
    
    def get_latest_by_household(self, db: Session, household_id: str) -> Optional[NetWorth]:
        """Get the most recent net worth for a household"""
        return db.query(NetWorth).filter(
            NetWorth.household_id == household_id
        ).order_by(NetWorth.as_of_date.desc()).first()
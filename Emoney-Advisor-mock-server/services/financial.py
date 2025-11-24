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
            query = query.filter(FinancialPlan.ClientID == client_id)
        if household_id:
            query = query.filter(FinancialPlan.HouseholdID == household_id)
        if status:
            query = query.filter(FinancialPlan.Status == status)
        if plan_type:
            query = query.filter(FinancialPlan.PlanType == plan_type)
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
        return query.filter(FinancialPlan.PlanID == plan_id).first()
    
    def get_plan_goals(self, db: Session, plan_id: str, status: Optional[str] = None) -> List[Goal]:
        """Get all goals for a specific financial plan"""
        query = db.query(Goal).filter(Goal.PlanID == plan_id)
        if status:
            query = query.filter(Goal.Status == status)
        return query.order_by(Goal.Priority, Goal.TargetDate).all()
    
    def get_plan_scenarios(self, db: Session, plan_id: str, 
                          scenario_type: Optional[str] = None) -> List[Scenario]:
        """Get all scenarios for a specific financial plan"""
        query = db.query(Scenario).filter(Scenario.PlanID == plan_id)
        if scenario_type:
            query = query.filter(Scenario.ScenarioType == scenario_type)
        return query.order_by(Scenario.CreatedDate).all()
    
    def get_plan_cashflow(self, db: Session, plan_id: str, 
                         start_year: Optional[int] = None, 
                         end_year: Optional[int] = None) -> List[CashFlow]:
        """Get cash flow projections for a specific financial plan"""
        query = db.query(CashFlow).filter(CashFlow.PlanID == plan_id)
        if start_year:
            query = query.filter(CashFlow.Year >= start_year)
        if end_year:
            query = query.filter(CashFlow.Year <= end_year)
        return query.order_by(CashFlow.Year, CashFlow.Month).all()
    
    def get_plan_networth(self, db: Session, plan_id: str, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[NetWorth]:
        """Get net worth analysis for a specific financial plan"""
        query = db.query(NetWorth).filter(NetWorth.PlanID == plan_id)
        if start_date:
            query = query.filter(NetWorth.AsOfDate >= start_date)
        if end_date:
            query = query.filter(NetWorth.AsOfDate <= end_date)
        return query.order_by(NetWorth.AsOfDate).all()


class GoalService:
    """Service for Goal operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, plan_id: Optional[str] = None,
                goal_type: Optional[str] = None, status: Optional[str] = None) -> List[Goal]:
        """Get all goals with pagination and optional filters"""
        query = db.query(Goal)
        if client_id:
            query = query.filter(Goal.ClientID == client_id)
        if plan_id:
            query = query.filter(Goal.PlanID == plan_id)
        if goal_type:
            query = query.filter(Goal.GoalType == goal_type)
        if status:
            query = query.filter(Goal.Status == status)
        return query.order_by(Goal.Priority, Goal.TargetDate).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, goal_id: str) -> Optional[Goal]:
        """Get goal by ID with plan and client details"""
        return db.query(Goal).options(
            joinedload(Goal.financial_plan),
            joinedload(Goal.client)
        ).filter(Goal.GoalID == goal_id).first()
    
    def get_client_goals(self, db: Session, client_id: str,
                        goal_type: Optional[str] = None, 
                        status: Optional[str] = None) -> List[Goal]:
        """Get all goals for a specific client"""
        query = db.query(Goal).filter(Goal.ClientID == client_id)
        if goal_type:
            query = query.filter(Goal.GoalType == goal_type)
        if status:
            query = query.filter(Goal.Status == status)
        return query.order_by(Goal.Priority, Goal.TargetDate).all()


class ScenarioService:
    """Service for Scenario operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, scenario_type: Optional[str] = None,
                status: Optional[str] = None) -> List[Scenario]:
        """Get all scenarios with pagination and optional filters"""
        query = db.query(Scenario)
        if plan_id:
            query = query.filter(Scenario.PlanID == plan_id)
        if scenario_type:
            query = query.filter(Scenario.ScenarioType == scenario_type)
        if status:
            query = query.filter(Scenario.Status == status)
        return query.order_by(Scenario.CreatedDate).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID with financial plan details"""
        return db.query(Scenario).options(
            joinedload(Scenario.financial_plan)
        ).filter(Scenario.ScenarioID == scenario_id).first()


class CashFlowService:
    """Service for Cash Flow operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, year: Optional[int] = None,
                status: Optional[str] = None) -> List[CashFlow]:
        """Get all cash flows with pagination and optional filters"""
        query = db.query(CashFlow)
        if plan_id:
            query = query.filter(CashFlow.PlanID == plan_id)
        if year:
            query = query.filter(CashFlow.Year == year)
        if status:
            query = query.filter(CashFlow.Status == status)
        return query.order_by(CashFlow.Year, CashFlow.Month).offset(skip).limit(limit).all()
    
    def get_by_plan_id(self, db: Session, plan_id: str,
                      start_year: Optional[int] = None,
                      end_year: Optional[int] = None) -> List[CashFlow]:
        """Get cash flow projections for a specific plan"""
        query = db.query(CashFlow).filter(CashFlow.PlanID == plan_id)
        if start_year:
            query = query.filter(CashFlow.Year >= start_year)
        if end_year:
            query = query.filter(CashFlow.Year <= end_year)
        return query.order_by(CashFlow.Year, CashFlow.Month).all()
    
    def get_cashflow_analysis(self, db: Session, plan_id: str) -> dict:
        """Get cash flow analysis summary for a plan"""
        cash_flows = self.get_by_plan_id(db, plan_id)
        if not cash_flows:
            return {}
        
        total_income = sum(cf.TotalIncome or 0 for cf in cash_flows)
        total_expenses = sum(cf.TotalExpenses or 0 for cf in cash_flows)
        net_cash_flow = total_income - total_expenses
        
        return {
            "plan_id": plan_id,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cash_flow": net_cash_flow,
            "projection_years": len(set(cf.Year for cf in cash_flows)),
            "final_cumulative_cash_flow": cash_flows[-1].CumulativeCashFlow if cash_flows else 0
        }


class NetWorthService:
    """Service for Net Worth operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                plan_id: Optional[str] = None, household_id: Optional[str] = None,
                status: Optional[str] = None) -> List[NetWorth]:
        """Get all net worth records with pagination and optional filters"""
        query = db.query(NetWorth)
        if plan_id:
            query = query.filter(NetWorth.PlanID == plan_id)
        if household_id:
            query = query.filter(NetWorth.HouseholdID == household_id)
        if status:
            query = query.filter(NetWorth.Status == status)
        return query.order_by(NetWorth.AsOfDate.desc()).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, net_worth_id: str) -> Optional[NetWorth]:
        """Get net worth by ID with plan and household details"""
        return db.query(NetWorth).options(
            joinedload(NetWorth.financial_plan),
            joinedload(NetWorth.household)
        ).filter(NetWorth.NetWorthID == net_worth_id).first()
    
    def get_latest_by_plan(self, db: Session, plan_id: str) -> Optional[NetWorth]:
        """Get the most recent net worth for a plan"""
        return db.query(NetWorth).filter(
            NetWorth.PlanID == plan_id
        ).order_by(NetWorth.AsOfDate.desc()).first()
    
    def get_latest_by_household(self, db: Session, household_id: str) -> Optional[NetWorth]:
        """Get the most recent net worth for a household"""
        return db.query(NetWorth).filter(
            NetWorth.HouseholdID == household_id
        ).order_by(NetWorth.AsOfDate.desc()).first()
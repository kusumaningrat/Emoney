# routes/financial.py - eMoney Advisor Financial Planning Core (Version 3)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from database import get_db
from models.financial import FinancialPlan, Goal, Scenario, CashFlow, NetWorth
from services.financial import (
    FinancialPlanService, GoalService, ScenarioService, 
    CashFlowService, NetWorthService
)

router = APIRouter(
    tags=["eMoney Financial Planning Core"],
    dependencies=[]
)

# Helper function to convert SQLAlchemy models to dict
def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        # Handle enum serialization
        elif hasattr(value, 'value'):
            value = value.value
        # Handle decimal serialization
        elif hasattr(value, '__float__'):
            value = float(value)
        result[column.name] = value
    return result

# ============================================================================
# PLANS & GOALS ENDPOINTS
# ============================================================================

@router.get("/plans")
def get_plans(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    planType: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    includeGoals: bool = Query(False),
    includeScenarios: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List all financial plans with pagination"""
    service = FinancialPlanService()
    skip = (page - 1) * pageSize
    
    # Get plans with filters
    plans = service.get_all(
        db, 
        skip=skip, 
        limit=pageSize,
        client_id=clientId,
        status=status,
        plan_type=planType
    )
    
    # Count total for pagination
    all_plans = service.get_all(
        db,
        client_id=clientId,
        status=status,
        plan_type=planType
    )
    total = len(all_plans)
    
    # Convert plans to dict and optionally include nested data
    plans_data = []
    for plan in plans:
        plan_dict = model_to_dict(plan)
        
        if includeGoals:
            plan_dict['goals'] = [model_to_dict(g) for g in service.get_plan_goals(db, plan.PlanID)]
        
        if includeScenarios:
            plan_dict['scenarios'] = [model_to_dict(s) for s in service.get_plan_scenarios(db, plan.PlanID)]
        
        plans_data.append(plan_dict)
    
    return {
        "plans": plans_data,
        "total": total,
        "page": page,
        "pageSize": len(plans),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/plans/{planId}")
def get_financial_plan(
    planId: str = Path(...),
    includeGoals: bool = Query(False),
    includeScenarios: bool = Query(False),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get specific financial plan"""
    service = FinancialPlanService()
    plan = service.get_by_id(db, planId, include_goals=includeGoals, include_scenarios=includeScenarios)
    
    if not plan:
        raise HTTPException(status_code=404, detail=f"Financial plan {planId} not found")
    
    result = model_to_dict(plan)
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'goals' in includes and not includeGoals:
            result['goals'] = [model_to_dict(g) for g in service.get_plan_goals(db, planId)]
        
        if 'scenarios' in includes and not includeScenarios:
            result['scenarios'] = [model_to_dict(s) for s in service.get_plan_scenarios(db, planId)]
        
        if 'cashflow' in includes:
            cashflow_service = CashFlowService()
            result['cashflow'] = [model_to_dict(cf) for cf in cashflow_service.get_by_plan_id(db, planId)]
        
        if 'networth' in includes:
            networth_service = NetWorthService()
            latest_networth = networth_service.get_latest_by_plan(db, planId)
            result['networth'] = model_to_dict(latest_networth) if latest_networth else None
    
    return result

@router.get("/plans/{planId}/goals")
def get_plan_goals(
    planId: str = Path(...),
    status: Optional[str] = Query(None),
    goalType: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get plan goals"""
    service = FinancialPlanService()
    plan = service.get_by_id(db, planId)
    
    if not plan:
        raise HTTPException(status_code=404, detail=f"Financial plan {planId} not found")
    
    goals = service.get_plan_goals(db, planId, status=status)
    
    # Filter by goalType if specified
    if goalType:
        goals = [g for g in goals if g.GoalType == goalType]
    
    return {
        "planId": planId,
        "goals": [model_to_dict(g) for g in goals],
        "total": len(goals)
    }

@router.get("/plans/{planId}/scenarios")
def get_plan_scenarios(
    planId: str = Path(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get plan scenarios"""
    service = FinancialPlanService()
    plan = service.get_by_id(db, planId)
    
    if not plan:
        raise HTTPException(status_code=404, detail=f"Financial plan {planId} not found")
    
    scenarios = service.get_plan_scenarios(db, planId)
    
    # Filter by status if specified
    if status:
        scenarios = [s for s in scenarios if s.Status == status]
    
    return {
        "planId": planId,
        "scenarios": [model_to_dict(s) for s in scenarios],
        "total": len(scenarios)
    }

@router.get("/plans/{planId}/cashflow")
def get_plan_cashflow(
    planId: str = Path(...),
    startYear: Optional[int] = Query(None),
    endYear: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get cashflow projections"""
    service = CashFlowService()
    cashflows = service.get_by_plan_id(db, planId, start_year=startYear, end_year=endYear)
    
    if not cashflows:
        raise HTTPException(status_code=404, detail=f"No cashflow data found for plan {planId}")
    
    return {
        "planId": planId,
        "cashFlowProjections": [model_to_dict(cf) for cf in cashflows],
        "total": len(cashflows),
        "startYear": startYear,
        "endYear": endYear
    }

@router.get("/plans/{planId}/networth")
def get_plan_networth(
    planId: str = Path(...),
    asOfDate: Optional[str] = Query(None),
    includeBreakdown: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get net worth analysis"""
    service = NetWorthService()
    
    if asOfDate:
        # Get net worth for specific date (simplified - would need more complex date filtering)
        networth_records = service.get_all(db, plan_id=planId, limit=10)
        networth = networth_records[0] if networth_records else None
    else:
        networth = service.get_latest_by_plan(db, planId)
    
    if not networth:
        raise HTTPException(status_code=404, detail=f"No net worth data found for plan {planId}")
    
    result = model_to_dict(networth)
    
    if includeBreakdown:
        result['breakdown'] = {
            "liquidAssets": float(networth.LiquidAssets) if networth.LiquidAssets else 0,
            "investedAssets": float(networth.InvestedAssets) if networth.InvestedAssets else 0,
            "useAssets": float(networth.UseAssets) if networth.UseAssets else 0,
            "totalAssets": float(networth.TotalAssets) if networth.TotalAssets else 0,
            "totalLiabilities": float(networth.TotalLiabilities) if networth.TotalLiabilities else 0,
            "netWorth": float(networth.NetWorth) if networth.NetWorth else 0
        }
    
    return result

@router.get("/goals")
def get_goals(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    goalType: Optional[str] = Query(None),
    planId: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all goals"""
    service = GoalService()
    skip = (page - 1) * pageSize
    
    goals = service.get_all(
        db, skip=skip, limit=pageSize, 
        client_id=clientId, plan_id=planId, 
        goal_type=goalType, status=status
    )
    
    # Count total for pagination
    total_goals = service.get_all(db, client_id=clientId, plan_id=planId, goal_type=goalType, status=status)
    total = len(total_goals)
    
    return {
        "goals": [model_to_dict(goal) for goal in goals],
        "total": total,
        "page": page,
        "pageSize": len(goals),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/goals/{goalId}")
def get_goal(
    goalId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific goal"""
    service = GoalService()
    goal = service.get_by_id(db, goalId)
    
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal {goalId} not found")
    
    result = model_to_dict(goal)
    
    # Add calculated fields
    if goal.TargetAmount and goal.CurrentValue:
        funding_percentage = (float(goal.CurrentValue) / float(goal.TargetAmount)) * 100
        result['calculatedFundingPercentage'] = round(funding_percentage, 2)
    
    if goal.TargetDate and goal.CurrentValue and goal.MonthlyContribution:
        # Simple projection calculation
        months_remaining = (goal.TargetDate.year - datetime.now().year) * 12
        months_remaining += (goal.TargetDate.month - datetime.now().month)
        if months_remaining > 0:
            projected_value = float(goal.CurrentValue) + (float(goal.MonthlyContribution) * months_remaining)
            result['projectedCompletion'] = round(projected_value, 2)
    
    return result

@router.get("/scenarios")
def get_scenarios(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    planId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    scenarioType: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all scenarios with pagination"""
    service = ScenarioService()
    skip = (page - 1) * pageSize
    
    # Get scenarios with filters
    scenarios = service.get_all(
        db,
        skip=skip,
        limit=pageSize,
        plan_id=planId,
        status=status,
        scenario_type=scenarioType
    )
    
    # Count total for pagination
    all_scenarios = service.get_all(
        db,
        plan_id=planId,
        status=status,
        scenario_type=scenarioType
    )
    total = len(all_scenarios)
    
    return {
        "scenarios": [model_to_dict(scenario) for scenario in scenarios],
        "total": total,
        "page": page,
        "pageSize": len(scenarios),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/scenarios/{scenarioId}")
def get_scenario(
    scenarioId: str = Path(...),
    includeResults: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get specific scenario"""
    service = ScenarioService()
    scenario = service.get_by_id(db, scenarioId)
    
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenarioId} not found")
    
    result = model_to_dict(scenario)
    
    if includeResults and scenario.Results:
        # Results are stored as JSON in the database
        result['detailedResults'] = scenario.Results
    
    return result

# ============================================================================
# CASH FLOW & BUDGET ENDPOINTS
# ============================================================================

@router.get("/cashflow")
def get_all_cashflow(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    planId: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """List all cashflow projections with pagination"""
    service = CashFlowService()
    skip = (page - 1) * pageSize
    
    # Get cashflows with filters
    cashflows = service.get_all(
        db,
        skip=skip,
        limit=pageSize,
        plan_id=planId,
        year=year
    )
    
    # Count total for pagination
    all_cashflows = service.get_all(
        db,
        plan_id=planId,
        year=year
    )
    total = len(all_cashflows)
    
    return {
        "cashflow": [model_to_dict(cf) for cf in cashflows],
        "total": total,
        "page": page,
        "pageSize": len(cashflows),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/cashflow/{planId}")
def get_cashflow_projections(
    planId: str = Path(...),
    years: Optional[int] = Query(30),
    startYear: Optional[int] = Query(None),
    endYear: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get cash flow projections"""
    service = CashFlowService()
    
    # Set default start/end years if not provided
    current_year = datetime.now().year
    if not startYear:
        startYear = current_year
    if not endYear:
        endYear = startYear + (years - 1) if years else current_year + 30
    
    cashflows = service.get_by_plan_id(db, planId, start_year=startYear, end_year=endYear)
    
    return {
        "planId": planId,
        "projections": [model_to_dict(cf) for cf in cashflows],
        "startYear": startYear,
        "endYear": endYear,
        "totalYears": len(set(cf.Year for cf in cashflows)) if cashflows else 0
    }

@router.get("/cashflow/{planId}/analysis")
def get_cashflow_analysis(
    planId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get cash flow analysis"""
    service = CashFlowService()
    analysis = service.get_cashflow_analysis(db, planId)
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No cashflow analysis available for plan {planId}")
    
    return analysis

@router.get("/income")
def get_income_sources(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    clientId: Optional[str] = Query(None),
    incomeType: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all income sources"""
    # Note: This would typically require a separate Income model
    # For now, return placeholder structure that could be extended
    return {
        "income": [],
        "total": 0,
        "page": page,
        "pageSize": 0,
        "totalPages": 0,
        "note": "Income tracking would require additional Income model implementation"
    }

@router.get("/income/{incomeId}")
def get_income_source(
    incomeId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific income"""
    # Placeholder - would need Income model
    raise HTTPException(status_code=404, detail="Income tracking not yet implemented")

@router.get("/expenses")
def get_expenses(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    clientId: Optional[str] = Query(None),
    expenseType: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all expenses"""
    # Note: This would typically require a separate Expense model
    # For now, return placeholder structure that could be extended
    return {
        "expenses": [],
        "total": 0,
        "page": page,
        "pageSize": 0,
        "totalPages": 0,
        "note": "Expense tracking would require additional Expense model implementation"
    }

@router.get("/expenses/{expenseId}")
def get_expense(
    expenseId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific expense"""
    # Placeholder - would need Expense model
    raise HTTPException(status_code=404, detail="Expense tracking not yet implemented")

@router.get("/budget/{clientId}")
def get_client_budget(
    clientId: str = Path(...),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get client budget"""
    # Placeholder - would need Budget model
    return {
        "clientId": clientId,
        "year": year or datetime.now().year,
        "budget": {},
        "note": "Budget tracking would require additional Budget model implementation"
    }

# ============================================================================
# NET WORTH ENDPOINTS
# ============================================================================

@router.get("/networth")
def get_all_networth(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    planId: Optional[str] = Query(None),
    householdId: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all net worth records with pagination"""
    service = NetWorthService()
    skip = (page - 1) * pageSize
    
    # Get networth records with filters
    networth_records = service.get_all(
        db,
        skip=skip,
        limit=pageSize,
        plan_id=planId,
        household_id=householdId
    )
    
    # Count total for pagination
    all_networth = service.get_all(
        db,
        plan_id=planId,
        household_id=householdId
    )
    total = len(all_networth)
    
    return {
        "networth": [model_to_dict(nw) for nw in networth_records],
        "total": total,
        "page": page,
        "pageSize": len(networth_records),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics/plans")
def get_planning_analytics(
    db: Session = Depends(get_db)
):
    """Get financial planning analytics"""
    plan_service = FinancialPlanService()
    goal_service = GoalService()
    
    # Get all plans and goals for analytics
    all_plans = plan_service.get_all(db, limit=1000)
    all_goals = goal_service.get_all(db, limit=5000)
    
    # Calculate status counts
    plan_status_counts = {}
    for plan in all_plans:
        status = plan.Status or "Unknown"
        plan_status_counts[status] = plan_status_counts.get(status, 0) + 1
    
    goal_status_counts = {}
    goal_type_counts = {}
    for goal in all_goals:
        status = goal.Status or "Unknown"
        goal_type = goal.GoalType or "Unknown"
        goal_status_counts[status] = goal_status_counts.get(status, 0) + 1
        goal_type_counts[goal_type] = goal_type_counts.get(goal_type, 0) + 1
    
    # Calculate average funding percentage
    funded_goals = [g for g in all_goals if g.FundingPercentage and float(g.FundingPercentage) > 0]
    avg_funding = sum(float(g.FundingPercentage) for g in funded_goals) / len(funded_goals) if funded_goals else 0
    
    analytics = {
        "total_plans": len(all_plans),
        "active_plans": plan_status_counts.get("Active", 0),
        "plans_by_status": plan_status_counts,
        "plans_by_type": {plan.PlanType: 1 for plan in all_plans},  # Simplified
        "total_goals": len(all_goals),
        "goals_on_track": goal_status_counts.get("OnTrack", 0),
        "goals_off_track": goal_status_counts.get("OffTrack", 0),
        "goals_by_status": goal_status_counts,
        "goals_by_type": goal_type_counts,
        "average_funding_percentage": round(avg_funding, 2)
    }
    
    return analytics

@router.get("/analytics/cashflow")
def get_cashflow_analytics(
    db: Session = Depends(get_db)
):
    """Get cash flow analytics"""
    service = CashFlowService()
    
    # Get all cashflows for analytics
    all_cashflows = service.get_all(db, limit=5000)
    
    if not all_cashflows:
        return {
            "total_cashflow_records": 0,
            "note": "No cashflow data available"
        }
    
    total_income = sum(float(cf.TotalIncome) if cf.TotalIncome else 0 for cf in all_cashflows)
    total_expenses = sum(float(cf.TotalExpenses) if cf.TotalExpenses else 0 for cf in all_cashflows)
    
    analytics = {
        "total_cashflow_records": len(all_cashflows),
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cashflow": total_income - total_expenses,
        "average_monthly_income": total_income / len(all_cashflows) if all_cashflows else 0,
        "average_monthly_expenses": total_expenses / len(all_cashflows) if all_cashflows else 0,
        "years_covered": len(set(cf.Year for cf in all_cashflows)),
        "plans_with_cashflow": len(set(cf.PlanID for cf in all_cashflows))
    }
    
    return analytics
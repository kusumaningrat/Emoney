from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/plans", tags=["Financial Planning"])
def get_client_plans(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """List all plans for a client"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FinancialPlan", db)
    return service.get_plans_by_client_id(client_id)

@router.get("/clients/{client_id}/plans/{plan_id}", tags=["Financial Planning"])
def get_plan(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get specific plan"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FinancialPlan", db)
    return service.get_plan_by_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/goals", tags=["Financial Planning"])
def get_plan_goals(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan goals"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Goal", db)
    return service.get_goals_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/scenarios", tags=["Financial Planning"])
def get_plan_scenarios(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan scenarios"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Scenario", db)
    return service.get_scenarios_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/cash-flows", tags=["Financial Planning"])
def get_plan_cashflows(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan cash flows"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("CashFlow", db)
    return service.get_cashflows_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/monte-carlo", tags=["Financial Planning"])
def get_plan_monte_carlo(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get Monte Carlo probability of success"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("MonteCarlo", db)
    return service.get_monte_carlo_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/projection", tags=["Financial Planning"])
def get_plan_projection(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan projections"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Projection", db)
    return service.get_projection_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/plans/{plan_id}/net-worth", tags=["Financial Planning"])
def get_client_net_worth(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client net worth"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("NetWorth", db)
    return service.get_net_worth_by_plan_id(client_id, plan_id)
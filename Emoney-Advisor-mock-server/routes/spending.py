from fastapi import APIRouter, Depends, Header, Query
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

router = APIRouter()

@router.get("/clients/{client_id}/spending", tags=["Spending & Budget Management"])
def get_client_spending(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client spending data"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Spending", db)
    return service.get_spending_by_client_id(client_id)

@router.get("/clients/{client_id}/budgets", tags=["Spending & Budget Management"])
def get_client_budgets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client budgets"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Budget", db)
    return service.get_budgets_by_client_id(client_id)

@router.get("/clients/{client_id}/income", tags=["Spending & Budget Management"])
def get_client_income(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client income"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Income", db)
    return service.get_income_by_client_id(client_id)

@router.get("/clients/{client_id}/plans/{plan_id}/income", tags=["Spending & Budget Management"])
def get_plan_income(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan income"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Income", db)
    return service.get_income_by_plan_id(client_id, plan_id)

@router.get("/clients/{client_id}/expenses", tags=["Spending & Budget Management"])
def get_client_expenses(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get client expenses"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Expense", db)
    return service.get_expenses_by_client_id(client_id)

@router.get("/clients/{client_id}/plans/{plan_id}/expenses", tags=["Spending & Budget Management"])
def get_plan_expenses(
    client_id: str,
    plan_id: str,
    is_goal: Optional[bool] = Query(None, description="Filter expenses by goal flag"),
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get plan expenses (includes goals when isGoal=true)"""
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Expense", db)
    return service.get_expenses_by_plan_id(client_id, plan_id, is_goal)
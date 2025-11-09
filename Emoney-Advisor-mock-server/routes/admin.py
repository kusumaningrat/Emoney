from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import importlib

from database import get_db, SessionLocal, Base, engine
from auth.dependencies import verify_api_key
from models.users import User, Firm

# Import the main seeder if available
try:
    from seeders.main_seeder import seed_all_data
except ImportError:
    print("Warning: main_seeder module not available")
    seed_all_data = None

router = APIRouter()

def ensure_system_user():
    """Ensure system user exists before seeding"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id='system').first()
        if existing:
            print("✓ System user already exists")
            return
        
        print("Creating system user...")
        
        # Get first firm or create a system firm with unique ID
        firm = db.query(Firm).first()
        if not firm:
            print("Creating system firm...")
            firm = Firm(
                id='firm-system',  # Use unique ID to avoid conflicts with seeder
                name='System Firm',
                email='contact@system.internal',
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(firm)
            db.flush()
        
        system_user = User(
            id='system',
            firm_id=firm.id,
            email='system@internal.app',
            username='system',
            first_name='System',
            last_name='User',
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(system_user)
        db.commit()
        print("✓ System user created successfully")
    except Exception as e:
        print(f"Error creating system user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@router.post("/seed", response_model=Dict[str, Any], tags=["Admin"])
async def seed_database(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Seed the database with mock data for all entities.
    
    This endpoint will create sample data for:
    - Firms, Users, Roles, and Permissions
    - Clients, Spouses, and Households
    - Financial Plans, Goals, and Projections
    - Accounts, Liabilities, and Investments
    - Assets, Asset Classes, and Holdings
    - Income Sources and Expenses
    - Estate Plans, Wills, Trusts, and Beneficiaries
    - Retirement Plans, Pensions, and Social Security
    - Insurance Plans, Policies, and Coverage
    - Tax Plans, Brackets, Deductions, and Credits
    - Documents, Notes, Tasks, and Alerts
    
    Warning: This will reset any existing data. Use with caution.
    """
    # Verify API credentials
    verify_api_key(x_api_key, x_api_secret)
    
    # CRITICAL: Ensure system user exists before seeding
    try:
        ensure_system_user()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create system user: {str(e)}"
        )
    
    try:
        # Call the main seeder function if available
        if seed_all_data:
            result = seed_all_data(db)
            
            if result.get("status") == "error":
                raise HTTPException(
                    status_code=500,
                    detail=result.get("message", "Unknown seeding error")
                )
            
            return result
        else:
            # Fallback if main seeder is not available
            return {
                "status": "warning",
                "message": "Main seeder not available. Please implement seeders.main_seeder.seed_all_data()",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed database: {str(e)}"
        )

@router.post("/reset", response_model=Dict[str, Any], tags=["Admin"])
async def reset_database(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Reset the database by dropping and recreating all tables.
    Warning: This will delete all data. Use with caution.
    """
    # Verify API credentials
    verify_api_key(x_api_key, x_api_secret)
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        
        # After reset, ensure system user is recreated
        try:
            ensure_system_user()
        except Exception as e:
            print(f"Warning: Could not recreate system user after reset: {e}")
        
        return {
            "status": "success",
            "message": "Database reset successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any], tags=["Admin"])
async def get_database_status(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get database status information including entity counts.
    """
    # Verify API credentials
    verify_api_key(x_api_key, x_api_secret)
    
    try:
        # Function to safely count models
        def safe_model_count(module_name, model_name):
            try:
                module = importlib.import_module(f"models.{module_name}")
                if hasattr(module, model_name):
                    model = getattr(module, model_name)
                    return db.query(model).count()
            except (ImportError, AttributeError, Exception) as e:
                print(f"Warning: Could not count {module_name}.{model_name}: {e}")
            return 0
        
        # Collect entity counts
        status = {
            "database": {
                "status": "Connected",
                "engine": str(engine.url).split("@")[-1] if "@" in str(engine.url) else str(engine.url)
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity_counts": {
                # User Management
                "firms": safe_model_count("users", "Firm"),
                "users": safe_model_count("users", "User"),
                "roles": safe_model_count("users", "Role"),
                "permissions": safe_model_count("users", "Permission"),
                "advisors": safe_model_count("users", "Advisor"),
                
                # Client Management
                "clients": safe_model_count("clients", "Client"),
                "spouses": safe_model_count("clients", "Spouse"),
                "households": safe_model_count("clients", "Household"),
                "contacts": safe_model_count("clients", "Contact"),
                "relationships": safe_model_count("clients", "Relationship"),
                
                # Financial Planning
                "financial_plans": safe_model_count("financial", "FinancialPlan"),
                "goals": safe_model_count("financial", "Goal"),
                "monte_carlo_analyses": safe_model_count("financial", "MonteCarlo"),
                "projections": safe_model_count("financial", "Projection"),
                "scenarios": safe_model_count("financial", "Scenario"),
                "cash_flows": safe_model_count("financial", "CashFlow"),
                
                # Account Management
                "accounts": safe_model_count("accounts", "Account"),
                "liabilities": safe_model_count("accounts", "Liability"),
                "account_types": safe_model_count("accounts", "AccountTypeModel"),
                "investments": safe_model_count("accounts", "Investment"),
                
                # Asset Management
                "assets": safe_model_count("assets", "Asset"),
                "asset_classes": safe_model_count("assets", "AssetClass"),
                "allocations": safe_model_count("assets", "Allocation"),
                "securities": safe_model_count("assets", "Security"),
                "holdings": safe_model_count("assets", "Holding"),
                
                # Spending Management
                "spending_records": safe_model_count("spending", "Spending"),
                "budgets": safe_model_count("spending", "Budget"),
                "income_sources": safe_model_count("spending", "Income"),
                "expenses": safe_model_count("spending", "Expense"),
                "budget_categories": safe_model_count("spending", "BudgetCategory"),
                
                # Document Management
                "file_types": safe_model_count("documents", "FileType"),
                "vault_documents": safe_model_count("documents", "VaultDocument"),
                "attachments": safe_model_count("documents", "Attachment"),
                "notes": safe_model_count("documents", "Note"),
                "tasks": safe_model_count("documents", "Task"),
                "alerts": safe_model_count("documents", "Alert"),
                
                # Estate Planning
                "estates": safe_model_count("estate", "Estate"),
                "wills": safe_model_count("estate", "Will"),
                "trusts": safe_model_count("estate", "Trust"),
                "beneficiaries": safe_model_count("estate", "Beneficiary"),
                
                # Retirement Planning
                "retirement_plans": safe_model_count("retirement", "RetirementPlan"),
                "pensions": safe_model_count("retirement", "Pension"),
                "social_security": safe_model_count("retirement", "SocialSecurity"),
                "rmds": safe_model_count("retirement", "RMD"),
                
                # Insurance Planning
                "insurances": safe_model_count("insurance", "Insurance"),
                "insurance_policies": safe_model_count("insurance", "InsurancePolicy"),
                "coverages": safe_model_count("insurance", "Coverage"),
                "premiums": safe_model_count("insurance", "Premium"),
                
                # Tax Planning
                "tax_plans": safe_model_count("tax", "TaxPlan"),
                "tax_brackets": safe_model_count("tax", "TaxBracket"),
                "deductions": safe_model_count("tax", "Deduction"),
                "credits": safe_model_count("tax", "Credit")
            }
        }
        
        # Calculate total entities
        non_zero_counts = [count for count in status["entity_counts"].values() if count > 0]
        status["entity_counts"]["total_entities"] = sum(non_zero_counts)
        status["entity_counts"]["total_entity_types"] = len(non_zero_counts)
        
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database status: {str(e)}"
        )
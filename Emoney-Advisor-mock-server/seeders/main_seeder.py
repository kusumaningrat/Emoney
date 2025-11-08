# seeders/main_seeder.py

from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import time
import importlib

from database import SessionLocal, Base, engine


import os, sys

# Force Python to recognize the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

print(f"[Seeder] Using ROOT_DIR={ROOT_DIR}")


# Function to safely import a module
def safe_import(module_name, attr_names=None):
    """Safely import a module and optionally specific attributes"""
    try:
        module = importlib.import_module(module_name)
        if attr_names:
            return {attr: getattr(module, attr) for attr in attr_names if hasattr(module, attr)}
        return module
    except ImportError:
        print(f"Warning: Module {module_name} could not be imported")
        return None

# Function to safely get count from a model
def safe_count(db, model_class):
    """Safely get count from a model class"""
    if model_class:
        try:
            return db.query(model_class).count()
        except Exception as e:
            print(f"Warning: Could not get count for {model_class.__name__}: {e}")
    return 0

# Safely import core modules
users = safe_import('models.users')
clients = safe_import('models.clients')
financial = safe_import('models.financial') 
accounts = safe_import('models.accounts')
assets = safe_import('models.assets')
spending = safe_import('models.spending')
document = safe_import('models.document')
estate = safe_import('models.estate')
retirement = safe_import('models.retirement')
insurance = safe_import('models.insurance')
tax = safe_import('models.tax')

# Safely import all seeders
users_seeder = safe_import('seeders.users_seeder')
client_seeder = safe_import('seeders.client_seeder')
financial_plans_seeder = safe_import('seeders.financial_plans_seeder')
account_seeder = safe_import('seeders.account_seeder')
asset_seeder = safe_import('seeders.asset_seeder')
spending_seeder = safe_import('seeders.spending_seeder')
document_seeder = safe_import('seeders.document_seeder')
estate_seeder = safe_import('seeders.estate_seeder')
retirement_seeder = safe_import('seeders.retirement_seeder')
insurance_seeder = safe_import('seeders.insurance_seeder')
tax_seeder = safe_import('seeders.tax_seeder')


def create_database_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Database tables created successfully!")

def seed_all_data(db: Session = None) -> Dict[str, Any]:
    """
    Main function to seed all data in the correct order.
    Returns a summary of the seeded data.
    """
    if db is None:
        db = SessionLocal()
    
    start_time = time.time()
    results = {"status": "success", "message": "Database seeded successfully with all data", "details": {}}
    
    try:
        # Step 1: Create database tables
        create_database_tables()
        
        # Step 2: Seed user data (firms, users, roles, permissions)
        print("\n===== Step 2: Seeding User Data =====")
        if users_seeder and hasattr(users_seeder, 'seed_firms'):
            users_seeder.seed_firms(db)
            users_seeder.seed_users(db)
            print("User data seeded successfully")
        else:
            print("Users seeder not available, skipping...")
        
        # Step 3: Seed client data
        print("\n===== Step 3: Seeding Client Data =====")
        if client_seeder and hasattr(client_seeder, 'seed_clients'):
            client_result = client_seeder.seed_clients()
        else:
            print("Client seeder not available, skipping...")
        
        # Step 4: Seed financial plans
        print("\n===== Step 4: Seeding Financial Plans =====")
        if financial_plans_seeder and hasattr(financial_plans_seeder, 'seed_financial_plans'):
            financial_result = financial_plans_seeder.seed_financial_plans()
        else:
            print("Financial plans seeder not available, skipping...")
        
        # Step 5: Seed account data
        print("\n===== Step 5: Seeding Account Data =====")
        if account_seeder and hasattr(account_seeder, 'seed_account_data'):
            account_result = account_seeder.seed_account_data()
        else:
            print("Account seeder not available, skipping...")
        
        # Step 6: Seed asset data
        print("\n===== Step 6: Seeding Asset Data =====")
        if asset_seeder and hasattr(asset_seeder, 'seed_asset_data'):
            asset_result = asset_seeder.seed_asset_data()
        else:
            print("Asset seeder not available, skipping...")
        
        # Step 7: Seed spending data
        print("\n===== Step 7: Seeding Spending Data =====")
        if spending_seeder and hasattr(spending_seeder, 'seed_spending_data'):
            spending_result = spending_seeder.seed_spending_data()
        else:
            print("Spending seeder not available, skipping...")
        
        # Step 8: Seed estate planning data
        print("\n===== Step 8: Seeding Estate Planning Data =====")
        if estate_seeder and hasattr(estate_seeder, 'seed_estate_planning'):
            estate_result = estate_seeder.seed_estate_planning()
        else:
            print("Estate planning seeder not available, skipping...")
        
        # Step 9: Seed retirement planning data
        print("\n===== Step 9: Seeding Retirement Planning Data =====")
        if retirement_seeder and hasattr(retirement_seeder, 'seed_retirement_data'):
            retirement_result = retirement_seeder.seed_retirement_data()
        else:
            print("Retirement seeder not available, skipping...")
        
        # Step 10: Seed insurance planning data
        print("\n===== Step 10: Seeding Insurance Planning Data =====")
        if insurance_seeder and hasattr(insurance_seeder, 'seed_insurance_data'):
            insurance_result = insurance_seeder.seed_insurance_data()
        else:
            print("Insurance seeder not available, skipping...")
        
        # Step 11: Seed tax planning data
        print("\n===== Step 11: Seeding Tax Planning Data =====")
        if tax_seeder and hasattr(tax_seeder, 'seed_tax_data'):
            tax_result = tax_seeder.seed_tax_data()
        else:
            print("Tax seeder not available, skipping...")
        
        # Step 12: Seed document data
        print("\n===== Step 12: Seeding Document Data =====")
        if document_seeder and hasattr(document_seeder, 'seed_document_data'):
            document_result = document_seeder.seed_document_data()
        else:
            print("Document seeder not available, skipping...")
        
        # Collect stats for all entities
        print("\n===== Collecting Seed Results =====")
        
        # User & Access Management
        if users:
            results["details"]["firms"] = safe_count(db, getattr(users, 'Firm', None))
            results["details"]["users"] = safe_count(db, getattr(users, 'User', None))
            results["details"]["roles"] = safe_count(db, getattr(users, 'Role', None))
            results["details"]["permissions"] = safe_count(db, getattr(users, 'Permission', None))
            results["details"]["advisors"] = safe_count(db, getattr(users, 'Advisor', None))
        
        # Client & Relationship Management
        if clients:
            results["details"]["clients"] = safe_count(db, getattr(clients, 'Client', None))
            results["details"]["spouses"] = safe_count(db, getattr(clients, 'Spouse', None))
            results["details"]["households"] = safe_count(db, getattr(clients, 'Household', None))
            results["details"]["contacts"] = safe_count(db, getattr(clients, 'Contact', None))
            results["details"]["relationships"] = safe_count(db, getattr(clients, 'Relationship', None))
        
        # Financial Planning
        if financial:
            results["details"]["financial_plans"] = safe_count(db, getattr(financial, 'FinancialPlan', None))
            results["details"]["goals"] = safe_count(db, getattr(financial, 'Goal', None))
            results["details"]["monte_carlo_analyses"] = safe_count(db, getattr(financial, 'MonteCarlo', None))
            results["details"]["projections"] = safe_count(db, getattr(financial, 'Projection', None))
            results["details"]["scenarios"] = safe_count(db, getattr(financial, 'Scenario', None))
            results["details"]["cash_flows"] = safe_count(db, getattr(financial, 'CashFlow', None))
        
        # Account Management
        if accounts:
            results["details"]["accounts"] = safe_count(db, getattr(accounts, 'Account', None))
            results["details"]["liabilities"] = safe_count(db, getattr(accounts, 'Liability', None))
            results["details"]["account_types"] = safe_count(db, getattr(accounts, 'AccountTypeModel', None))
            results["details"]["investments"] = safe_count(db, getattr(accounts, 'Investment', None))
        
        # Asset Management
        if assets:
            results["details"]["assets"] = safe_count(db, getattr(assets, 'Asset', None))
            results["details"]["asset_classes"] = safe_count(db, getattr(assets, 'AssetClass', None))
            results["details"]["allocations"] = safe_count(db, getattr(assets, 'Allocation', None))
            results["details"]["securities"] = safe_count(db, getattr(assets, 'Security', None))
            results["details"]["holdings"] = safe_count(db, getattr(assets, 'Holding', None))
        
        # Spending Management
        if spending:
            results["details"]["spending_records"] = safe_count(db, getattr(spending, 'Spending', None))
            results["details"]["budgets"] = safe_count(db, getattr(spending, 'Budget', None))
            results["details"]["income_sources"] = safe_count(db, getattr(spending, 'Income', None))
            results["details"]["expenses"] = safe_count(db, getattr(spending, 'Expense', None))
            results["details"]["budget_categories"] = safe_count(db, getattr(spending, 'BudgetCategory', None))
        
        # Document Management
        if document:
            results["details"]["file_types"] = safe_count(db, getattr(document, 'FileType', None))
            results["details"]["vault_documents"] = safe_count(db, getattr(document, 'VaultDocument', None))
            results["details"]["attachments"] = safe_count(db, getattr(document, 'Attachment', None))
            results["details"]["notes"] = safe_count(db, getattr(document, 'Note', None))
            results["details"]["tasks"] = safe_count(db, getattr(document, 'Task', None))
            results["details"]["alerts"] = safe_count(db, getattr(document, 'Alert', None))
        
        # Estate Planning
        if estate:
            results["details"]["estates"] = safe_count(db, getattr(estate, 'Estate', None))
            results["details"]["wills"] = safe_count(db, getattr(estate, 'Will', None))
            results["details"]["trusts"] = safe_count(db, getattr(estate, 'Trust', None))
            results["details"]["beneficiaries"] = safe_count(db, getattr(estate, 'Beneficiary', None))
        
        # Retirement Planning
        if retirement:
            results["details"]["retirement_plans"] = safe_count(db, getattr(retirement, 'RetirementPlan', None))
            results["details"]["pensions"] = safe_count(db, getattr(retirement, 'Pension', None))
            results["details"]["social_security"] = safe_count(db, getattr(retirement, 'SocialSecurity', None))
            results["details"]["rmds"] = safe_count(db, getattr(retirement, 'RMD', None))
        
        # Insurance Planning
        if insurance:
            results["details"]["insurances"] = safe_count(db, getattr(insurance, 'Insurance', None))
            results["details"]["insurance_policies"] = safe_count(db, getattr(insurance, 'InsurancePolicy', None))
            results["details"]["coverages"] = safe_count(db, getattr(insurance, 'Coverage', None))
            results["details"]["premiums"] = safe_count(db, getattr(insurance, 'Premium', None))
        
        # Tax Planning
        if tax:
            results["details"]["tax_plans"] = safe_count(db, getattr(tax, 'TaxPlan', None))
            results["details"]["tax_brackets"] = safe_count(db, getattr(tax, 'TaxBracket', None))
            results["details"]["deductions"] = safe_count(db, getattr(tax, 'Deduction', None))
            results["details"]["credits"] = safe_count(db, getattr(tax, 'Credit', None))
        
        # Set timestamp
        results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        
        # Calculate execution time
        end_time = time.time()
        results["execution_time"] = round(end_time - start_time, 2)
        
        print(f"\n===== Seeding completed successfully in {results['execution_time']} seconds =====")
        print(json.dumps(results, indent=2))
        
        return results
        
    except Exception as e:
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        
        results = {
            "status": "error",
            "message": f"Error seeding database: {str(e)}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "execution_time": execution_time
        }
        
        print(f"\n===== Seeding failed after {execution_time} seconds =====")
        print(json.dumps(results, indent=2))
        
        db.rollback()
        return results
    finally:
        db.close()

# This will allow importing the services for Swagger docs
# Map entity names to their model classes for API service registration
entity_models = {}

# Safely add models to entity_models
def safe_add_models(module, model_names):
    if module:
        for name in model_names:
            if hasattr(module, name):
                entity_models[name] = getattr(module, name)

# Add models from each module
if users:
    safe_add_models(users, ['User', 'Role', 'Permission', 'Firm', 'Logon', 'Workspace', 'Advisor'])
if clients:
    safe_add_models(clients, ['Client', 'Spouse', 'Household', 'HouseholdMember', 'Contact', 'Relationship'])
if financial:
    safe_add_models(financial, ['FinancialPlan', 'Goal', 'MonteCarlo', 'Projection', 'CashFlow', 'Scenario'])
if accounts:
    safe_add_models(accounts, ['Account', 'AccountTypeModel', 'Investment', 'Liability'])
if assets:
    safe_add_models(assets, ['Asset', 'AssetClass', 'Allocation', 'Security', 'Holding'])
if spending:
    safe_add_models(spending, ['Spending', 'Budget', 'Income', 'Expense', 'BudgetCategory'])
if document:
    safe_add_models(document, ['FileType', 'VaultDocument', 'Attachment', 'Note', 'Task', 'Alert'])
if estate:
    safe_add_models(estate, ['Estate', 'Will', 'Trust', 'Beneficiary'])
if retirement:
    safe_add_models(retirement, ['RetirementPlan', 'Pension', 'SocialSecurity', 'RMD'])
if insurance:
    safe_add_models(insurance, ['Insurance', 'InsurancePolicy', 'Coverage', 'Premium'])
if tax:
    safe_add_models(tax, ['TaxPlan', 'TaxBracket', 'Deduction', 'Credit'])

# Endpoint schemas for Swagger documentation
entity_endpoints = {
    # Client & Relationship Management
    "clients": {
        "description": "Client information endpoints",
        "endpoints": [
            "/clients", 
            "/clients/{client_id}",
            "/clients/{client_id}/spouse",
            "/clients/{client_id}/household",
            "/clients/{client_id}/relationships"
        ]
    },
    
    # Financial Planning
    "financial-planning": {
        "description": "Financial planning endpoints",
        "endpoints": [
            "/clients/{client_id}/plans",
            "/clients/{client_id}/plans/{plan_id}",
            "/clients/{client_id}/plans/{plan_id}/goals",
            "/clients/{client_id}/plans/{plan_id}/scenarios",
            "/clients/{client_id}/plans/{plan_id}/cash-flows"
        ]
    },
    
    # Add other endpoint groups as needed...
}

if __name__ == "__main__":
    seed_all_data()
# seeders/account_seeder.py

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
import json

from database import SessionLocal
from models.accounts import Account, Investment, Liability, AccountTypeModel
from models.clients import Client
from models.users import User
from models.assets import Security

# Initialize Faker
fake = Faker()

# Main function to seed all account data
def seed_account_data(db: Session = None):
    """Main function to seed all account management data in correct order."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_accounts = db.query(Account).count()
        if existing_accounts > 0:
            print("Account management data already seeded, skipping...")
            return
        
        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first required.")
            return
            
        # Get users
        users = db.query(User).all()
        if not users:
            print("No users found, seeding users first required.")
            return
            
        # 1. Create account types
        account_types = seed_account_types(db)
        db.commit()
            
        # 2. Create accounts first
        accounts = seed_accounts(db, clients, users)
        db.commit()
        
        # 3. Create securities first (before investments)
        securities = seed_securities(db, users)
        db.commit()
        
        # 4. Create investments for appropriate accounts
        seed_investments(db, accounts, securities, users)
        db.commit()
        
        # 5. Create liabilities
        seed_liabilities(db, clients, accounts, users)
        db.commit()
        
        print("Account management seeding complete!")
        return True
        
    except Exception as e:
        print(f"Error seeding account management data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_account_types(db: Session):
    """Create account type definitions."""
    print("Creating account types...")
    
    account_types = [
        {
            "id": generate_id("acct_type"),
            "name": "Checking Account",
            "description": "Standard checking account for everyday transactions",
            "category": "Asset",
            "tax_treatment": "Taxable",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Savings Account",
            "description": "Interest-earning savings account",
            "category": "Asset",
            "tax_treatment": "Taxable",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Brokerage Account",
            "description": "Standard investment account for securities",
            "category": "Asset",
            "tax_treatment": "Taxable",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Traditional IRA",
            "description": "Tax-deferred individual retirement account",
            "category": "Asset",
            "tax_treatment": "Tax-Deferred",
            "is_retirement": True,
            "is_qualified": True,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": {
                "annual": 6000,
                "catch_up": 1000,
                "catch_up_age": 50
            },
            "withdrawal_rules": {
                "early_withdrawal_age": 59.5,
                "rmd_age": 72,
                "early_withdrawal_penalty": 0.1
            }
        },
        {
            "id": generate_id("acct_type"),
            "name": "Roth IRA",
            "description": "Tax-free individual retirement account",
            "category": "Asset",
            "tax_treatment": "Tax-Free",
            "is_retirement": True,
            "is_qualified": True,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": {
                "annual": 6000,
                "catch_up": 1000,
                "catch_up_age": 50
            },
            "withdrawal_rules": {
                "early_withdrawal_age": 59.5,
                "rmd_required": False,
                "contribution_withdrawal": "Always tax-free",
                "earnings_withdrawal": "Tax-free after 5 years and age 59.5"
            }
        },
        {
            "id": generate_id("acct_type"),
            "name": "401(k)",
            "description": "Employer-sponsored retirement plan",
            "category": "Asset",
            "tax_treatment": "Tax-Deferred",
            "is_retirement": True,
            "is_qualified": True,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": {
                "annual": 19500,
                "catch_up": 6500,
                "catch_up_age": 50,
                "employer_contribution": "Varies"
            },
            "withdrawal_rules": {
                "early_withdrawal_age": 59.5,
                "rmd_age": 72,
                "early_withdrawal_penalty": 0.1,
                "loan_provisions": "May be available"
            }
        },
        {
            "id": generate_id("acct_type"),
            "name": "529 Plan",
            "description": "Tax-advantaged education savings plan",
            "category": "Asset",
            "tax_treatment": "Tax-Free for qualified education expenses",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": True,
            "is_education": True,
            "is_health": False,
            "contribution_limits": {
                "annual": "State dependent",
                "lifetime": "State dependent"
            },
            "withdrawal_rules": {
                "qualified_expenses": [
                    "Tuition", "Room & Board", "Books", "Supplies", "Equipment"
                ],
                "non_qualified_penalty": 0.1
            }
        },
        {
            "id": generate_id("acct_type"),
            "name": "HSA",
            "description": "Health Savings Account",
            "category": "Asset",
            "tax_treatment": "Triple tax advantage",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": True,
            "contribution_limits": {
                "annual_individual": 3550,
                "annual_family": 7100,
                "catch_up": 1000,
                "catch_up_age": 55
            },
            "withdrawal_rules": {
                "qualified_expenses": "Medical expenses",
                "non_qualified_penalty": 0.2
            }
        },
        {
            "id": generate_id("acct_type"),
            "name": "Mortgage",
            "description": "Loan secured by real property",
            "category": "Liability",
            "tax_treatment": "Interest may be tax-deductible",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Auto Loan",
            "description": "Loan for vehicle purchase",
            "category": "Liability",
            "tax_treatment": "Not tax-deductible",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Credit Card",
            "description": "Revolving credit account",
            "category": "Liability",
            "tax_treatment": "Not tax-deductible",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": False,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        },
        {
            "id": generate_id("acct_type"),
            "name": "Student Loan",
            "description": "Loan for educational expenses",
            "category": "Liability",
            "tax_treatment": "Interest may be tax-deductible",
            "is_retirement": False,
            "is_qualified": False,
            "is_custodial": False,
            "is_education": True,
            "is_health": False,
            "contribution_limits": None,
            "withdrawal_rules": None
        }
    ]
    
    account_type_models = []
    
    # Create a random user for created_by/updated_by
    random_user = random.choice(db.query(User).all())
    
    for account_type in account_types:
        account_type["created_by"] = random_user.id
        account_type["updated_by"] = random_user.id
        account_type["created_at"] = datetime.utcnow()
        account_type["updated_at"] = datetime.utcnow()
        
        # Convert JSON fields to strings
        if account_type["contribution_limits"]:
            account_type["contribution_limits"] = json.dumps(account_type["contribution_limits"])
        if account_type["withdrawal_rules"]:
            account_type["withdrawal_rules"] = json.dumps(account_type["withdrawal_rules"])
        
        account_type_model = AccountTypeModel(**account_type)
        db.add(account_type_model)
        account_type_models.append(account_type_model)
    
    db.commit()
    print(f"Created {len(account_type_models)} account types!")
    return account_type_models

def seed_accounts(db: Session, clients: list, users: list) -> list:
    """Seed account data for clients."""
    print("Seeding account data...")
    
    accounts = []
    account_count = 0
    
    # Get account types from database
    account_types = db.query(AccountTypeModel).all()
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.8:
            continue
            
        # Select random creator/updater
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Determine number of accounts to create for this client (2-6)
        num_accounts = random.randint(2, 6)
        
        # Types of accounts to consider for this client
        available_account_types = [
            at for at in account_types if at.category == "Asset"
        ]
        
        # Ensure we have enough account types
        if len(available_account_types) < num_accounts:
            num_accounts = len(available_account_types)
        
        # Select random account types for this client
        selected_account_types = random.sample(available_account_types, num_accounts)
        
        for account_type in selected_account_types:
            # Create account
            account_id = generate_id("account")
            
            # Generate account name
            account_name = f"{client.last_name} {account_type.name}"
            
            # Generate institution based on account type
            if "IRA" in account_type.name or "401(k)" in account_type.name or "Brokerage" in account_type.name:
                institution = random.choice([
                    "Charles Schwab", "Fidelity", "Vanguard", "TD Ameritrade", 
                    "E*TRADE", "Merrill Lynch", "T. Rowe Price"
                ])
            elif "Checking" in account_type.name or "Savings" in account_type.name:
                institution = random.choice([
                    "Bank of America", "Chase", "Wells Fargo", "Citi", 
                    "US Bank", "PNC Bank", "Capital One"
                ])
            else:
                institution = random.choice([
                    "Charles Schwab", "Fidelity", "Vanguard", "TD Ameritrade", 
                    "Bank of America", "Chase", "Wells Fargo", "Citi"
                ])
            
            # Generate account number (masked)
            account_number = f"xxx-xx-{random.randint(1000, 9999)}"
            
            # Generate description
            descriptions = {
                "Checking Account": "Primary checking for daily expenses",
                "Savings Account": "Emergency fund and short-term savings",
                "Brokerage Account": "Taxable investment account",
                "Traditional IRA": "Tax-deferred retirement savings",
                "Roth IRA": "Tax-free retirement savings",
                "401(k)": f"Employer-sponsored retirement plan through {institution}",
                "529 Plan": "College savings for children",
                "HSA": "Health savings account for medical expenses"
            }
            description = descriptions.get(account_type.name, None)
            
            # Determine tax status
            tax_status = account_type.tax_treatment
            
            # Determine ownership type
            ownership = random.choice(["Individual", "Joint"])
            
            # Create account
            account = Account(
                id=account_id,
                client_id=client.id,
                name=account_name,
                description=description,
                institution=institution,
                account_number=account_number,
                type=account_type.name,
                ownership=ownership,
                tax_status=tax_status,
                is_external=random.random() < 0.2,  # 20% chance of being external
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(account)
            accounts.append(account)
            account_count += 1
    
    db.commit()
    print(f"Created {account_count} accounts for {len(set(a.client_id for a in accounts))} clients!")
    return accounts

def seed_securities(db: Session, users: list):
    """Create securities in the database."""
    print("Creating securities...")
    
    securities_data = [
        {"symbol": "AAPL", "name": "Apple Inc.", "type": "Stock"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "Stock"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "Stock"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "type": "Stock"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "type": "Stock"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "type": "Stock"},
        {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc. Class B", "type": "Stock"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "type": "Stock"},
        {"symbol": "V", "name": "Visa Inc. Class A", "type": "Stock"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "type": "Stock"},
        
        {"symbol": "VFIAX", "name": "Vanguard 500 Index Fund", "type": "Mutual Fund"},
        {"symbol": "VTSAX", "name": "Vanguard Total Stock Market Index Fund", "type": "Mutual Fund"},
        {"symbol": "VBTLX", "name": "Vanguard Total Bond Market Index Fund", "type": "Mutual Fund"},
        {"symbol": "VTIAX", "name": "Vanguard Total International Stock Index Fund", "type": "Mutual Fund"},
        {"symbol": "FXAIX", "name": "Fidelity 500 Index Fund", "type": "Mutual Fund"},
        
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "type": "ETF"},
        {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "type": "ETF"},
        {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "type": "ETF"},
        {"symbol": "QQQ", "name": "Invesco QQQ Trust", "type": "ETF"},
        {"symbol": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF", "type": "ETF"}
    ]
    
    db_securities = []
    for security_data in securities_data:
        # Check if security already exists
        existing = db.query(Security).filter_by(symbol=security_data["symbol"]).first()
        
        if not existing:
            creator = random.choice(users)
            
            # Generate random price based on security type
            if security_data["type"] == "Stock":
                price = random.uniform(50, 500)
            elif security_data["type"] == "ETF":
                price = random.uniform(30, 300)
            else:  # Mutual Fund
                price = random.uniform(10, 150)
            
            security = Security(
                id=generate_id("security"),
                symbol=security_data["symbol"],
                name=security_data["name"],
                type=security_data["type"],
                price=round(price, 2),
                price_date=date.today(),
                asset_class_id=None,  # Can be linked later if asset classes are seeded
                created_by=creator.id,
                updated_by=creator.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(security)
            db_securities.append(security)
    
    db.commit()
    print(f"Created {len(db_securities)} securities!")
    return db_securities

def seed_investments(db: Session, accounts: list, securities: list, users: list):
    """Create investments for investment/retirement accounts."""
    print("Creating account investments...")
    
    investment_count = 0
    
    # Define investment account types
    investment_account_types = ["Brokerage Account", "Traditional IRA", "Roth IRA", "401(k)", "529 Plan"]
    
    # Get only investment accounts
    investment_accounts = [a for a in accounts if a.type in investment_account_types]
    
    # Get all securities from database
    all_securities = db.query(Security).all()
    
    if not all_securities:
        print("No securities found in database!")
        return
    
    # Now create investments for each investment account
    for account in investment_accounts:
        # Select random user for creator/updater
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Determine number of investments (3-8)
        num_investments = random.randint(3, 8)
        
        # Select random securities for this account
        selected_securities = random.sample(all_securities, min(num_investments, len(all_securities)))
        
        # Generate allocation percentages that sum to 100%
        allocations = [random.randint(5, 30) for _ in range(len(selected_securities))]
        total_allocation = sum(allocations)
        normalized_allocations = [round(a / total_allocation * 100, 2) for a in allocations]
        
        # Adjust for rounding errors
        if sum(normalized_allocations) < 100:
            normalized_allocations[-1] += 100 - sum(normalized_allocations)
        elif sum(normalized_allocations) > 100:
            normalized_allocations[-1] -= sum(normalized_allocations) - 100
        
        # Assume a random account value between $10k and $500k
        account_value = random.uniform(10000, 500000)
        
        for i, security in enumerate(selected_securities):
            # Calculate this investment's allocation and value
            allocation_pct = normalized_allocations[i]
            market_value = account_value * (allocation_pct / 100)
            
            # Use the price from the security record
            current_price = security.price
            
            # Calculate shares based on value and price
            shares = round(market_value / current_price, 4)
            
            # Random purchase date between 1 and 10 years ago
            purchase_date = fake.date_between(start_date='-10y', end_date='-1y')
            
            # Calculate purchase price (slightly different from current price)
            price_change_factor = random.uniform(0.7, 1.3)
            purchase_price = round(current_price / price_change_factor, 2)
            
            # Calculate cost basis
            cost_basis = round(shares * purchase_price, 2)
            
            # Get asset class name from security type for display purposes
            asset_class = {
                "Stock": "Equity",
                "ETF": "Mixed",
                "Mutual Fund": "Mixed",
                "Bond": "Fixed Income"
            }.get(security.type, "Other")
            
            # Create investment
            investment_id = generate_id("invest")
            investment = Investment(
                id=investment_id,
                account_id=account.id,
                security_id=security.id,
                name=security.name,
                ticker=security.symbol,
                asset_class=asset_class,
                investment_type=security.type,
                shares=shares,
                purchase_price=purchase_price,
                current_price=current_price,
                purchase_date=purchase_date,
                cost_basis=cost_basis,
                market_value=market_value,
                allocation_percentage=allocation_pct,
                yield_rate=random.uniform(0, 0.05) if random.random() > 0.5 else None,
                is_core_position=random.random() < 0.3,
                notes=fake.sentence() if random.random() < 0.3 else None,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(investment)
            investment_count += 1
    
    db.commit()
    print(f"Created {investment_count} investments!")

def seed_liabilities(db: Session, clients: list, accounts: list, users: list):
    """Create liability records for clients."""
    print("Creating liability records...")
    
    liability_count = 0
    
    # Get liability account types
    liability_types = db.query(AccountTypeModel).filter(AccountTypeModel.category == "Liability").all()
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.7:
            continue
            
        # Select random creator/updater
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Determine number of liabilities for this client (0-4)
        num_liabilities = random.randint(0, 4)
        
        if num_liabilities == 0:
            continue
            
        # Select random liability types
        selected_liability_types = random.sample(liability_types, min(num_liabilities, len(liability_types)))
        
        # Get client's accounts for possible association
        client_accounts = [a for a in accounts if a.client_id == client.id]
        
        for liability_type in selected_liability_types:
            # Get a random account to associate with this liability (or None)
            account_id = random.choice(client_accounts).id if client_accounts and random.random() > 0.5 else None
            
            # Generate liability name
            liability_name = f"{client.last_name} {liability_type.name}"
            
            # Generate liability description
            description = None
            if liability_type.name == "Mortgage":
                description = random.choice([
                    "Primary residence mortgage", 
                    "Vacation home mortgage",
                    "Investment property mortgage"
                ])
            elif liability_type.name == "Auto Loan":
                description = f"Loan for {random.choice(['Toyota', 'Honda', 'Ford', 'Tesla', 'BMW', 'Mercedes'])}"
            elif liability_type.name == "Student Loan":
                description = random.choice([
                    "Undergraduate student loans",
                    "Graduate student loans",
                    "Medical school loans",
                    "Law school loans"
                ])
            
            # Generate balance amount based on liability type
            if liability_type.name == "Mortgage":
                original_balance = random.uniform(100000, 800000)
                balance = original_balance * random.uniform(0.5, 0.95)  # Partially paid off
                interest_rate = random.uniform(0.03, 0.06)
                payment_amount = (original_balance * interest_rate / 12) / (1 - (1 + interest_rate / 12) ** -360)
                payment_frequency = "Monthly"
                start_date = fake.date_between(start_date='-20y', end_date='-1y')
                end_date = date(start_date.year + 30, start_date.month, start_date.day)
            elif liability_type.name == "Auto Loan":
                original_balance = random.uniform(15000, 60000)
                balance = original_balance * random.uniform(0.3, 0.9)  # Partially paid off
                interest_rate = random.uniform(0.035, 0.075)
                payment_amount = (original_balance * interest_rate / 12) / (1 - (1 + interest_rate / 12) ** -60)
                payment_frequency = "Monthly"
                start_date = fake.date_between(start_date='-5y', end_date='-6m')
                end_date = date(start_date.year + 5, start_date.month, start_date.day)
            elif liability_type.name == "Student Loan":
                original_balance = random.uniform(20000, 150000)
                balance = original_balance * random.uniform(0.4, 1.0)  # Partially paid off or recently acquired
                interest_rate = random.uniform(0.04, 0.08)
                payment_amount = (original_balance * interest_rate / 12) / (1 - (1 + interest_rate / 12) ** -120)
                payment_frequency = "Monthly"
                start_date = fake.date_between(start_date='-15y', end_date='-1y')
                end_date = date(start_date.year + 10, start_date.month, start_date.day)
            elif liability_type.name == "Credit Card":
                original_balance = random.uniform(1000, 20000)
                balance = original_balance  # Usually reporting current balance
                interest_rate = random.uniform(0.14, 0.25)
                payment_amount = balance * 0.025  # Minimum payment
                payment_frequency = "Monthly"
                start_date = fake.date_between(start_date='-5y', end_date='-1m')
                end_date = None  # Revolving debt doesn't have a set end date
            else:
                original_balance = random.uniform(5000, 50000)
                balance = original_balance * random.uniform(0.5, 1.0)
                interest_rate = random.uniform(0.05, 0.12)
                payment_amount = (original_balance * interest_rate / 12) / (1 - (1 + interest_rate / 12) ** -60)
                payment_frequency = "Monthly"
                start_date = fake.date_between(start_date='-5y', end_date='-1y')
                end_date = date(start_date.year + 5, start_date.month, start_date.day)
            
            # Create liability
            liability_id = generate_id("liab")
            liability = Liability(
                id=liability_id,
                client_id=client.id,
                plan_id=None,  # Could link to a financial plan if needed
                name=liability_name,
                description=description,
                type=liability_type.name,
                balance=round(balance, 2),
                original_balance=round(original_balance, 2),
                interest_rate=interest_rate,
                payment_amount=round(payment_amount, 2),
                payment_frequency=payment_frequency,
                start_date=start_date,
                end_date=end_date,
                ownership=random.choice(["Individual", "Joint"]),
                account_id=account_id,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(liability)
            liability_count += 1
    
    db.commit()
    print(f"Created {liability_count} liabilities!")

if __name__ == "__main__":
    seed_account_data()
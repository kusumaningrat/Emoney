# seeders/spending_seeder.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta, date
from faker import Faker
from decimal import Decimal
import random
import uuid
import json

from database import SessionLocal
from models.spending import Spending, Budget, Income, Expense, BudgetCategory
from models.clients import Client
from models.users import User
from models.financial import FinancialPlan, Goal

# Initialize Faker
fake = Faker()

# Main function to seed all spending data
def seed_spending_data(db: Session = None):
    """Main function to seed all spending and budget management data in correct order."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_spending = db.query(Spending).count()
        if existing_spending > 0:
            print("Spending and budget data already seeded, skipping...")
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
            
        # Get financial plans and goals if available
        financial_plans = db.query(FinancialPlan).all()
        goals = db.query(Goal).all()
        
        # Create workspace_id for all records
        workspace_id = "workspace-" + uuid.uuid4().hex[:8]
            
        # 1. Create spending records
        spending_records = seed_spending_records(db, clients, users, workspace_id)
        db.commit()
            
        # 2. Create income sources
        income_sources = seed_income_sources(db, spending_records, financial_plans, users, workspace_id)
        db.commit()
            
        # 3. Create expenses
        expenses = seed_expenses(db, spending_records, financial_plans, goals, users, workspace_id)
        db.commit()
            
        # 4. Create budgets with categories
        budgets = seed_budgets(db, spending_records, users, workspace_id)
        db.commit()
        
        # 5. Update spending records with totals
        update_spending_records(db, spending_records)
        db.commit()
        
        print("Spending and budget management seeding complete!")
        return True
        
    except Exception as e:
        print(f"Error seeding spending and budget data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_spending_records(db: Session, clients: list, users: list, workspace_id: str):
    """Create spending records for clients."""
    print("Creating spending records...")
    
    spending_records = []
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.8:
            continue
            
        # Select random user for created_by/updated_by
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Initial spending record with empty totals (will be updated later)
        spending = Spending(
            id=generate_id("spending"),
            workspace_id=workspace_id,
            client_id=client.id,
            created_by=creator.id,
            updated_by=updater.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="Active",
            annual_income=0,
            annual_expenses=0,
            annual_savings=0,
            monthly_income=0,
            monthly_expenses=0,
            monthly_savings=0,
            savings_rate=0,
            expense_to_income_ratio=0,
            cash_flow_status="Unknown",
            last_update=date.today(),
            sync_status="Manual",
            expense_categories={},
            linked_accounts=[] if random.random() < 0.7 else [
                {
                    "account_id": generate_id("account"),  # This would be a real account ID in practice
                    "name": f"{random.choice(['Chase', 'Bank of America', 'Wells Fargo'])} {random.choice(['Checking', 'Credit Card'])}",
                    "sync_status": "Active"
                }
            ],
            analysis={
                "savings_trend": "Stable",
                "expense_breakdown": {},
                "income_breakdown": {},
                "recommendations": []
            },
            notes=fake.paragraph() if random.random() < 0.3 else None
        )
        
        db.add(spending)
        spending_records.append(spending)
    
    db.commit()
    print(f"Created {len(spending_records)} spending records!")
    return spending_records

def seed_income_sources(db: Session, spending_records: list, financial_plans: list, users: list, workspace_id: str):
    """Create income sources for spending records."""
    print("Creating income sources...")
    
    income_sources = []
    
    # Common income types
    income_types = [
        "Salary", "Bonus", "Commission", "Self-Employment", "Pension", 
        "Social Security", "Rental", "Dividend", "Interest", "Capital Gains", 
        "Alimony", "Child Support", "Royalties", "Business"
    ]
    
    # Frequency types
    frequency_types = ["Weekly", "Biweekly", "Monthly", "Quarterly", "Semi-Annual", "Annual"]
    
    for spending in spending_records:
        # Get client ID
        client_id = spending.client_id
        
        # Try to find a financial plan for this client
        client_plan = next((plan for plan in financial_plans if plan.client_id == client_id), None)
        
        # Select random user for created_by/updated_by
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Determine number of income sources (1-4)
        num_income_sources = random.randint(1, 4)
        
        # Always include primary income source (usually salary)
        primary_income_type = random.choice(["Salary", "Self-Employment", "Business"])
        primary_income_freq = "Biweekly" if primary_income_type == "Salary" else random.choice(["Monthly", "Biweekly"])
        
        # Determine primary income amount based on type
        if primary_income_type == "Salary":
            annual_amount = random.uniform(50000, 200000)
        elif primary_income_type == "Self-Employment":
            annual_amount = random.uniform(40000, 250000)
        else:  # Business
            annual_amount = random.uniform(75000, 350000)
            
        # Calculate derived amounts
        monthly_amount = annual_amount / 12
        
        # Calculate amount per payment based on frequency
        payments_per_year = {
            "Weekly": 52,
            "Biweekly": 26,
            "Monthly": 12,
            "Quarterly": 4,
            "Semi-Annual": 2,
            "Annual": 1
        }.get(primary_income_freq, 12)
        
        amount_per_payment = annual_amount / payments_per_year
        
        # Create primary income source
        primary_income = Income(
            id=generate_id("income"),
            workspace_id=workspace_id,
            spending_id=spending.id,
            client_id=client_id,
            plan_id=client_plan.id if client_plan else None,
            created_by=creator.id,
            updated_by=updater.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=f"{primary_income_type} Income",
            description=f"Primary {primary_income_type.lower()} income",
            income_type=primary_income_type,
            status="Active",
            frequency=primary_income_freq,
            annual_amount=annual_amount,
            monthly_amount=monthly_amount,
            amount_per_payment=amount_per_payment,
            payment_day=random.randint(1, 15) if primary_income_freq in ["Monthly", "Semi-Annual", "Quarterly", "Annual"] else None,
            start_date=fake.date_between(start_date='-5y', end_date='-1m'),
            end_date=None,
            growth_rate=random.uniform(0.01, 0.04),  # 1-4% annual growth
            income_source=generate_income_source_details(primary_income_type),
            taxable=True,
            tax_rate=random.uniform(0.15, 0.35),
            notes=fake.paragraph() if random.random() < 0.3 else None
        )
        
        db.add(primary_income)
        income_sources.append(primary_income)
        
        # Add secondary income sources if needed
        for i in range(1, num_income_sources):
            # Choose a different income type
            secondary_income_type = random.choice([t for t in income_types if t != primary_income_type])
            secondary_income_freq = random.choice(frequency_types)
            
            # Determine secondary income amount (usually smaller than primary)
            if secondary_income_type in ["Rental", "Dividend", "Business"]:
                annual_amount = random.uniform(10000, 50000)
            elif secondary_income_type in ["Bonus", "Commission"]:
                annual_amount = random.uniform(5000, 30000)
            else:
                annual_amount = random.uniform(3000, 20000)
                
            # Calculate derived amounts
            monthly_amount = annual_amount / 12
            
            # Calculate amount per payment based on frequency
            payments_per_year = {
                "Weekly": 52,
                "Biweekly": 26,
                "Monthly": 12,
                "Quarterly": 4,
                "Semi-Annual": 2,
                "Annual": 1
            }.get(secondary_income_freq, 12)
            
            amount_per_payment = annual_amount / payments_per_year
            
            # Create secondary income source
            secondary_income = Income(
                id=generate_id("income"),
                workspace_id=workspace_id,
                spending_id=spending.id,
                client_id=client_id,
                plan_id=client_plan.id if client_plan else None,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                name=f"{secondary_income_type} Income",
                description=f"Additional income from {secondary_income_type.lower()}",
                income_type=secondary_income_type,
                status="Active",
                frequency=secondary_income_freq,
                annual_amount=annual_amount,
                monthly_amount=monthly_amount,
                amount_per_payment=amount_per_payment,
                payment_day=random.randint(1, 28) if secondary_income_freq in ["Monthly", "Semi-Annual", "Quarterly", "Annual"] else None,
                start_date=fake.date_between(start_date='-3y', end_date='-1m'),
                end_date=fake.date_between(start_date='+1y', end_date='+10y') if random.random() < 0.3 else None,
                growth_rate=random.uniform(0, 0.03),  # 0-3% annual growth
                income_source=generate_income_source_details(secondary_income_type),
                taxable=not secondary_income_type in ["Municipal Bonds", "Child Support"],
                tax_rate=random.uniform(0.15, 0.32) if secondary_income_type not in ["Municipal Bonds", "Child Support"] else 0,
                notes=fake.paragraph() if random.random() < 0.3 else None
            )
            
            db.add(secondary_income)
            income_sources.append(secondary_income)
    
    db.commit()
    print(f"Created {len(income_sources)} income sources!")
    return income_sources

def generate_income_source_details(income_type):
    """Generate appropriate details for different income types."""
    if income_type == "Salary":
        return {
            "employer": fake.company(),
            "position": random.choice([
                "Senior Engineer", "Project Manager", "Director", "Manager",
                "Specialist", "Coordinator", "Analyst", "Executive", "Administrator"
            ]),
            "payment_method": random.choice(["Direct Deposit", "Check"]),
            "withholding": {
                "federal": True,
                "state": True,
                "local": random.choice([True, False]),
                "retirement": random.choice([True, False])
            }
        }
    elif income_type in ["Self-Employment", "Business"]:
        return {
            "business_name": fake.company(),
            "industry": random.choice([
                "Consulting", "Technology", "Healthcare", "Retail", 
                "Financial Services", "Education", "Construction"
            ]),
            "payment_method": random.choice(["Direct Deposit", "Check", "Cash", "Transfer"]),
            "quarterly_taxes": random.choice([True, False])
        }
    elif income_type == "Rental":
        return {
            "property_type": random.choice(["Residential", "Commercial", "Vacation"]),
            "address": fake.address(),
            "tenant": fake.name() if random.random() < 0.7 else None,
            "lease_terms": {
                "duration": random.choice(["Month-to-Month", "1 Year", "2 Year"]),
                "renewal_date": str(fake.date_between(start_date='+30d', end_date='+1y'))
            }
        }
    elif income_type in ["Dividend", "Interest", "Capital Gains"]:
        return {
            "investment_type": random.choice([
                "Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "CDs", "Savings Account"
            ]),
            "institution": random.choice([
                "Charles Schwab", "Fidelity", "Vanguard", "TD Ameritrade", 
                "Bank of America", "Chase", "Wells Fargo"
            ]),
            "reinvestment": random.choice([True, False])
        }
    elif income_type in ["Pension", "Social Security"]:
        return {
            "provider": fake.company() if income_type == "Pension" else "Social Security Administration",
            "plan_type": random.choice(["Defined Benefit", "Defined Contribution"]) if income_type == "Pension" else "Federal",
            "payment_method": "Direct Deposit",
            "cola": random.choice([True, False])
        }
    else:
        return {
            "source": fake.company(),
            "payment_method": random.choice(["Direct Deposit", "Check", "Cash", "Transfer"]),
            "reliability": random.choice(["Very Reliable", "Reliable", "Somewhat Reliable", "Variable"])
        }

def seed_expenses(db: Session, spending_records: list, financial_plans: list, goals: list, users: list, workspace_id: str):
    """Create expenses for spending records."""
    print("Creating expenses...")
    
    expenses = []
    
    # Common expense categories
    expense_categories = [
        "Housing", "Transportation", "Food", "Utilities", "Healthcare", 
        "Insurance", "Debt Payments", "Entertainment", "Shopping", 
        "Personal Care", "Education", "Childcare", "Travel", "Gifts & Donations", 
        "Taxes", "Savings", "Miscellaneous"
    ]
    
    # Sub-categories for better descriptions
    sub_categories = {
        "Housing": ["Mortgage", "Rent", "Property Taxes", "HOA Fees", "Home Maintenance", "Home Insurance"],
        "Transportation": ["Car Payment", "Fuel", "Car Insurance", "Maintenance", "Public Transit", "Rideshare"],
        "Food": ["Groceries", "Restaurants", "Coffee Shops", "Meal Delivery"],
        "Utilities": ["Electricity", "Water", "Gas", "Internet", "Cable", "Phone"],
        "Healthcare": ["Health Insurance", "Prescriptions", "Doctor Visits", "Dental Care", "Vision Care"],
        "Insurance": ["Life Insurance", "Disability Insurance", "Umbrella Policy"],
        "Debt Payments": ["Credit Card", "Student Loan", "Personal Loan"],
        "Entertainment": ["Streaming Services", "Movies", "Concerts", "Sports Events", "Hobbies"],
        "Shopping": ["Clothing", "Electronics", "Home Goods", "Books"],
        "Personal Care": ["Haircuts", "Gym Membership", "Spa", "Beauty Products"],
        "Education": ["Tuition", "Books", "Online Courses", "Tutoring"],
        "Childcare": ["Daycare", "Babysitting", "School Supplies", "Activities"],
        "Travel": ["Vacations", "Flights", "Hotels", "Rental Cars"],
        "Gifts & Donations": ["Birthdays", "Holidays", "Charitable Contributions"],
        "Taxes": ["Federal", "State", "Local", "Property", "Self-Employment"],
        "Savings": ["Emergency Fund", "Retirement", "Investment", "Goal-Specific"],
        "Miscellaneous": ["Subscriptions", "Fees", "Miscellaneous"]
    }
    
    # Frequency types
    frequency_types = ["Weekly", "Biweekly", "Monthly", "Quarterly", "Semi-Annual", "Annual"]
    
    # Payment methods
    payment_methods = ["Credit Card", "Debit Card", "ACH", "Check", "Cash", "Automatic Payment"]
    
    for spending in spending_records:
        # Get client ID
        client_id = spending.client_id
        
        # Try to find a financial plan for this client
        client_plan = next((plan for plan in financial_plans if plan.client_id == client_id), None)
        
        # Try to find goals for this client - FIXED: Changed from financial_plan_id to plan_id
        client_goals = [goal for goal in goals if goal.plan_id == client_plan.id] if client_plan else []
        
        # Select random user for created_by/updated_by
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Determine number of expenses (8-20)
        num_expenses = random.randint(8, 20)
        
        # Track expenses by category for analysis
        expense_by_category = {}
        
        # Determine annual income (for realistic expense scaling)
        annual_income = sum([
            float(income.annual_amount) if income.annual_amount else 0
            for income in db.query(Income).filter(Income.spending_id == spending.id).all()
        ])
        
        # If no income found, set a default
        if not annual_income:
            annual_income = random.uniform(60000, 150000)
        
        # Create common essential expenses first
        essential_expenses = [
            # Housing (typically 25-35% of income)
            {
                "category": "Housing",
                "sub_category": "Mortgage" if random.random() < 0.7 else "Rent",
                "frequency": "Monthly",
                "annual_percent": random.uniform(0.25, 0.35),
                "is_discretionary": False
            },
            # Transportation (typically 10-15% of income)
            {
                "category": "Transportation",
                "sub_category": "Car Payment" if random.random() < 0.8 else "Public Transit",
                "frequency": "Monthly",
                "annual_percent": random.uniform(0.1, 0.15),
                "is_discretionary": False
            },
            # Food (typically 10-15% of income)
            {
                "category": "Food",
                "sub_category": "Groceries",
                "frequency": "Weekly" if random.random() < 0.5 else "Biweekly",
                "annual_percent": random.uniform(0.1, 0.15),
                "is_discretionary": False
            },
            # Utilities (typically 5-7% of income)
            {
                "category": "Utilities",
                "sub_category": random.choice(sub_categories["Utilities"]),
                "frequency": "Monthly",
                "annual_percent": random.uniform(0.05, 0.07),
                "is_discretionary": False
            },
            # Healthcare (typically 5-10% of income)
            {
                "category": "Healthcare",
                "sub_category": "Health Insurance",
                "frequency": "Monthly",
                "annual_percent": random.uniform(0.05, 0.1),
                "is_discretionary": False
            },
            # Insurance (typically 2-5% of income)
            {
                "category": "Insurance",
                "sub_category": random.choice(sub_categories["Insurance"]),
                "frequency": "Monthly" if random.random() < 0.7 else "Annual",
                "annual_percent": random.uniform(0.02, 0.05),
                "is_discretionary": False
            }
        ]
        
        # Process essential expenses
        for expense_template in essential_expenses:
            category = expense_template["category"]
            sub_category = expense_template["sub_category"]
            frequency = expense_template["frequency"]
            annual_percent = expense_template["annual_percent"]
            is_discretionary = expense_template["is_discretionary"]
            
            # Calculate amounts
            annual_amount = annual_income * annual_percent
            monthly_amount = annual_amount / 12
            
            # Calculate amount per payment based on frequency
            payments_per_year = {
                "Weekly": 52,
                "Biweekly": 26,
                "Monthly": 12,
                "Quarterly": 4,
                "Semi-Annual": 2,
                "Annual": 1
            }.get(frequency, 12)
            
            amount_per_payment = annual_amount / payments_per_year
            
            # Create expense
            expense = Expense(
                id=generate_id("expense"),
                workspace_id=workspace_id,
                spending_id=spending.id,
                client_id=client_id,
                plan_id=client_plan.id if client_plan else None,
                goal_id=None,  # Essential expenses are typically not tied to goals
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                name=f"{sub_category}",
                description=f"{sub_category} expense",
                category=category,
                status="Active",
                frequency=frequency,
                annual_amount=annual_amount,
                monthly_amount=monthly_amount,
                amount_per_payment=amount_per_payment,
                payment_day=random.randint(1, 15) if frequency in ["Monthly"] else None,
                start_date=fake.date_between(start_date='-3y', end_date='-1m'),
                end_date=None,  # Essential expenses usually don't have end dates
                growth_rate=random.uniform(0.01, 0.03),  # 1-3% annual growth
                auto_payment=random.choice([True, False]),
                payment_method=random.choice(payment_methods),
                is_tax_deductible=category in ["Mortgage Interest", "Charitable Contributions", "Medical Expenses"],
                expense_source={
                    "vendor": fake.company(),
                    "category": category,
                    "sub_category": sub_category,
                    "notes": fake.sentence() if random.random() < 0.3 else None
                },
                is_discretionary=is_discretionary,
                is_goal=False,
                notes=fake.paragraph() if random.random() < 0.3 else None
            )
            
            db.add(expense)
            expenses.append(expense)
            
            # Track expenses by category
            if category not in expense_by_category:
                expense_by_category[category] = 0
            expense_by_category[category] += annual_amount
        
        # Fill remaining expenses with discretionary and miscellaneous
        remaining_expenses = num_expenses - len(essential_expenses)
        
        # Calculate remaining income for discretionary expenses
        essential_expense_total = sum(float(v) for v in expense_by_category.values())
        remaining_income = annual_income - essential_expense_total
        
        # Average discretionary expense amount
        avg_discretionary = remaining_income / max(1, remaining_expenses)
        
        for i in range(remaining_expenses):
            # Choose a category that isn't represented yet, or random
            remaining_categories = [cat for cat in expense_categories if cat not in expense_by_category]
            if not remaining_categories or random.random() < 0.3:
                remaining_categories = [cat for cat in expense_categories if cat not in ["Housing", "Utilities"]]
                
            category = random.choice(remaining_categories)
            sub_category = random.choice(sub_categories.get(category, [category]))
            
            # Decide if this is a discretionary expense
            is_discretionary = category in [
                "Entertainment", "Shopping", "Travel", "Gifts & Donations", 
                "Miscellaneous", "Personal Care"
            ] or random.random() < 0.3
            
            # Decide if this is tied to a goal
            is_goal = False
            goal_id = None
            
            if client_goals and random.random() < 0.2:
                # 20% chance of tying to a goal if goals exist
                goal = random.choice(client_goals)
                is_goal = True
                goal_id = goal.id
            
            # Determine frequency (discretionary expenses are more variable)
            if is_discretionary:
                frequency = random.choice(frequency_types)
            else:
                frequency = random.choice(["Monthly", "Quarterly", "Annual"])
                
            # Determine amount (discretionary expenses are more variable)
            if is_discretionary:
                annual_amount = random.uniform(0.1 * avg_discretionary, 0.5 * avg_discretionary)
            else:
                annual_amount = random.uniform(0.3 * avg_discretionary, avg_discretionary)
                
            monthly_amount = annual_amount / 12
            
            # Calculate amount per payment based on frequency
            payments_per_year = {
                "Weekly": 52,
                "Biweekly": 26,
                "Monthly": 12,
                "Quarterly": 4,
                "Semi-Annual": 2,
                "Annual": 1
            }.get(frequency, 12)
            
            amount_per_payment = annual_amount / payments_per_year
            
            # Create expense
            expense = Expense(
                id=generate_id("expense"),
                workspace_id=workspace_id,
                spending_id=spending.id,
                client_id=client_id,
                plan_id=client_plan.id if client_plan else None,
                goal_id=goal_id,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                name=f"{sub_category}",
                description=f"{sub_category} expense",
                category=category,
                status="Active",
                frequency=frequency,
                annual_amount=annual_amount,
                monthly_amount=monthly_amount,
                amount_per_payment=amount_per_payment,
                payment_day=random.randint(1, 28) if frequency in ["Monthly"] else None,
                start_date=fake.date_between(start_date='-2y', end_date='-1m'),
                end_date=fake.date_between(start_date='+1m', end_date='+2y') if random.random() < 0.3 else None,
                growth_rate=random.uniform(0, 0.02),  # 0-2% annual growth
                auto_payment=random.choice([True, False]),
                payment_method=random.choice(payment_methods),
                is_tax_deductible=category in ["Charitable Contributions", "Medical Expenses", "Education"],
                expense_source={
                    "vendor": fake.company(),
                    "category": category,
                    "sub_category": sub_category,
                    "notes": fake.sentence() if random.random() < 0.3 else None
                },
                is_discretionary=is_discretionary,
                is_goal=is_goal,
                notes=fake.paragraph() if random.random() < 0.3 else None
            )
            
            db.add(expense)
            expenses.append(expense)
            
            # Track expenses by category
            if category not in expense_by_category:
                expense_by_category[category] = 0
            expense_by_category[category] += annual_amount
        
        # Update spending record with expense categories
        spending.expense_categories = {
            category: round(amount, 2) for category, amount in expense_by_category.items()
        }
    
    db.commit()
    print(f"Created {len(expenses)} expenses!")
    return expenses

def seed_budgets(db: Session, spending_records: list, users: list, workspace_id: str):
    """Create budgets and budget categories for spending records."""
    print("Creating budgets and budget categories...")
    
    budgets = []
    budget_categories_created = 0
    
    # Common budget periods
    budget_periods = ["Monthly", "Quarterly", "Annual"]
    
    for spending in spending_records:
        # Get client ID
        client_id = spending.client_id
        
        # Select random user for created_by/updated_by
        creator = random.choice(users)
        updater = random.choice(users)
        
        # Get client's expenses
        client_expenses = db.query(Expense).filter(Expense.client_id == client_id).all()
        if not client_expenses:
            continue
            
        # Choose a budget period
        period_type = random.choice(budget_periods)
        
        # Set budget dates
        if period_type == "Monthly":
            start_date = date.today().replace(day=1)
            next_month = start_date.month + 1
            next_year = start_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            end_date = date(next_year, next_month, 1) - timedelta(days=1)
        elif period_type == "Quarterly":
            month = ((date.today().month - 1) // 3) * 3 + 1
            start_date = date(date.today().year, month, 1)
            next_quarter_month = month + 3
            next_quarter_year = date.today().year
            if next_quarter_month > 12:
                next_quarter_month -= 12
                next_quarter_year += 1
            end_date = date(next_quarter_year, next_quarter_month, 1) - timedelta(days=1)
        else:  # Annual
            start_date = date(date.today().year, 1, 1)
            end_date = date(date.today().year, 12, 31)
            
        # Group expenses by category
        expenses_by_category = {}
        for expense in client_expenses:
            if expense.category not in expenses_by_category:
                expenses_by_category[expense.category] = []
            expenses_by_category[expense.category].append(expense)
            
        # Calculate total income and expenses
        total_monthly_income = float(db.query(func.sum(Income.monthly_amount)).filter(Income.client_id == client_id).scalar() or 0)
        total_monthly_expenses = float(db.query(func.sum(Expense.monthly_amount)).filter(Expense.client_id == client_id).scalar() or 0)
        
        # Scale to budget period
        period_multiplier = {
            "Monthly": 1,
            "Quarterly": 3,
            "Annual": 12
        }.get(period_type, 1)
        
        total_income = total_monthly_income * period_multiplier
        total_expenses = total_monthly_expenses * period_multiplier
        total_savings = total_income - total_expenses
        
        # Prepare category limits and allocations
        category_limits = {}
        allocations = []
        
        # Generate category allocations (target vs. actual)
        for category, expenses in expenses_by_category.items():
            # Calculate actual spending in this category
            actual_monthly = sum(float(expense.monthly_amount) if expense.monthly_amount else 0 for expense in expenses)
            actual_amount = actual_monthly * period_multiplier
            
            # Set a target limit (slightly adjusted from actual)
            target_adjustment = random.uniform(0.8, 1.1)  # 80% to 110% of actual
            target_amount = actual_amount * target_adjustment
            
            # Add to category limits
            category_limits[category] = round(target_amount, 2)
            
            # Add to allocations
            allocations.append({
                "category": category,
                "target_amount": round(target_amount, 2),
                "actual_amount": round(actual_amount, 2),
                "percentage": round((actual_amount / total_expenses) * 100 if total_expenses > 0 else 0, 2)
            })
            
        # Create budget
        budget_id = generate_id("budget")
        budget = Budget(
            id=budget_id,
            workspace_id=workspace_id,
            spending_id=spending.id,
            client_id=client_id,
            created_by=creator.id,
            updated_by=updater.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=f"{period_type} Budget {start_date.strftime('%Y-%m')}",
            status="Active",
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            total_income=round(total_income, 2),
            total_expenses=round(total_expenses, 2),
            total_savings=round(total_savings, 2),
            allocations=allocations,
            category_limits=category_limits,
            progress={
                "spent_percentage": random.uniform(0, 1),
                "days_elapsed": (date.today() - start_date).days,
                "days_total": (end_date - start_date).days + 1,
                "last_updated": str(date.today())
            },
            auto_categorization=random.choice([True, False]),
            notifications={
                "over_budget": random.choice([True, False]),
                "regular_updates": random.choice([True, False]),
                "email": random.choice([True, False])
            },
            notes=fake.paragraph() if random.random() < 0.3 else None
        )
        
        db.add(budget)
        budgets.append(budget)
        
        # Create budget categories
        for category, amount in category_limits.items():
            budget_category = BudgetCategory(
                id=generate_id("budcat"),
                budget_id=budget_id,
                name=category,
                description=f"{category} budget allocation",
                amount=amount,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(budget_category)
            budget_categories_created += 1
    
    db.commit()
    print(f"Created {len(budgets)} budgets with {budget_categories_created} budget categories!")
    return budgets

def update_spending_records(db: Session, spending_records: list):
    """Update spending records with calculated totals."""
    print("Updating spending records with totals...")
    
    for spending in spending_records:
        # Get client ID
        client_id = spending.client_id
        
        # Calculate totals
        annual_income = float(db.query(func.sum(Income.annual_amount)).filter(Income.client_id == client_id).scalar() or 0)
        annual_expenses = float(db.query(func.sum(Expense.annual_amount)).filter(Expense.client_id == client_id).scalar() or 0)
        annual_savings = annual_income - annual_expenses
        
        monthly_income = float(db.query(func.sum(Income.monthly_amount)).filter(Income.client_id == client_id).scalar() or 0)
        monthly_expenses = float(db.query(func.sum(Expense.monthly_amount)).filter(Expense.client_id == client_id).scalar() or 0)
        monthly_savings = monthly_income - monthly_expenses
        
        # Calculate ratios
        savings_rate = (annual_savings / annual_income) if annual_income > 0 else 0
        expense_to_income_ratio = (annual_expenses / annual_income) if annual_income > 0 else 0
        
        # Determine cash flow status
        if savings_rate >= 0.2:
            cash_flow_status = "Excellent"
        elif savings_rate >= 0.1:
            cash_flow_status = "Good"
        elif savings_rate >= 0:
            cash_flow_status = "Satisfactory"
        else:
            cash_flow_status = "Needs Improvement"
            
        # Get expense breakdown
        expense_breakdown = db.query(
            Expense.category, 
            func.sum(Expense.annual_amount).label('amount')
        ).filter(
            Expense.client_id == client_id
        ).group_by(
            Expense.category
        ).all()
        
        expense_breakdown_dict = {
            category: float(amount) if amount else 0 for category, amount in expense_breakdown
        }
        
        # Get income breakdown
        income_breakdown = db.query(
            Income.income_type, 
            func.sum(Income.annual_amount).label('amount')
        ).filter(
            Income.client_id == client_id
        ).group_by(
            Income.income_type
        ).all()
        
        income_breakdown_dict = {
            income_type: float(amount) if amount else 0 for income_type, amount in income_breakdown
        }
        
        # Generate recommendations
        recommendations = []
        
        # Savings recommendations
        if savings_rate < 0.1:
            recommendations.append("Consider increasing savings rate to at least 10% of income.")
        
        # Housing recommendations
        housing_percent = expense_breakdown_dict.get("Housing", 0) / annual_income if annual_income > 0 else 0
        if housing_percent > 0.35:
            recommendations.append("Housing expenses exceed 35% of income. Consider ways to reduce this cost.")
            
        # Debt recommendations
        debt_percent = expense_breakdown_dict.get("Debt Payments", 0) / annual_income if annual_income > 0 else 0
        if debt_percent > 0.2:
            recommendations.append("Debt payments exceed 20% of income. Consider a debt reduction strategy.")
            
        # Income diversification
        if len(income_breakdown_dict) < 2:
            recommendations.append("Consider diversifying income sources for greater financial stability.")
            
        # Update spending record
        spending.annual_income = annual_income
        spending.annual_expenses = annual_expenses
        spending.annual_savings = annual_savings
        spending.monthly_income = monthly_income
        spending.monthly_expenses = monthly_expenses
        spending.monthly_savings = monthly_savings
        spending.savings_rate = savings_rate
        spending.expense_to_income_ratio = expense_to_income_ratio
        spending.cash_flow_status = cash_flow_status
        spending.expense_categories = expense_breakdown_dict
        spending.analysis = {
            "savings_trend": "Stable",  # Would be calculated from historical data in a real app
            "expense_breakdown": expense_breakdown_dict,
            "income_breakdown": income_breakdown_dict,
            "recommendations": recommendations
        }
    
    db.commit()
    print(f"Updated {len(spending_records)} spending records with totals!")

if __name__ == "__main__":
    seed_spending_data()
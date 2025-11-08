from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import random
import uuid

# Import models correctly based on your model structure
from models.financial import (
    FinancialPlan, Goal, MonteCarlo, Projection, CashFlow,
    PlanIncome, Scenario
)
from models.clients import Client
from database import SessionLocal


def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def seed_financial_plans(db: Session = None):
    """Main function to seed all financial planning data."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_plans = db.query(FinancialPlan).count()
        if existing_plans > 0:
            print("Financial plan data already seeded, skipping...")
            return
        
        # Get all clients
        clients = db.query(Client).all()
        if not clients:
            print("No clients found. Please seed client data first.")
            return
        
        print(f"Found {len(clients)} clients. Seeding financial plans...")
        
        # Seed financial plans for most clients (about 80%)
        selected_clients = random.sample(clients, int(len(clients) * 0.8))
        plan_count = 0
        goal_count = 0
        monte_carlo_count = 0
        projection_count = 0
        scenario_count = 0
        cashflow_count = 0
        income_count = 0
        
        for client in selected_clients:
            # Create 1-3 financial plans per client
            num_plans = random.randint(1, 3)
            
            for i in range(num_plans):
                # Create Financial Plan
                plan = seed_financial_plan(db, client)
                plan_count += 1
                
                # Create Goals (3-6 per plan)
                goals = seed_goals(db, plan.id, random.randint(3, 6))
                goal_count += len(goals)
                
                # Create Monte Carlo Simulation
                monte_carlo = seed_monte_carlo(db, plan.id)
                monte_carlo_count += 1
                
                # Create Scenarios (1-3 per plan)
                scenarios = seed_scenarios(db, plan.id, random.randint(1, 3))
                scenario_count += len(scenarios)
                
                # Create Projections (10-30 years)
                projections = seed_projections(db, plan.id, random.randint(10, 30))
                projection_count += len(projections)
                
                # Create Cash Flow
                cash_flow = seed_cash_flow(db, plan.id)
                cashflow_count += 1
                
                # Create Plan Income sources (2-5 per plan)
                incomes = seed_plan_income(db, plan.id, random.randint(2, 5))
                income_count += len(incomes)
                
                # Commit after each plan is created with all its associated data
                db.commit()
        
        print(f"Financial planning seeding complete!")
        print(f"Created: {plan_count} financial plans, {goal_count} goals, "
              f"{monte_carlo_count} Monte Carlo simulations, {scenario_count} scenarios, "
              f"{projection_count} projections, {cashflow_count} cash flows, "
              f"{income_count} income sources")
        
        return plan_count
        
    except Exception as e:
        print(f"Error seeding financial planning data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()


def seed_financial_plan(db: Session, client):
    """Create a financial plan for a client."""
    plan_names = [
        "Comprehensive Financial Plan",
        "Retirement Strategy",
        "Wealth Building Plan",
        "Legacy Planning",
        "Investment Strategy",
        "College Savings Plan"
    ]
    
    plan_descriptions = [
        "Long-term wealth building and retirement strategy",
        "Focused on achieving retirement goals by target date",
        "Optimizing investment performance and tax efficiency",
        "Preserving wealth for future generations",
        "Balancing growth and income for long-term security",
        "Education funding strategy for dependents"
    ]
    
    plan = FinancialPlan(
        id=generate_id("plan"),
        client_id=client.id,
        name=f"{random.choice(plan_names)} {random.randint(2024, 2025)}",
        description=random.choice(plan_descriptions),
        status=random.choice(["active", "draft", "review"]),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(plan)
    db.flush()  # Flush to get the ID
    return plan


def seed_goals(db: Session, plan_id, count=4):
    """Create goals for a financial plan."""
    goal_templates = [
        {
            "name": "Emergency Fund",
            "description": "Build 6-month emergency reserve",
            "target_amount": lambda: random.uniform(20000, 50000),
            "current_amount": lambda amt: amt * random.uniform(0.3, 0.8),
            "target_date": lambda: date.today() + timedelta(days=random.randint(180, 730)),
            "priority": "high",
            "category": "savings"
        },
        {
            "name": "Home Purchase",
            "description": "Save for down payment on primary residence",
            "target_amount": lambda: random.uniform(50000, 200000),
            "current_amount": lambda amt: amt * random.uniform(0.2, 0.6),
            "target_date": lambda: date.today() + timedelta(days=random.randint(365, 1825)),
            "priority": "high",
            "category": "major_purchase"
        },
        {
            "name": "Children's Education",
            "description": "College fund for children",
            "target_amount": lambda: random.uniform(100000, 400000),
            "current_amount": lambda amt: amt * random.uniform(0.1, 0.4),
            "target_date": lambda: date.today() + timedelta(days=random.randint(2920, 6570)),
            "priority": "medium",
            "category": "education"
        },
        {
            "name": "Retirement Savings",
            "description": "Accumulate retirement nest egg",
            "target_amount": lambda: random.uniform(1000000, 5000000),
            "current_amount": lambda amt: amt * random.uniform(0.05, 0.3),
            "target_date": lambda: date.today() + timedelta(days=random.randint(3650, 10950)),
            "priority": "high",
            "category": "retirement"
        },
        {
            "name": "Debt Elimination",
            "description": "Pay off all consumer debt",
            "target_amount": lambda: random.uniform(10000, 100000),
            "current_amount": lambda amt: amt * random.uniform(0.0, 0.1),
            "target_date": lambda: date.today() + timedelta(days=random.randint(365, 1825)),
            "priority": "high",
            "category": "debt_reduction"
        },
        {
            "name": "Vacation Home",
            "description": "Purchase vacation property",
            "target_amount": lambda: random.uniform(200000, 800000),
            "current_amount": lambda amt: amt * random.uniform(0.05, 0.2),
            "target_date": lambda: date.today() + timedelta(days=random.randint(1825, 3650)),
            "priority": "low",
            "category": "major_purchase"
        },
        {
            "name": "Business Investment",
            "description": "Capital for business venture",
            "target_amount": lambda: random.uniform(50000, 250000),
            "current_amount": lambda amt: amt * random.uniform(0.1, 0.3),
            "target_date": lambda: date.today() + timedelta(days=random.randint(365, 2555)),
            "priority": "medium",
            "category": "business"
        },
        {
            "name": "Travel Fund",
            "description": "World travel experiences",
            "target_amount": lambda: random.uniform(20000, 100000),
            "current_amount": lambda amt: amt * random.uniform(0.1, 0.4),
            "target_date": lambda: date.today() + timedelta(days=random.randint(365, 2555)),
            "priority": "low",
            "category": "lifestyle"
        }
    ]
    
    # Choose a random subset of goal templates
    selected_templates = random.sample(goal_templates, min(count, len(goal_templates)))
    
    goals = []
    for template in selected_templates:
        target = template["target_amount"]()
        current = template["current_amount"](target)
        
        goal = Goal(
            id=generate_id("goal"),
            plan_id=plan_id,
            name=template["name"],
            description=template["description"],
            target_amount=round(target, 2),
            current_amount=round(current, 2),
            target_date=template["target_date"](),
            priority=template["priority"],
            category=template["category"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(goal)
        goals.append(goal)
    
    db.flush()
    return goals


def seed_monte_carlo(db: Session, plan_id):
    """Create a Monte Carlo simulation for a financial plan."""
    # Calculate random but plausible Monte Carlo results
    success_rate = random.uniform(0.65, 0.95)
    iterations = 10000
    median_value = random.uniform(1000000, 3000000)
    std_dev = median_value * random.uniform(0.2, 0.4)
    
    low_percentile = max(0, median_value - (std_dev * 1.5))
    high_percentile = median_value + (std_dev * 1.5)
    
    monte_carlo = MonteCarlo(
        id=generate_id("monte"),
        plan_id=plan_id,
        scenario_id=None,  # Will be updated later if scenarios are created
        success_rate=success_rate,
        iterations=iterations,
        confidence_interval=0.95,
        median_ending_value=median_value,
        lowest_percentile_value=low_percentile,
        highest_percentile_value=high_percentile,
        results_detail={
            "percentile_10": round(max(0, median_value - (std_dev * 1.3)), 2),
            "percentile_25": round(max(0, median_value - (std_dev * 0.7)), 2),
            "percentile_50": round(median_value, 2),
            "percentile_75": round(median_value + (std_dev * 0.7), 2),
            "percentile_90": round(median_value + (std_dev * 1.3), 2),
            "mean": round(median_value, 2),
            "standard_deviation": round(std_dev, 2)
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(monte_carlo)
    db.flush()
    return monte_carlo


def seed_scenarios(db: Session, plan_id, count=2):
    """Create scenarios for a financial plan."""
    scenario_templates = [
        {
            "name": "Base Case",
            "description": "Expected financial trajectory with current assumptions",
            "is_default": True,
            "retirement_age": lambda: random.randint(62, 70),
            "life_expectancy": lambda: random.randint(85, 95),
            "inflation_rate": lambda: round(random.uniform(0.02, 0.035), 4),
            "investment_return_rate": lambda: round(random.uniform(0.05, 0.09), 4),
            "tax_rate": lambda: round(random.uniform(0.15, 0.35), 4)
        },
        {
            "name": "Early Retirement",
            "description": "Accelerated retirement timeline with adjusted spending",
            "is_default": False,
            "retirement_age": lambda: random.randint(55, 60),
            "life_expectancy": lambda: random.randint(85, 95),
            "inflation_rate": lambda: round(random.uniform(0.02, 0.035), 4),
            "investment_return_rate": lambda: round(random.uniform(0.04, 0.08), 4),
            "tax_rate": lambda: round(random.uniform(0.15, 0.32), 4)
        },
        {
            "name": "Conservative Growth",
            "description": "Lower risk portfolio with reduced expected returns",
            "is_default": False,
            "retirement_age": lambda: random.randint(65, 72),
            "life_expectancy": lambda: random.randint(85, 95),
            "inflation_rate": lambda: round(random.uniform(0.02, 0.03), 4),
            "investment_return_rate": lambda: round(random.uniform(0.04, 0.06), 4),
            "tax_rate": lambda: round(random.uniform(0.15, 0.25), 4)
        },
        {
            "name": "Aggressive Growth",
            "description": "Higher risk portfolio targeting larger returns",
            "is_default": False,
            "retirement_age": lambda: random.randint(60, 67),
            "life_expectancy": lambda: random.randint(85, 95),
            "inflation_rate": lambda: round(random.uniform(0.025, 0.035), 4),
            "investment_return_rate": lambda: round(random.uniform(0.07, 0.11), 4),
            "tax_rate": lambda: round(random.uniform(0.2, 0.37), 4)
        },
        {
            "name": "High Inflation",
            "description": "Planning for periods of elevated inflation",
            "is_default": False,
            "retirement_age": lambda: random.randint(65, 70),
            "life_expectancy": lambda: random.randint(85, 95),
            "inflation_rate": lambda: round(random.uniform(0.04, 0.06), 4),
            "investment_return_rate": lambda: round(random.uniform(0.06, 0.1), 4),
            "tax_rate": lambda: round(random.uniform(0.18, 0.35), 4)
        }
    ]
    
    # Choose a random subset of scenario templates
    selected_templates = random.sample(scenario_templates, min(count, len(scenario_templates)))
    
    # Ensure we have a default scenario
    has_default = any(template["is_default"] for template in selected_templates)
    if not has_default and len(selected_templates) > 0:
        selected_templates[0]["is_default"] = True
    
    scenarios = []
    for template in selected_templates:
        withdrawal_strategies = ["4% Rule", "Dynamic Spending", "Bucket Strategy", "Income Floor"]
        social_security_strategies = ["Claim at FRA", "Claim at 70", "Claim at 62", "Spousal Optimization"]
        
        scenario = Scenario(
            id=generate_id("scenario"),
            plan_id=plan_id,
            name=template["name"],
            description=template["description"],
            is_default=template["is_default"],
            status="active",
            retirement_age=template["retirement_age"](),
            life_expectancy=template["life_expectancy"](),
            inflation_rate=template["inflation_rate"](),
            investment_return_rate=template["investment_return_rate"](),
            tax_rate=template["tax_rate"](),
            withdrawal_strategy=random.choice(withdrawal_strategies),
            social_security_strategy=random.choice(social_security_strategies),
            parameters={
                "additional_income": random.randint(0, 50000),
                "legacy_goal": random.randint(0, 1000000),
                "healthcare_annual_cost": random.randint(5000, 20000),
                "long_term_care_insurance": random.choice([True, False])
            },
            results_summary={
                "success_probability": random.uniform(0.65, 0.95),
                "median_ending_balance": random.uniform(500000, 3000000),
                "worst_case_balance": random.uniform(0, 500000),
                "best_case_balance": random.uniform(3000000, 10000000)
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(scenario)
        scenarios.append(scenario)
    
    db.flush()
    return scenarios


def seed_projections(db: Session, plan_id, years=30):
    """Create year-by-year financial projections."""
    current_year = datetime.now().year
    base_assets = random.uniform(200000, 1000000)
    base_liabilities = base_assets * random.uniform(0.2, 0.8)
    base_income = random.uniform(80000, 250000)
    base_expenses = base_income * random.uniform(0.5, 0.8)
    
    # Growth rates
    asset_growth_rate = random.uniform(0.04, 0.08)
    liability_reduction_rate = random.uniform(0.03, 0.07)
    income_growth_rate = random.uniform(0.02, 0.04)
    expense_growth_rate = random.uniform(0.02, 0.035)
    
    projections = []
    for i in range(years):
        year = current_year + i
        assets = base_assets * ((1 + asset_growth_rate) ** i)
        liabilities = max(0, base_liabilities * ((1 - liability_reduction_rate) ** i))
        income = base_income * ((1 + income_growth_rate) ** i)
        expenses = base_expenses * ((1 + expense_growth_rate) ** i)
        
        projection = Projection(
            id=generate_id("proj"),
            plan_id=plan_id,
            year=year,
            assets=round(assets, 2),
            liabilities=round(liabilities, 2),
            net_worth=round(assets - liabilities, 2),
            income=round(income, 2),
            expenses=round(expenses, 2),
            cash_flow=round(income - expenses, 2),
            created_at=datetime.utcnow()
        )
        db.add(projection)
        projections.append(projection)
    
    db.flush()
    return projections


def seed_cash_flow(db: Session, plan_id):
    """Create a cash flow record for a financial plan."""
    # Base values
    base_salary = random.uniform(60000, 200000)
    base_business = random.uniform(0, 100000) if random.random() < 0.3 else 0
    base_investment = random.uniform(2000, 50000)
    base_rental = random.uniform(0, 60000) if random.random() < 0.3 else 0
    base_other = random.uniform(0, 20000) if random.random() < 0.5 else 0
    
    total_income = base_salary + base_business + base_investment + base_rental + base_other
    
    # Expenses as percentages of income
    housing_pct = random.uniform(0.2, 0.35)
    utilities_pct = random.uniform(0.03, 0.06)
    food_pct = random.uniform(0.08, 0.15)
    transportation_pct = random.uniform(0.05, 0.12)
    healthcare_pct = random.uniform(0.05, 0.1)
    insurance_pct = random.uniform(0.03, 0.08)
    debt_pct = random.uniform(0.05, 0.2)
    entertainment_pct = random.uniform(0.03, 0.1)
    personal_pct = random.uniform(0.02, 0.06)
    other_pct = random.uniform(0.02, 0.06)
    
    # Calculate expense values
    housing_expense = total_income * housing_pct
    utilities_expense = total_income * utilities_pct
    food_expense = total_income * food_pct
    transportation_expense = total_income * transportation_pct
    healthcare_expense = total_income * healthcare_pct
    insurance_expense = total_income * insurance_pct
    debt_payments = total_income * debt_pct
    entertainment_expense = total_income * entertainment_pct
    personal_expense = total_income * personal_pct
    other_expense = total_income * other_pct
    
    total_expenses = (housing_expense + utilities_expense + food_expense + 
                     transportation_expense + healthcare_expense + insurance_expense + 
                     debt_payments + entertainment_expense + personal_expense + other_expense)
    
    cash_flow = CashFlow(
        id=generate_id("cash"),
        plan_id=plan_id,
        scenario_id=None,  # Will be updated later if linked to a specific scenario
        salary_income=round(base_salary, 2),
        business_income=round(base_business, 2),
        investment_income=round(base_investment, 2),
        rental_income=round(base_rental, 2),
        other_income=round(base_other, 2),
        total_income=round(total_income, 2),
        housing_expense=round(housing_expense, 2),
        utilities_expense=round(utilities_expense, 2),
        food_expense=round(food_expense, 2),
        transportation_expense=round(transportation_expense, 2),
        healthcare_expense=round(healthcare_expense, 2),
        insurance_expense=round(insurance_expense, 2),
        debt_payments=round(debt_payments, 2),
        entertainment_expense=round(entertainment_expense, 2),
        personal_expense=round(personal_expense, 2),
        other_expense=round(other_expense, 2),
        total_expenses=round(total_expenses, 2),
        net_cash_flow=round(total_income - total_expenses, 2),
        period="Annual",
        year=datetime.now().year,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cash_flow)
    db.flush()
    return cash_flow


def seed_plan_income(db: Session, plan_id, count=3):
    """Create income sources for a financial plan."""
    income_types = [
        "Salary", "Bonus", "Commission", "Self-Employment", "Rental",
        "Dividend", "Interest", "Capital Gains", "Pension", "Social Security",
        "Annuity", "Royalty", "Business", "Trust", "Alimony"
    ]
    
    frequencies = ["Weekly", "Bi-weekly", "Semi-monthly", "Monthly", "Quarterly", "Annual"]
    
    incomes = []
    for i in range(count):
        income_type = random.choice(income_types)
        frequency = random.choice(frequencies)
        
        # Set appropriate amount range based on income type
        if income_type == "Salary":
            amount = random.uniform(50000, 250000)
        elif income_type in ["Bonus", "Commission"]:
            amount = random.uniform(5000, 50000)
        elif income_type == "Rental":
            amount = random.uniform(12000, 60000)
        elif income_type in ["Dividend", "Interest"]:
            amount = random.uniform(1000, 30000)
        elif income_type in ["Pension", "Social Security"]:
            amount = random.uniform(15000, 45000)
        else:
            amount = random.uniform(3000, 100000)
        
        # Adjust amount based on frequency
        if frequency != "Annual":
            if frequency == "Monthly":
                amount /= 12
            elif frequency == "Quarterly":
                amount /= 4
            elif frequency == "Bi-weekly":
                amount /= 26
            elif frequency == "Semi-monthly":
                amount /= 24
            elif frequency == "Weekly":
                amount /= 52
        
        # Set dates
        start_date = date.today() - timedelta(days=random.randint(0, 3650))
        
        # End date (some incomes ongoing, some ending)
        if random.random() < 0.7:  # 70% have no end date
            end_date = None
        else:
            end_date = start_date + timedelta(days=random.randint(365, 7300))
        
        # Create income source
        income = PlanIncome(
            id=generate_id("income"),
            plan_id=plan_id,
            name=f"{income_type} Income" if random.random() < 0.5 else f"{['Primary', 'Secondary', 'Supplemental'][random.randint(0, 2)]} {income_type}",
            income_type=income_type,
            amount=round(amount, 2),
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            growth_rate=round(random.uniform(0.01, 0.05), 4),
            details=generate_income_details(income_type),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(income)
        incomes.append(income)
    
    db.flush()
    return incomes


def generate_income_details(income_type):
    """Generate appropriate details for different income types."""
    if income_type == "Salary":
        return {
            "employer": f"{random.choice(['Tech', 'Global', 'Advanced', 'Premier'])} {random.choice(['Solutions', 'Industries', 'Corporation', 'Enterprises'])}",
            "position": random.choice([
                "Senior Engineer", "Project Manager", "Director of Operations",
                "Marketing Manager", "Financial Analyst", "HR Specialist",
                "Product Manager", "Sales Executive", "Operations Lead"
            ])
        }
    elif income_type in ["Bonus", "Commission"]:
        return {
            "basis": random.choice(["Performance", "Sales", "Profit Sharing", "Year-end"]),
            "average_percentage": round(random.uniform(0.05, 0.3), 2)
        }
    elif income_type == "Rental":
        return {
            "property_type": random.choice(["Residential", "Commercial", "Multi-family"]),
            "address": f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine', 'Cedar'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
            "units": random.randint(1, 5)
        }
    elif income_type in ["Dividend", "Interest"]:
        return {
            "account_type": random.choice(["Brokerage", "Savings", "CD", "Money Market", "Bond"]),
            "institution": random.choice([
                "Fidelity", "Vanguard", "Charles Schwab", "JP Morgan",
                "Bank of America", "Wells Fargo", "Citi"
            ]),
            "average_yield": round(random.uniform(0.01, 0.06), 4)
        }
    elif income_type == "Business":
        return {
            "business_name": f"{random.choice(['Blue', 'Green', 'Red', 'Golden', 'Silver'])} {random.choice(['Horizon', 'Peak', 'Edge', 'Valley', 'Mountain'])} {random.choice(['LLC', 'Inc', 'Enterprises', 'Group'])}",
            "industry": random.choice([
                "Technology", "Consulting", "Retail", "Manufacturing", 
                "Food Service", "Healthcare", "Financial Services"
            ]),
            "ownership_percentage": round(random.uniform(0.25, 1.0), 2)
        }
    else:
        return {
            "description": random.choice([
                "Regular income source", "Variable income source",
                "Guaranteed income", "Performance-based income",
                "Passive income", "Fixed income", "Supplemental income"
            ]),
            "reliability": random.choice(["High", "Medium", "Low"]),
            "taxability": random.choice(["Fully taxable", "Partially taxable", "Tax-advantaged"])
        }


if __name__ == "__main__":
    seed_financial_plans()
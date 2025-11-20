# seeders/financial_seeder.py - FIXED for PascalCase field names

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from decimal import Decimal
import random
import json
from faker import Faker

from models.financial import (
    FinancialPlan, Goal, Scenario, CashFlow, NetWorth,
    PlanStatus, PlanType, GoalType, GoalStatus, ScenarioType, RetirementReadiness
)

fake = Faker()

class FinancialSeeder:
    def __init__(self, db: Session):
        self.db = db
        self.created_data = {
            "financial_plans": [],
            "goals": [],
            "scenarios": [],
            "cash_flows": [],
            "net_worths": []
        }
    
    def seed_all(self) -> Dict[str, List[Any]]:
        """Seed all V3 Financial Planning Core entities"""
        print("Starting V3 Financial Planning seeding...")
        
        # Seed in dependency order
        self.seed_financial_plans()
        self.seed_goals()
        self.seed_scenarios()
        self.seed_cash_flows()
        self.seed_net_worths()
        
        self.db.commit()
        print("V3 Financial Planning seeding completed!")
        
        return self.created_data
    
    def seed_financial_plans(self):
        """Seed 200 financial plans"""
        print("Seeding financial plans...")
        
        # Assume clients C00001 through C00200 exist from V2
        client_ids = [f"C{i:05d}" for i in range(1, 201)]
        household_ids = [f"H{i:03d}" for i in range(1, 151)]
        user_ids = [f"USR-{i:03d}" for i in range(1, 61)]
        
        plan_types = list(PlanType)
        plan_statuses = list(PlanStatus)
        retirement_readiness_options = list(RetirementReadiness)
        
        for i in range(1, 201):
            client_id = client_ids[i-1]
            household_id = random.choice(household_ids)
            
            plan_type = random.choice(plan_types)
            plan_name = self._generate_plan_name(plan_type, i)
            
            created_date = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            last_reviewed = created_date + timedelta(days=random.randint(30, 365)) if random.random() < 0.8 else None
            
            financial_plan = FinancialPlan(
                PlanID=f"PLAN-{i:05d}",
                ClientID=client_id,
                HouseholdID=household_id if random.random() < 0.7 else None,
                PlanName=plan_name,
                PlanType=plan_type.value,
                Status=random.choice([PlanStatus.ACTIVE.value] * 8 + [PlanStatus.DRAFT.value] + [PlanStatus.ARCHIVED.value]),
                StartDate=created_date.date(),
                EndDate=(created_date + timedelta(days=random.randint(1825, 10950))).date() if random.random() < 0.9 else None,
                CreatedDate=created_date,
                LastReviewed=last_reviewed,
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                CreatedBy=random.choice(user_ids),
                RetirementReadiness=random.choice(retirement_readiness_options).value
            )
            
            self.db.add(financial_plan)
            self.created_data["financial_plans"].append(financial_plan)
        
        print(f"✓ Seeded {len(self.created_data['financial_plans'])} financial plans")
    
    def seed_goals(self):
        """Seed 800 goals (4 per plan on average)"""
        print("Seeding goals...")
        
        plans = self.created_data["financial_plans"]
        goal_types = list(GoalType)
        goal_statuses = list(GoalStatus)
        
        goal_counter = 1
        
        for plan in plans:
            # Each plan gets 2-6 goals
            num_goals = random.randint(2, 6)
            
            for _ in range(num_goals):
                if goal_counter > 800:
                    break
                
                goal_type = random.choice(goal_types)
                goal_name = self._generate_goal_name(goal_type)
                
                # Generate realistic amounts based on goal type
                target_amount, current_value, monthly_contribution = self._generate_goal_amounts(goal_type)
                
                # Calculate funding percentage and projected value
                if target_amount > 0:
                    funding_percentage = min(Decimal('100.00'), (current_value / target_amount) * 100)
                else:
                    funding_percentage = Decimal('0.00')
                
                # Simple projection calculation (not sophisticated, just for mock data)
                years_to_goal = random.randint(5, 30)
                projected_value = current_value + (monthly_contribution * 12 * years_to_goal * Decimal('1.07'))  # Assume 7% growth
                
                target_date = (datetime.utcnow() + timedelta(days=years_to_goal * 365)).date()
                
                # Determine status based on funding percentage
                if funding_percentage >= 95:
                    status = GoalStatus.ON_TRACK.value
                elif funding_percentage >= 75:
                    status = random.choice([GoalStatus.ON_TRACK.value, GoalStatus.ON_TRACK.value, GoalStatus.OFF_TRACK.value])
                else:
                    status = random.choice([GoalStatus.OFF_TRACK.value, GoalStatus.ON_TRACK.value])
                
                goal = Goal(
                    GoalID=f"GOAL-{goal_counter:05d}",
                    PlanID=plan.PlanID,
                    ClientID=plan.ClientID,
                    GoalType=goal_type.value,
                    GoalName=goal_name,
                    Description=self._generate_goal_description(goal_type, goal_name),
                    TargetDate=target_date,
                    TargetAmount=target_amount,
                    CurrentValue=current_value,
                    MonthlyContribution=monthly_contribution,
                    ProjectedValue=projected_value,
                    FundingPercentage=funding_percentage,
                    Priority=random.randint(1, 5),
                    Status=status,
                    CreatedDate=plan.CreatedDate + timedelta(days=random.randint(0, 30)),
                    ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                
                self.db.add(goal)
                self.created_data["goals"].append(goal)
                goal_counter += 1
        
        print(f"✓ Seeded {len(self.created_data['goals'])} goals")
    
    def seed_scenarios(self):
        """Seed 150 scenarios"""
        print("Seeding scenarios...")
        
        plans = self.created_data["financial_plans"]
        scenario_types = list(ScenarioType)
        
        # Select 150 random plans to have scenarios
        selected_plans = random.sample(plans, min(150, len(plans)))
        
        for i, plan in enumerate(selected_plans, 1):
            scenario_type = random.choice(scenario_types)
            scenario_name = self._generate_scenario_name(scenario_type, i)
            
            # Generate scenario assumptions and results
            assumptions = self._generate_scenario_assumptions(scenario_type)
            results = self._generate_scenario_results(scenario_type, assumptions)
            
            scenario = Scenario(
                ScenarioID=f"SCEN-{i:05d}",
                PlanID=plan.PlanID,
                ScenarioName=scenario_name,
                ScenarioType=scenario_type.value,
                Description=self._generate_scenario_description(scenario_type),
                Assumptions=assumptions,
                Results=results,
                Status=random.choice([PlanStatus.ACTIVE.value] * 9 + [PlanStatus.DRAFT.value]),
                CreatedDate=plan.CreatedDate + timedelta(days=random.randint(30, 180)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(scenario)
            self.created_data["scenarios"].append(scenario)
        
        print(f"✓ Seeded {len(self.created_data['scenarios'])} scenarios")
    
    def seed_cash_flows(self):
        """Seed 200 cash flow projections (one per plan)"""
        print("Seeding cash flows...")
        
        plans = self.created_data["financial_plans"]
        cash_flow_counter = 1
        
        for plan in plans:
            # Create 5-20 years of cash flow projections per plan
            years_to_project = random.randint(5, 20)
            current_year = datetime.now().year
            
            cumulative_cash_flow = Decimal('0.00')
            
            for year_offset in range(years_to_project):
                if cash_flow_counter > 200:
                    break
                    
                projection_year = current_year + year_offset
                
                # Generate realistic income and expense projections
                base_income = Decimal(str(random.randint(50000, 300000)))
                income_growth = Decimal('1.03') ** year_offset  # 3% annual growth
                total_income = base_income * income_growth
                
                base_expenses = Decimal(str(random.randint(40000, 200000)))
                expense_growth = Decimal('1.025') ** year_offset  # 2.5% annual growth
                total_expenses = base_expenses * expense_growth
                
                net_cash_flow = total_income - total_expenses
                cumulative_cash_flow += net_cash_flow
                
                cash_flow = CashFlow(
                    CashFlowID=f"CF-{plan.PlanID}-{projection_year}",
                    PlanID=plan.PlanID,
                    Year=projection_year,
                    Month=None,  # Annual projections
                    TotalIncome=total_income,
                    TotalExpenses=total_expenses,
                    NetCashFlow=net_cash_flow,
                    CumulativeCashFlow=cumulative_cash_flow,
                    InflationRate=Decimal('0.0275'),  # 2.75% inflation assumption
                    Status=PlanStatus.ACTIVE.value,
                    CreatedDate=plan.CreatedDate + timedelta(days=random.randint(30, 90)),
                    ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                
                self.db.add(cash_flow)
                self.created_data["cash_flows"].append(cash_flow)
                cash_flow_counter += 1
        
        print(f"✓ Seeded {len(self.created_data['cash_flows'])} cash flow projections")
    
    def seed_net_worths(self):
        """Seed 200 net worth records (one per plan)"""
        print("Seeding net worths...")
        
        plans = self.created_data["financial_plans"]
        
        for plan in plans:
            # Generate realistic net worth components
            liquid_assets = Decimal(str(random.randint(10000, 500000)))
            invested_assets = Decimal(str(random.randint(50000, 2000000)))
            use_assets = Decimal(str(random.randint(100000, 1000000)))  # Home, cars, etc.
            
            total_assets = liquid_assets + invested_assets + use_assets
            
            total_liabilities = Decimal(str(random.randint(0, int(total_assets * Decimal('0.4')))))  # Max 40% of assets
            net_worth_value = total_assets - total_liabilities
            
            # Use plan creation date as the as_of_date
            as_of_date = plan.CreatedDate.date()
            
            net_worth_record = NetWorth(
                NetWorthID=f"NW-{plan.PlanID}",
                PlanID=plan.PlanID,
                HouseholdID=plan.HouseholdID,
                AsOfDate=as_of_date,
                TotalAssets=total_assets,
                TotalLiabilities=total_liabilities,
                NetWorth=net_worth_value,
                LiquidAssets=liquid_assets,
                InvestedAssets=invested_assets,
                UseAssets=use_assets,
                Status=PlanStatus.ACTIVE.value,
                CreatedDate=as_of_date + timedelta(days=1),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(net_worth_record)
            self.created_data["net_worths"].append(net_worth_record)
        
        print(f"✓ Seeded {len(self.created_data['net_worths'])} net worth records")
    
    def _generate_plan_name(self, plan_type: PlanType, index: int) -> str:
        """Generate plan name based on type"""
        names = {
            PlanType.COMPREHENSIVE: f"Comprehensive Financial Plan {index}",
            PlanType.RETIREMENT: f"Retirement Planning Strategy {index}",
            PlanType.EDUCATION: f"Education Funding Plan {index}",
            PlanType.ESTATE: f"Estate Planning Strategy {index}",
            PlanType.TAX: f"Tax Optimization Plan {index}",
            PlanType.INSURANCE: f"Insurance Analysis Plan {index}"
        }
        return names.get(plan_type, f"Financial Plan {index}")
    
    def _generate_goal_name(self, goal_type: GoalType) -> str:
        """Generate goal name based on type"""
        names = {
            GoalType.RETIREMENT: random.choice(["Comfortable Retirement", "Early Retirement", "Retirement Security"]),
            GoalType.EDUCATION: random.choice(["Children's College Fund", "Graduate School", "Education Savings"]),
            GoalType.HOME_PURCHASE: random.choice(["Dream Home", "Vacation Home", "New Car", "Home Renovation"]),
            GoalType.EMERGENCY_FUND: random.choice(["Emergency Fund", "Rainy Day Fund", "Security Buffer"]),
            GoalType.DEBT_PAYOFF: random.choice(["Mortgage Payoff", "Student Loan Elimination", "Credit Card Freedom"]),
            GoalType.VACATION: random.choice(["European Vacation", "Family Trip", "Dream Vacation", "Annual Travel Fund"]),
            GoalType.OTHER: random.choice(["Special Goal", "Personal Objective", "Custom Goal"])
        }
        return names.get(goal_type, "Financial Goal")
    
    def _generate_goal_amounts(self, goal_type: GoalType) -> tuple:
        """Generate realistic amounts for different goal types"""
        amounts = {
            GoalType.RETIREMENT: (Decimal(str(random.randint(800000, 2500000))), 
                                Decimal(str(random.randint(100000, 800000))), 
                                Decimal(str(random.randint(500, 2000)))),
            GoalType.EDUCATION: (Decimal(str(random.randint(100000, 400000))), 
                               Decimal(str(random.randint(10000, 150000))), 
                               Decimal(str(random.randint(200, 800)))),
            GoalType.HOME_PURCHASE: (Decimal(str(random.randint(50000, 500000))), 
                                    Decimal(str(random.randint(10000, 200000))), 
                                    Decimal(str(random.randint(300, 1200)))),
            GoalType.EMERGENCY_FUND: (Decimal(str(random.randint(25000, 100000))), 
                                    Decimal(str(random.randint(5000, 50000))), 
                                    Decimal(str(random.randint(200, 600)))),
            GoalType.DEBT_PAYOFF: (Decimal(str(random.randint(50000, 300000))), 
                                 Decimal(str(random.randint(150000, 280000))), 
                                 Decimal(str(random.randint(800, 2500)))),
            GoalType.VACATION: (Decimal(str(random.randint(10000, 50000))), 
                              Decimal(str(random.randint(2000, 25000))), 
                              Decimal(str(random.randint(100, 500)))),
        }
        return amounts.get(goal_type, (Decimal('50000'), Decimal('10000'), Decimal('300')))
    
    def _generate_goal_description(self, goal_type: GoalType, goal_name: str) -> str:
        """Generate goal description"""
        descriptions = {
            GoalType.RETIREMENT: f"Plan for {goal_name.lower()} with adequate income replacement",
            GoalType.EDUCATION: f"Save for {goal_name.lower()} to ensure educational opportunities",
            GoalType.HOME_PURCHASE: f"Accumulate funds for {goal_name.lower()}",
            GoalType.EMERGENCY_FUND: f"Build {goal_name.lower()} for unexpected expenses",
            GoalType.DEBT_PAYOFF: f"Strategy to achieve {goal_name.lower()}",
            GoalType.VACATION: f"Save for {goal_name.lower()} and travel experiences",
        }
        return descriptions.get(goal_type, f"Work toward achieving {goal_name}")
    
    def _generate_scenario_name(self, scenario_type: ScenarioType, index: int) -> str:
        """Generate scenario name"""
        names = {
            ScenarioType.BASE_CASE: f"Base Case Scenario {index}",
            ScenarioType.OPTIMISTIC: f"Optimistic Scenario {index}",
            ScenarioType.PESSIMISTIC: f"Conservative Scenario {index}",
            ScenarioType.WHAT_IF: f"What-If Analysis {index}"
        }
        return names.get(scenario_type, f"Scenario {index}")
    
    def _generate_scenario_description(self, scenario_type: ScenarioType) -> str:
        """Generate scenario description"""
        descriptions = {
            ScenarioType.BASE_CASE: "Primary planning scenario with moderate assumptions",
            ScenarioType.OPTIMISTIC: "Best-case scenario with favorable market conditions",
            ScenarioType.PESSIMISTIC: "Conservative scenario with cautious assumptions",
            ScenarioType.WHAT_IF: "Alternative scenario exploring different possibilities"
        }
        return descriptions.get(scenario_type, "Financial planning scenario")
    
    def _generate_scenario_assumptions(self, scenario_type: ScenarioType) -> dict:
        """Generate scenario assumptions"""
        base_assumptions = {
            "inflation_rate": 0.025,
            "market_return": 0.07,
            "salary_growth": 0.03,
            "retirement_age": 65,
            "life_expectancy": 90
        }
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            base_assumptions.update({
                "market_return": 0.09,
                "salary_growth": 0.04,
                "inflation_rate": 0.02
            })
        elif scenario_type == ScenarioType.PESSIMISTIC:
            base_assumptions.update({
                "market_return": 0.05,
                "salary_growth": 0.02,
                "inflation_rate": 0.035
            })
        
        return base_assumptions
    
    def _generate_scenario_results(self, scenario_type: ScenarioType, assumptions: dict) -> dict:
        """Generate scenario results based on assumptions"""
        market_return = assumptions.get("market_return", 0.07)
        
        # Simple calculations for mock results
        projected_wealth = random.randint(500000, 3000000) * (1 + market_return) ** 20
        retirement_income = projected_wealth * 0.04  # 4% rule
        
        success_probability = {
            ScenarioType.OPTIMISTIC: random.uniform(0.85, 0.95),
            ScenarioType.BASE_CASE: random.uniform(0.75, 0.85),
            ScenarioType.PESSIMISTIC: random.uniform(0.60, 0.75),
            ScenarioType.WHAT_IF: random.uniform(0.65, 0.80)
        }.get(scenario_type, 0.75)
        
        return {
            "projected_wealth": round(projected_wealth, 2),
            "retirement_income": round(retirement_income, 2),
            "success_probability": round(success_probability, 3),
            "years_to_goal": random.randint(15, 30),
            "shortfall_risk": round(1 - success_probability, 3)
        }
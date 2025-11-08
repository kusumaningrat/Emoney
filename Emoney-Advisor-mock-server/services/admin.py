from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
import uuid
import random
import datetime
from faker import Faker

# Use print statements instead of loguru if not available
try:
    from loguru import logger
except ImportError:
    # Fallback to print-based logger
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    logger = SimpleLogger()

from database import Base, engine
from models.clients import Client, Spouse, Household, HouseholdMember, Contact
from models.financial import FinancialPlan, Goal, MonteCarlo, Projection, CashFlow
from models.accounts import Account, Liability, AccountTypeModel
from models.assets import Asset, AssetClass, Allocation, Security, Holding
from models.spending import Income, Expense, Budget, BudgetCategory
from models.documents import VaultDocument, Note, Task, Alert
from models.users import User, Role, Permission, Firm, Logon

# Try to import optional models
try:
    from models.insurance import Insurance
except ImportError:
    Insurance = None

try:
    from models.retirement import RetirementPlan
except ImportError:
    RetirementPlan = None

try:
    from models.tax import Tax
except ImportError:
    Tax = None

try:
    from models.estate import Estate
except ImportError:
    Estate = None

fake = Faker()

class AdminService:
    """
    Service for administrative operations
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_entity_type(self) -> str:
        return "Admin"
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get database status information
        """
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_counts = {}
        for table in tables:
            try:
                count = self.db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                table_counts[table] = count
            except Exception as e:
                table_counts[table] = f"Error: {str(e)}"
        
        return {
            "status": "connected" if tables else "error",
            "tables": tables,
            "counts": table_counts,
            "database_url": str(engine.url).replace(":***@", ":******@"),  # Hide password
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def reset_database(self) -> Dict[str, Any]:
        """
        Reset database by dropping and recreating all tables
        """
        try:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            
            return {
                "status": "success",
                "message": "Database reset successfully",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")
    
    def seed_database(self, entity_type: str = "all") -> Dict[str, Any]:
        """
        Seed database with test data
        """
        try:
            # Define mapping of entity types to seeder methods
            seeders = {
                "all": self._seed_all,
                "clients": self._seed_clients,
                "financial_plans": self._seed_financial_plans,
                "accounts": self._seed_accounts,
                "assets": self._seed_assets,
                "spending": self._seed_spending,
                "documents": self._seed_documents,
                "users": self._seed_users,
                "firms": self._seed_firms
            }
            
            # Check if entity type is valid
            if entity_type not in seeders:
                raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")
            
            # Call appropriate seeder method
            result = seeders[entity_type]()
            
            return {
                "status": "success",
                "message": f"Database seeded successfully with {entity_type} data",
                "details": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error seeding database: {str(e)}")
    
    def _seed_all(self) -> Dict[str, int]:
        """
        Seed all entity types
        """
        results = {}
        
        results.update(self._seed_firms())
        results.update(self._seed_users())
        results.update(self._seed_clients())
        results.update(self._seed_financial_plans())
        results.update(self._seed_accounts())
        results.update(self._seed_assets())
        results.update(self._seed_spending())
        results.update(self._seed_file_types())  # Add this BEFORE documents
        results.update(self._seed_documents())
        
        return results
    
    def _seed_firms(self) -> Dict[str, int]:
        """
        Seed firms
        """
        firm_count = 0
        
        try:
            # Create firms
            firms = [
                Firm(
                    id=f"firm-00{i+1}",
                    name=f"{fake.company()} {random.choice(['Wealth Management', 'Financial Advisors', 'Investments', 'Asset Management'])}",
                    address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state_abbr(),
                    postal_code=fake.zipcode(),
                    country="United States",
                    phone=fake.phone_number(),
                    email=f"info@{fake.domain_name()}",
                    website=f"https://www.{fake.domain_name()}"
                )
                for i in range(3)
            ]
            
            # Add to database
            for firm in firms:
                self.db.add(firm)
            
            self.db.commit()
            firm_count = len(firms)
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding firms: {str(e)}")
        
        return {"firms": firm_count}
    
    def _seed_users(self) -> Dict[str, int]:
        """
        Seed users, roles, and permissions
        """
        user_count = 0
        role_count = 0
        permission_count = 0
        
        try:
            # Create roles
            roles = [
                Role(id="role-001", name="Advisor", description="Financial advisor role"),
                Role(id="role-002", name="Assistant", description="Assistant role"),
                Role(id="role-003", name="Manager", description="Manager role"),
                Role(id="role-004", name="Compliance", description="Compliance officer role"),
                Role(id="role-005", name="Investment", description="Investment specialist role"),
                Role(id="role-006", name="Admin", description="Administrator role")
            ]
            
            # Add roles to database
            for role in roles:
                self.db.add(role)
            
            self.db.commit()
            role_count = len(roles)
            
            # Create permissions
            permissions = []
            resources = ["Client", "Plan", "Account", "Asset", "Document", "Task", "User", "Firm"]
            actions = ["read", "create", "update", "delete"]
            
            for role in roles:
                for resource in resources:
                    for action in actions:
                        # Admin and Manager can do everything
                        if role.name in ["Admin", "Manager"]:
                            permission = Permission(
                                id=f"perm-{uuid.uuid4().hex[:8]}",
                                role_id=role.id,
                                resource=resource,
                                action=action
                            )
                            permissions.append(permission)
                        
                        # Advisors can do everything except delete
                        elif role.name == "Advisor" and action != "delete":
                            permission = Permission(
                                id=f"perm-{uuid.uuid4().hex[:8]}",
                                role_id=role.id,
                                resource=resource,
                                action=action
                            )
                            permissions.append(permission)
                        
                        # Assistants can read everything and create/update some things
                        elif role.name == "Assistant" and (action == "read" or (action in ["create", "update"] and resource in ["Task", "Document"])):
                            permission = Permission(
                                id=f"perm-{uuid.uuid4().hex[:8]}",
                                role_id=role.id,
                                resource=resource,
                                action=action
                            )
                            permissions.append(permission)
                        
                        # Compliance can read everything
                        elif role.name == "Compliance" and action == "read":
                            permission = Permission(
                                id=f"perm-{uuid.uuid4().hex[:8]}",
                                role_id=role.id,
                                resource=resource,
                                action=action
                            )
                            permissions.append(permission)
                        
                        # Investment specialists can read everything and create/update some things
                        elif role.name == "Investment" and (action == "read" or (action in ["create", "update"] and resource in ["Asset", "Account"])):
                            permission = Permission(
                                id=f"perm-{uuid.uuid4().hex[:8]}",
                                role_id=role.id,
                                resource=resource,
                                action=action
                            )
                            permissions.append(permission)
            
            # Add permissions to database
            for permission in permissions:
                self.db.add(permission)
            
            self.db.commit()
            permission_count = len(permissions)
            
            # Get firms
            firms = self.db.query(Firm).all()
            if not firms:
                # Create a default firm if none exists
                firm = Firm(
                    id="firm-001",
                    name="Acme Financial Advisors",
                    address="123 Main St",
                    city="New York",
                    state="NY",
                    postal_code="10001",
                    country="United States",
                    phone="555-123-4567",
                    email="info@acmefinancial.com",
                    website="https://www.acmefinancial.com"
                )
                self.db.add(firm)
                self.db.commit()
                firms = [firm]
            
            # Create users
            users = []
            
            # Create 2-3 users per firm with different roles
            for firm in firms:
                # Create an admin
                admin = User(
                    id=f"user-admin-{firm.id}",
                    firm_id=firm.id,
                    username=f"admin-{firm.id}",
                    email=f"admin@{firm.name.lower().replace(' ', '')}.com",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    title="Administrator",
                    phone=fake.phone_number(),
                    is_active=True
                )
                admin.roles.append(self.db.query(Role).filter(Role.name == "Admin").first())
                users.append(admin)
                
                # Create advisors
                for i in range(3):
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    username = f"{first_name.lower()}.{last_name.lower()}"
                    
                    advisor = User(
                        id=f"user-{uuid.uuid4().hex[:8]}",
                        firm_id=firm.id,
                        username=username,
                        email=f"{username}@{firm.name.lower().replace(' ', '')}.com",
                        first_name=first_name,
                        last_name=last_name,
                        title="Financial Advisor",
                        phone=fake.phone_number(),
                        is_active=True
                    )
                    advisor.roles.append(self.db.query(Role).filter(Role.name == "Advisor").first())
                    users.append(advisor)
                
                # Create one of each other role
                for role_name in ["Assistant", "Manager", "Compliance", "Investment"]:
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    username = f"{first_name.lower()}.{last_name.lower()}"
                    
                    user = User(
                        id=f"user-{uuid.uuid4().hex[:8]}",
                        firm_id=firm.id,
                        username=username,
                        email=f"{username}@{firm.name.lower().replace(' ', '')}.com",
                        first_name=first_name,
                        last_name=last_name,
                        title=f"{role_name} Specialist",
                        phone=fake.phone_number(),
                        is_active=True
                    )
                    user.roles.append(self.db.query(Role).filter(Role.name == role_name).first())
                    users.append(user)
            
            # Add users to database
            for user in users:
                self.db.add(user)
            
            self.db.commit()
            user_count = len(users)
            
            # Create logons for users
            logons = []
            
            for user in users:
                logon = Logon(
                    id=f"logon-{uuid.uuid4().hex[:8]}",
                    user_id=user.id,
                    username=user.username,
                    status="Active",
                    last_login=fake.date_time_between(start_date="-30d", end_date="now")
                )
                logons.append(logon)
            
            # Add logons to database
            for logon in logons:
                self.db.add(logon)
            
            self.db.commit()
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding users: {str(e)}")
        
        return {"users": user_count, "roles": role_count, "permissions": permission_count}
    
    def _seed_clients(self) -> Dict[str, int]:
        """
        Seed clients, spouses, households, and contacts
        """
        client_count = 0
        spouse_count = 0
        household_count = 0
        
        try:
            # Get firms and advisors
            firms = self.db.query(Firm).all()
            if not firms:
                raise HTTPException(status_code=400, detail="No firms found. Please seed firms first.")
            
            advisors = self.db.query(User).join(User.roles).filter(Role.name == "Advisor").all()
            if not advisors:
                raise HTTPException(status_code=400, detail="No advisors found. Please seed users first.")
            
            # Create clients (10-15 per firm)
            clients = []
            spouses = []
            households = []
            
            for firm in firms:
                firm_advisors = [advisor for advisor in advisors if advisor.firm_id == firm.id]
                
                if not firm_advisors:
                    continue
                
                # Create 10-15 clients for this firm
                for i in range(random.randint(10, 15)):
                    # Create client
                    client_id = f"client-{uuid.uuid4().hex[:8]}"
                    advisor = random.choice(firm_advisors)
                    
                    marital_status = random.choice(["Single", "Married", "Divorced", "Widowed"])
                    
                    client = Client(
                        id=client_id,
                        firm_id=firm.id,
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        email=fake.email(),
                        phone=fake.phone_number(),
                        marital_status=marital_status,
                        previous_marriages=random.choice([True, False]) if marital_status in ["Divorced", "Widowed", "Married"] else False,
                        date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=80),
                        owning_advisor=advisor.id,
                        external_id=f"CRM-{fake.random_number(digits=6)}"
                    )
                    clients.append(client)
                    
                    # If married, create spouse
                    if marital_status == "Married":
                        spouse = Spouse(
                            id=f"spouse-{uuid.uuid4().hex[:8]}",
                            client_id=client_id,
                            first_name=fake.first_name(),
                            last_name=client.last_name,
                            email=fake.email(),
                            phone=fake.phone_number(),
                            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=80),
                            previous_marriages=random.choice([True, False])
                        )
                        spouses.append(spouse)
                    
                    # Create household for some clients
                    if random.random() < 0.8:
                        household = Household(
                            id=f"household-{uuid.uuid4().hex[:8]}",
                            name=f"{client.last_name} Household",
                            primary_client_id=client_id
                        )
                        households.append(household)
            
            # Add to database
            for client in clients:
                self.db.add(client)
            
            self.db.commit()
            client_count = len(clients)
            
            for spouse in spouses:
                self.db.add(spouse)
            
            self.db.commit()
            spouse_count = len(spouses)
            
            for household in households:
                self.db.add(household)
            
            self.db.commit()
            household_count = len(households)
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding clients: {str(e)}")
        
        return {"clients": client_count, "spouses": spouse_count, "households": household_count}
    
    def _seed_financial_plans(self) -> Dict[str, int]:
        """
        Seed financial plans, goals, monte carlo analyses, and projections
        """
        plan_count = 0
        goal_count = 0
        monte_carlo_count = 0
        projection_count = 0
        
        try:
            # Get clients
            clients = self.db.query(Client).all()
            if not clients:
                raise HTTPException(status_code=400, detail="No clients found. Please seed clients first.")
            
            logger.info(f"Found {len(clients)} clients to create plans for")
            
            # Create plans (1-3 per client)
            plans = []
            goals = []
            monte_carlos = []
            projections = []
            
            for client in clients:
                num_plans = random.randint(1, 3)
                
                for i in range(num_plans):
                    plan_type = random.choice(["Base Facts", "Advanced Planning Scenario", "What-If"])
                    status = "active" if i == 0 else random.choice(["draft", "active", "review"])
                    
                    plan_id = f"plan-{uuid.uuid4().hex[:8]}"
                    
                    try:
                        plan = FinancialPlan(
                            id=plan_id,
                            client_id=client.id,
                            name=f"{plan_type} - {fake.catch_phrase()}" if i > 0 else "Base Facts",
                            description=fake.text(max_nb_chars=100),
                            status=status
                        )
                        plans.append(plan)
                        logger.info(f"Created plan {plan_id} for client {client.id}")
                    except Exception as e:
                        logger.error(f"Error creating plan for client {client.id}: {str(e)}")
                        raise
                    
                    # Create goals (2-5 per plan)
                    num_goals = random.randint(2, 5)
                    for j in range(num_goals):
                        goal_types = [
                            ("Retirement", "Retire comfortably", 25, 40),
                            ("College Education", "Fund college education", 5, 10),
                            ("Home Purchase", "Buy a dream home", 1, 5),
                            ("Travel", "Travel the world", 1, 3),
                            ("Legacy", "Leave a legacy", 20, 40),
                            ("Business", "Start a business", 2, 5)
                        ]
                        
                        goal_type = random.choice(goal_types)
                        start_years = random.randint(goal_type[2], goal_type[3])
                        
                        target_amount = float(random.randint(5, 100) * 10000)
                        current_amount = float(target_amount * random.uniform(0.1, 0.5))
                        target_date = datetime.date.today() + datetime.timedelta(days=365*start_years)
                        
                        try:
                            goal = Goal(
                                id=f"goal-{uuid.uuid4().hex[:8]}",
                                plan_id=plan_id,
                                name=goal_type[0],
                                description=goal_type[1],
                                target_amount=target_amount,
                                current_amount=current_amount,
                                target_date=target_date,
                                priority=random.choice(["high", "medium", "low"]),
                                category=goal_type[0].lower().replace(" ", "_")
                            )
                            goals.append(goal)
                        except Exception as e:
                            logger.error(f"Error creating goal for plan {plan_id}: {str(e)}")
                            raise
                    
                    # Create Monte Carlo analysis
                    success_rate = round(random.uniform(0.50, 0.95), 3)
                    try:
                        monte_carlo = MonteCarlo(
                            id=f"mc-{uuid.uuid4().hex[:8]}",
                            plan_id=plan_id,
                            success_rate=success_rate,
                            iterations=1000,
                            confidence_interval=0.95,
                            median_ending_value=float(random.randint(100, 500) * 10000),
                            lowest_percentile_value=float(random.randint(10, 50) * 10000),
                            highest_percentile_value=float(random.randint(500, 1000) * 10000),
                            results_detail={
                                "years": list(range(1, 31)),
                                "percentiles": {
                                    "10": [int(random.randint(5, 10) * 100000 * (1 + 0.02*i)) for i in range(30)],
                                    "25": [int(random.randint(7, 15) * 100000 * (1 + 0.03*i)) for i in range(30)],
                                    "50": [int(random.randint(10, 20) * 100000 * (1 + 0.04*i)) for i in range(30)],
                                    "75": [int(random.randint(15, 25) * 100000 * (1 + 0.05*i)) for i in range(30)],
                                    "90": [int(random.randint(20, 30) * 100000 * (1 + 0.06*i)) for i in range(30)]
                                }
                            }
                        )
                        monte_carlos.append(monte_carlo)
                    except Exception as e:
                        logger.error(f"Error creating Monte Carlo for plan {plan_id}: {str(e)}")
                        raise
                    
                    # Create projections (30 years)
                    current_year = datetime.date.today().year
                    assets = float(random.randint(50, 200) * 10000)
                    liabilities = float(random.randint(10, 50) * 10000)
                    income = float(random.randint(10, 30) * 10000)
                    expenses = float(random.randint(5, 15) * 10000)
                    
                    for year in range(current_year, current_year + 30):
                        assets *= 1.07
                        liabilities *= 0.95
                        income *= 1.03
                        expenses *= 1.025
                        
                        try:
                            projection = Projection(
                                id=f"proj-{uuid.uuid4().hex[:8]}",
                                plan_id=plan_id,
                                year=year,
                                assets=round(assets, 2),
                                liabilities=round(liabilities, 2),
                                net_worth=round(assets - liabilities, 2),
                                income=round(income, 2),
                                expenses=round(expenses, 2),
                                cash_flow=round(income - expenses, 2)
                            )
                            projections.append(projection)
                        except Exception as e:
                            logger.error(f"Error creating projection for plan {plan_id}, year {year}: {str(e)}")
                            raise
            
            logger.info(f"Created {len(plans)} plans, {len(goals)} goals, {len(monte_carlos)} monte carlos, {len(projections)} projections")
            
            # Add to database
            for plan in plans:
                self.db.add(plan)
            
            self.db.commit()
            plan_count = len(plans)
            logger.info(f"Committed {plan_count} plans")
            
            for goal in goals:
                self.db.add(goal)
            
            self.db.commit()
            goal_count = len(goals)
            logger.info(f"Committed {goal_count} goals")
            
            for monte_carlo in monte_carlos:
                self.db.add(monte_carlo)
            
            self.db.commit()
            monte_carlo_count = len(monte_carlos)
            logger.info(f"Committed {monte_carlo_count} monte carlos")
            
            for projection in projections:
                self.db.add(projection)
            
            self.db.commit()
            projection_count = len(projections)
            logger.info(f"Committed {projection_count} projections")
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in _seed_financial_plans: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error seeding financial plans: {str(e)}")
        
        return {
            "financial_plans": plan_count,
            "goals": goal_count,
            "monte_carlo_analyses": monte_carlo_count,
            "projections": projection_count
        }
    
    def _seed_accounts(self) -> Dict[str, int]:
        """
        Seed accounts and liabilities
        """
        account_count = 0
        liability_count = 0
        account_type_count = 0
        
        try:
            # Check if account types already exist
            existing_types = self.db.query(AccountTypeModel).count()
            if existing_types > 0:
                logger.info(f"Account types already seeded ({existing_types} types exist)")
            else:
                # Create account types with UNIQUE names by including category in name
                account_types = [
                    AccountTypeModel(
                        id="acct-type-001",
                        name="Checking",
                        description="Checking account",
                        category="Asset",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-002",
                        name="Savings",
                        description="Savings account",
                        category="Asset",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-003",
                        name="Brokerage",
                        description="Brokerage account",
                        category="Asset",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-004",
                        name="Retirement",
                        description="Retirement account",
                        category="Asset",
                        tax_treatment="Tax-Deferred",
                        is_retirement=True,
                        is_qualified=True,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-005",
                        name="College Savings",
                        description="College savings account",
                        category="Asset",
                        tax_treatment="Tax-Free",
                        is_retirement=False,
                        is_qualified=True,
                        is_custodial=False,
                        is_education=True,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-006",
                        name="Health Savings",
                        description="Health savings account",
                        category="Asset",
                        tax_treatment="Tax-Free",
                        is_retirement=False,
                        is_qualified=True,
                        is_custodial=False,
                        is_education=False,
                        is_health=True
                    ),
                    AccountTypeModel(
                        id="acct-type-007",
                        name="Mortgage",
                        description="Mortgage",
                        category="Liability",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-008",
                        name="Loan",
                        description="Loan",
                        category="Liability",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-009",
                        name="Credit Card",
                        description="Credit card",
                        category="Liability",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-010",
                        name="Line of Credit",
                        description="Line of credit",
                        category="Liability",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-011",
                        name="Other Asset",  # Made unique by adding "Asset"
                        description="Other account type",
                        category="Asset",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    ),
                    AccountTypeModel(
                        id="acct-type-012",
                        name="Other Liability",  # Made unique by adding "Liability"
                        description="Other liability type",
                        category="Liability",
                        tax_treatment=None,
                        is_retirement=False,
                        is_qualified=False,
                        is_custodial=False,
                        is_education=False,
                        is_health=False
                    )
                ]
                
                # Add account types to database one by one with error handling
                for account_type in account_types:
                    try:
                        self.db.add(account_type)
                        self.db.commit()
                        account_type_count += 1
                    except IntegrityError as e:
                        self.db.rollback()
                        logger.warning(f"Account type {account_type.name} already exists, skipping")
                        continue
                
                logger.info(f"Created {account_type_count} account types")
            
            # Get clients and plans
            clients = self.db.query(Client).all()
            if not clients:
                raise HTTPException(status_code=400, detail="No clients found. Please seed clients first.")
            
            # Create accounts and liabilities
            accounts = []
            liabilities = []
            
            # Financial institutions
            banks = ["Bank of America", "Chase", "Wells Fargo", "Citibank", "US Bank", "Capital One", "TD Bank"]
            investment_firms = ["Fidelity", "Charles Schwab", "Vanguard", "TD Ameritrade", "E*TRADE", "Merrill Lynch", "Morgan Stanley"]
            
            for client in clients:
                # Get client's active plans
                plans = self.db.query(FinancialPlan).filter(
                    FinancialPlan.client_id == client.id,
                    FinancialPlan.status == "active"
                ).all()
                
                if not plans:
                    continue
                
                plan = plans[0]  # Use the first active plan
                
                # Create accounts (3-7 per client)
                num_accounts = random.randint(3, 7)
                for i in range(num_accounts):
                    # Decide account type
                    account_categories = [
                        {"type": "Checking", "institution": random.choice(banks)},
                        {"type": "Savings", "institution": random.choice(banks)},
                        {"type": "Brokerage", "institution": random.choice(investment_firms)},
                        {"type": "Retirement", "institution": random.choice(investment_firms)},
                        {"type": "College Savings", "institution": random.choice(investment_firms)},
                        {"type": "Health Savings", "institution": random.choice(banks)}
                    ]
                    
                    account_category = random.choice(account_categories)
                    ownership = random.choice(["Client", "Spouse", "Joint", "Trust"]) if client.marital_status == "Married" else random.choice(["Client", "Trust"])
                    
                    account = Account(
                        id=f"account-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        name=f"{account_category['type']} Account",
                        description=f"{ownership} {account_category['type']} account",
                        institution=account_category['institution'],
                        account_number=f"XXXX{fake.random_number(digits=4)}",
                        type=account_category['type'],
                        ownership=ownership,
                        tax_status=random.choice(["Taxable", "Tax-Deferred", "Tax-Free"]) if account_category['type'] in ["Brokerage", "Retirement", "College Savings"] else None,
                        is_external=random.choice([True, False]) if i > 2 else False
                    )
                    accounts.append(account)
                
                # Create liabilities (1-3 per client)
                num_liabilities = random.randint(1, 3)
                for i in range(num_liabilities):
                    # Decide liability type
                    liability_categories = [
                        {"type": "Mortgage", "term": 30, "interest": round(random.uniform(0.03, 0.045), 4), "amount": random.randint(20, 50) * 10000},
                        {"type": "Loan", "term": 5, "interest": round(random.uniform(0.04, 0.08), 4), "amount": random.randint(1, 3) * 10000},
                        {"type": "Credit Card", "term": None, "interest": round(random.uniform(0.15, 0.25), 4), "amount": random.randint(2, 10) * 1000},
                        {"type": "Line of Credit", "term": None, "interest": round(random.uniform(0.06, 0.12), 4), "amount": random.randint(1, 5) * 10000}
                    ]
                    
                    liability_category = random.choice(liability_categories)
                    ownership = random.choice(["Client", "Spouse", "Joint"]) if client.marital_status == "Married" else "Client"
                    
                    # Calculate start and end dates for term-based liabilities
                    if liability_category["term"]:
                        start_date = fake.date_between(start_date="-10y", end_date="today")
                        end_date = start_date + datetime.timedelta(days=365 * liability_category["term"])
                    else:
                        start_date = fake.date_between(start_date="-5y", end_date="today")
                        end_date = None
                    
                    # Calculate payment amount for term-based liabilities
                    if liability_category["term"]:
                        # Simple calculation (not exact amortization)
                        payment_amount = liability_category["amount"] * (liability_category["interest"] / 12) / (1 - (1 + liability_category["interest"] / 12) ** (-12 * liability_category["term"]))
                        payment_frequency = "Monthly"
                    else:
                        payment_amount = liability_category["amount"] * 0.03
                        payment_frequency = "Monthly"
                    
                    liability = Liability(
                        id=f"liability-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        plan_id=plan.id,
                        name=f"{liability_category['type']}",
                        description=f"{ownership} {liability_category['type']}",
                        type=liability_category['type'],
                        balance=liability_category['amount'],
                        original_balance=liability_category['amount'] * random.uniform(1.1, 1.5) if liability_category["term"] else None,
                        interest_rate=liability_category['interest'],
                        payment_amount=round(payment_amount, 2),
                        payment_frequency=payment_frequency,
                        start_date=start_date,
                        end_date=end_date,
                        ownership=ownership
                    )
                    liabilities.append(liability)
            
            # Add to database
            for account in accounts:
                self.db.add(account)
            
            self.db.commit()
            account_count = len(accounts)
            
            for liability in liabilities:
                self.db.add(liability)
            
            self.db.commit()
            liability_count = len(liabilities)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error seeding accounts: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error seeding accounts: {str(e)}")
        
        return {
            "accounts": account_count,
            "liabilities": liability_count,
            "account_types": account_type_count
        }
    
    def _seed_assets(self) -> Dict[str, int]:
        """
        Seed assets, asset classes, allocations, securities, and holdings
        """
        asset_count = 0
        asset_class_count = 0
        
        try:
            # Get clients, plans, and accounts
            clients = self.db.query(Client).all()
            if not clients:
                raise HTTPException(status_code=400, detail="No clients found. Please seed clients first.")
            
            # Check if asset classes already exist
            existing_classes = self.db.query(AssetClass).count()
            if existing_classes > 0:
                logger.info(f"Asset classes already seeded ({existing_classes} classes exist)")
            else:
                # Create asset classes
                asset_classes = [
                    AssetClass(id="asset-class-001", name="Equity"),
                    AssetClass(id="asset-class-002", name="Fixed Income"),
                    AssetClass(id="asset-class-003", name="Cash"),
                    AssetClass(id="asset-class-004", name="Real Estate"),
                    AssetClass(id="asset-class-005", name="Alternative"),
                    # Subcategories
                    AssetClass(id="asset-class-101", name="US Large Cap", parent_id="asset-class-001"),
                    AssetClass(id="asset-class-102", name="US Mid Cap", parent_id="asset-class-001"),
                    AssetClass(id="asset-class-103", name="US Small Cap", parent_id="asset-class-001"),
                    AssetClass(id="asset-class-104", name="International Developed", parent_id="asset-class-001"),
                    AssetClass(id="asset-class-105", name="Emerging Markets", parent_id="asset-class-001"),
                    AssetClass(id="asset-class-201", name="US Government", parent_id="asset-class-002"),
                    AssetClass(id="asset-class-202", name="Corporate", parent_id="asset-class-002"),
                    AssetClass(id="asset-class-203", name="Municipal", parent_id="asset-class-002"),
                    AssetClass(id="asset-class-204", name="International", parent_id="asset-class-002"),
                    AssetClass(id="asset-class-205", name="High Yield", parent_id="asset-class-002"),
                    AssetClass(id="asset-class-301", name="Cash & Equivalents", parent_id="asset-class-003"),
                    AssetClass(id="asset-class-401", name="Residential", parent_id="asset-class-004"),
                    AssetClass(id="asset-class-402", name="Commercial", parent_id="asset-class-004"),
                    AssetClass(id="asset-class-403", name="REITs", parent_id="asset-class-004"),
                    AssetClass(id="asset-class-501", name="Commodities", parent_id="asset-class-005"),
                    AssetClass(id="asset-class-502", name="Private Equity", parent_id="asset-class-005"),
                    AssetClass(id="asset-class-503", name="Hedge Funds", parent_id="asset-class-005")
                ]
                
                # Add asset classes to database
                for asset_class in asset_classes:
                    self.db.add(asset_class)
                
                self.db.commit()
                asset_class_count = len(asset_classes)
            
            # Create assets
            assets = []
            
            for client in clients:
                # Get client's active plans
                plans = self.db.query(FinancialPlan).filter(
                    FinancialPlan.client_id == client.id,
                    FinancialPlan.status == "active"
                ).all()
                
                if not plans:
                    continue
                
                plan = plans[0]  # Use the first active plan
                
                # Get client's accounts
                accounts = self.db.query(Account).filter(Account.client_id == client.id).all()
                
                # Create primary residence
                primary_residence = Asset(
                    id=f"asset-{uuid.uuid4().hex[:8]}",
                    client_id=client.id,
                    plan_id=plan.id,
                    name="Primary Residence",
                    description="Primary home",
                    type="Real Estate",
                    value=random.randint(25, 100) * 10000,
                    basis=random.randint(20, 80) * 10000,
                    growth_rate=round(random.uniform(0.02, 0.04), 4),
                    ownership="Joint" if client.marital_status == "Married" else "Client"
                )
                assets.append(primary_residence)
                
                # Create financial assets based on accounts
                for account in accounts:
                    if account.type in ["Checking", "Savings", "Health Savings"]:
                        # Cash assets
                        asset_value = random.randint(5, 50) * 1000
                        asset = Asset(
                            id=f"asset-{uuid.uuid4().hex[:8]}",
                            client_id=client.id,
                            plan_id=plan.id,
                            name=account.name,
                            description=f"Cash asset in {account.name}",
                            type="Cash",
                            value=asset_value,
                            basis=asset_value,
                            growth_rate=round(random.uniform(0.001, 0.02), 4),
                            ownership=account.ownership,
                            account_id=account.id
                        )
                        assets.append(asset)
                    elif account.type in ["Brokerage", "Retirement", "College Savings"]:
                        # Investment assets
                        asset_value = random.randint(10, 500) * 1000
                        asset = Asset(
                            id=f"asset-{uuid.uuid4().hex[:8]}",
                            client_id=client.id,
                            plan_id=plan.id,
                            name=account.name,
                            description=f"Investment asset in {account.name}",
                            type="Investment",
                            value=asset_value,
                            basis=asset_value * random.uniform(0.7, 1.0),
                            growth_rate=round(random.uniform(0.05, 0.08), 4),
                            ownership=account.ownership,
                            account_id=account.id
                        )
                        assets.append(asset)
                
                # Create other assets (1-3 per client)
                num_other_assets = random.randint(1, 3)
                for i in range(num_other_assets):
                    asset_types = [
                        {"type": "Vehicle", "value": random.randint(2, 5) * 10000, "growth": round(random.uniform(-0.1, 0.0), 4)},
                        {"type": "Business", "value": random.randint(20, 100) * 10000, "growth": round(random.uniform(0.05, 0.15), 4)},
                        {"type": "Personal Property", "value": random.randint(5, 20) * 10000, "growth": round(random.uniform(0.0, 0.02), 4)}
                    ]
                    
                    asset_type = random.choice(asset_types)
                    asset = Asset(
                        id=f"asset-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        plan_id=plan.id,
                        name=f"{asset_type['type']}",
                        description=f"Client {asset_type['type']}",
                        type=asset_type['type'],
                        value=asset_type['value'],
                        basis=asset_type['value'] * random.uniform(0.8, 1.2),
                        growth_rate=asset_type['growth'],
                        ownership=random.choice(["Client", "Spouse", "Joint"]) if client.marital_status == "Married" else "Client"
                    )
                    assets.append(asset)
            
            # Add assets to database
            for asset in assets:
                self.db.add(asset)
            
            self.db.commit()
            asset_count = len(assets)
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding assets: {str(e)}")
        
        return {"assets": asset_count, "asset_classes": asset_class_count}
    
    def _seed_spending(self) -> Dict[str, int]:
        """
        Seed income sources, expenses, budgets, and budget categories
        """
        income_count = 0
        expense_count = 0
        
        try:
            # Get clients and plans
            clients = self.db.query(Client).all()
            if not clients:
                raise HTTPException(status_code=400, detail="No clients found. Please seed clients first.")
            
            # Create income and expenses
            incomes = []
            expenses = []
            
            for client in clients:
                # Get client's active plans
                plans = self.db.query(FinancialPlan).filter(
                    FinancialPlan.client_id == client.id,
                    FinancialPlan.status == "active"
                ).all()
                
                if not plans:
                    continue
                
                plan = plans[0]  # Use the first active plan
                
                # Get workspace_id and user IDs
                workspace_id = getattr(plan, 'workspace_id', 'workspace-001')
                created_by = getattr(plan, 'created_by', 'system')
                updated_by = getattr(plan, 'updated_by', 'system')
                
                # Create income sources (1-4 per client)
                # Primary salary
                annual_amount = random.randint(5, 20) * 10000
                primary_income = Income(
                    id=f"income-{uuid.uuid4().hex[:8]}",
                    workspace_id=workspace_id,
                    client_id=client.id,
                    plan_id=plan.id,
                    created_by=created_by,
                    updated_by=updated_by,
                    name="Primary Salary",
                    description="Primary employment income",
                    income_type="Salary",
                    status="active",
                    annual_amount=annual_amount,
                    monthly_amount=annual_amount / 12,
                    amount_per_payment=annual_amount / 12,
                    frequency="Monthly",
                    start_date=fake.date_between(start_date="-10y", end_date="today"),
                    end_date=fake.date_between(start_date="+15y", end_date="+30y"),
                    growth_rate=round(random.uniform(0.02, 0.04), 4),
                    taxable=True
                )
                incomes.append(primary_income)
                
                # Spouse salary if married
                if client.marital_status == "Married":
                    annual_amount = random.randint(5, 15) * 10000
                    spouse_income = Income(
                        id=f"income-{uuid.uuid4().hex[:8]}",
                        workspace_id=workspace_id,
                        client_id=client.id,
                        plan_id=plan.id,
                        created_by=created_by,
                        updated_by=updated_by,
                        name="Spouse Salary",
                        description="Spouse employment income",
                        income_type="Salary",
                        status="active",
                        annual_amount=annual_amount,
                        monthly_amount=annual_amount / 12,
                        amount_per_payment=annual_amount / 12,
                        frequency="Monthly",
                        start_date=fake.date_between(start_date="-10y", end_date="today"),
                        end_date=fake.date_between(start_date="+15y", end_date="+30y"),
                        growth_rate=round(random.uniform(0.02, 0.04), 4),
                        taxable=True
                    )
                    incomes.append(spouse_income)
                
                # Additional income sources (0-2)
                num_additional_income = random.randint(0, 2)
                for i in range(num_additional_income):
                    income_types = [
                        {"type": "Bonus", "frequency": "Annual", "amount": random.randint(1, 5) * 10000},
                        {"type": "RentalIncome", "frequency": "Monthly", "amount": random.randint(1, 4) * 1000},
                        {"type": "Investment", "frequency": "Annual", "amount": random.randint(2, 10) * 1000},
                        {"type": "SelfEmployment", "frequency": "Monthly", "amount": random.randint(3, 8) * 1000}
                    ]
                    
                    income_type = random.choice(income_types)
                    base_amount = income_type['amount']
                    
                    # Calculate proper amounts based on frequency
                    if income_type['frequency'] == "Monthly":
                        monthly_amount = base_amount
                        annual_amount = monthly_amount * 12
                        amount_per_payment = monthly_amount
                    else:  # Annual
                        annual_amount = base_amount
                        monthly_amount = annual_amount / 12
                        amount_per_payment = annual_amount
                    
                    income = Income(
                        id=f"income-{uuid.uuid4().hex[:8]}",
                        workspace_id=workspace_id,
                        client_id=client.id,
                        plan_id=plan.id,
                        created_by=created_by,
                        updated_by=updated_by,
                        name=f"{income_type['type']} Income",
                        description=f"{income_type['type']} income",
                        income_type=income_type['type'],
                        status="active",
                        annual_amount=annual_amount,
                        monthly_amount=monthly_amount,
                        amount_per_payment=amount_per_payment,
                        frequency=income_type['frequency'],
                        start_date=fake.date_between(start_date="-5y", end_date="today"),
                        end_date=fake.date_between(start_date="+10y", end_date="+20y") if random.random() < 0.7 else None,
                        growth_rate=round(random.uniform(0.01, 0.03), 4),
                        taxable=True
                    )
                    incomes.append(income)
                
                # Future income sources (Social Security, etc.)
                future_income_types = [
                    {"type": "SocialSecurity", "age": random.randint(67, 70)},
                    {"type": "SocialSecurity", "age": random.randint(67, 70)} if client.marital_status == "Married" else None,
                    {"type": "Pension", "age": random.randint(62, 65)},
                    {"type": "Pension", "age": random.randint(62, 65)} if client.marital_status == "Married" else None
                ]
                
                for income_type in future_income_types:
                    if not income_type:
                        continue
                    
                    # Calculate start date based on age
                    dob = client.date_of_birth
                    start_year = dob.year + income_type["age"]
                    start_date = datetime.date(start_year, dob.month, dob.day)
                    
                    if start_date < datetime.date.today():
                        # If already started, use today
                        start_date = datetime.date.today()
                    
                    annual_amount = random.randint(1, 4) * 10000 if income_type['type'] == "SocialSecurity" else random.randint(2, 6) * 10000
                    
                    income = Income(
                        id=f"income-{uuid.uuid4().hex[:8]}",
                        workspace_id=workspace_id,
                        client_id=client.id,
                        plan_id=plan.id,
                        created_by=created_by,
                        updated_by=updated_by,
                        name=f"{income_type['type']}",
                        description=f"{income_type['type']} income",
                        income_type=income_type['type'],
                        status="active",
                        annual_amount=annual_amount,
                        monthly_amount=annual_amount / 12,
                        amount_per_payment=annual_amount / 12,
                        frequency="Monthly",
                        start_date=start_date,
                        end_date=None,
                        growth_rate=round(random.uniform(0.01, 0.025), 4),
                        taxable=True if income_type['type'] == "Pension" else random.choice([True, False])
                    )
                    incomes.append(income)
                
                # Create expenses (6-12 per client)
                expense_categories = [
                    {"category": "Housing", "essential": True, "amount": random.randint(1, 3) * 1000},
                    {"category": "Transportation", "essential": True, "amount": random.randint(3, 8) * 100},
                    {"category": "Food", "essential": True, "amount": random.randint(5, 12) * 100},
                    {"category": "Healthcare", "essential": True, "amount": random.randint(2, 6) * 100},
                    {"category": "Entertainment", "essential": False, "amount": random.randint(2, 5) * 100},
                    {"category": "Debt", "essential": True, "amount": random.randint(5, 15) * 100},
                    {"category": "Education", "essential": False, "amount": random.randint(2, 5) * 100},
                    {"category": "Travel", "essential": False, "amount": random.randint(3, 10) * 100},
                    {"category": "Insurance", "essential": True, "amount": random.randint(2, 5) * 100},
                    {"category": "Personal", "essential": False, "amount": random.randint(2, 4) * 100},
                    {"category": "Utilities", "essential": True, "amount": random.randint(1, 3) * 100},
                    {"category": "Gifts & Donations", "essential": False, "amount": random.randint(1, 5) * 100}
                ]
                
                for expense_category in expense_categories:
                    monthly_amount = expense_category["amount"]
                    annual_amount = monthly_amount * 12
                    
                    expense = Expense(
                        id=f"expense-{uuid.uuid4().hex[:8]}",
                        workspace_id=workspace_id,
                        client_id=client.id,
                        plan_id=plan.id,
                        created_by=created_by,
                        updated_by=updated_by,
                        name=expense_category["category"],
                        description=f"{expense_category['category']} expenses",
                        category=expense_category["category"],
                        status="active",
                        annual_amount=annual_amount,
                        monthly_amount=monthly_amount,
                        amount_per_payment=monthly_amount,
                        frequency="Monthly",
                        growth_rate=round(random.uniform(0.02, 0.03), 4),
                        is_discretionary=not expense_category["essential"],
                        is_goal=False
                    )
                    expenses.append(expense)
                
                # Get client's goals to create goal-related expenses
                goals = self.db.query(Goal).filter(Goal.plan_id == plan.id).all()
                
                for goal in goals:
                    if goal.name in ["Retirement", "Legacy"]:
                        # These are typically handled separately
                        continue
                    
                    # Create a goal-related expense
                    monthly_amount = goal.target_amount / 12
                    annual_amount = monthly_amount * 12
                    
                    expense = Expense(
                        id=f"expense-{uuid.uuid4().hex[:8]}",
                        workspace_id=workspace_id,
                        client_id=client.id,
                        plan_id=plan.id,
                        created_by=created_by,
                        updated_by=updated_by,
                        name=goal.name,
                        description=goal.description,
                        category="Education" if goal.name == "College Education" else goal.category,
                        status="active",
                        annual_amount=annual_amount,
                        monthly_amount=monthly_amount,
                        amount_per_payment=monthly_amount,
                        frequency="Monthly",
                        start_date=datetime.date.today(),
                        end_date=goal.target_date,
                        growth_rate=0.03,
                        is_discretionary=False,
                        is_goal=True,
                        goal_id=goal.id
                    )
                    expenses.append(expense)
            
            # Add to database
            for income in incomes:
                self.db.add(income)
            
            self.db.commit()
            income_count = len(incomes)
            
            for expense in expenses:
                self.db.add(expense)
            
            self.db.commit()
            expense_count = len(expenses)
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding spending: {str(e)}")
        
        return {"income_sources": income_count, "expenses": expense_count}
    
    def _seed_file_types(self) -> Dict[str, int]:
        """
        Seed file types for document management
        """
        file_type_count = 0
        
        try:
            # Check if file types already exist
            from models.documents import FileType
            
            existing_types = self.db.query(FileType).count()
            if existing_types > 0:
                logger.info(f"File types already seeded ({existing_types} types exist)")
                return {"file_types": 0}
            
            # Create common file types
            file_types = [
                {
                    'id': 'ft-001',
                    'name': 'PDF Document',
                    'extension': '.pdf',
                    'mime_type': 'application/pdf',
                    'category': 'document',
                    'icon': 'file-pdf',
                    'max_size': 10485760,  # 10MB
                    'is_active': True
                },
                {
                    'id': 'ft-002',
                    'name': 'Word Document',
                    'extension': '.docx',
                    'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'category': 'document',
                    'icon': 'file-word',
                    'max_size': 10485760,
                    'is_active': True
                },
                {
                    'id': 'ft-003',
                    'name': 'Excel Spreadsheet',
                    'extension': '.xlsx',
                    'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'category': 'spreadsheet',
                    'icon': 'file-excel',
                    'max_size': 10485760,
                    'is_active': True
                },
                {
                    'id': 'ft-004',
                    'name': 'PowerPoint Presentation',
                    'extension': '.pptx',
                    'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'category': 'presentation',
                    'icon': 'file-powerpoint',
                    'max_size': 20971520,  # 20MB
                    'is_active': True
                },
                {
                    'id': 'ft-005',
                    'name': 'JPEG Image',
                    'extension': '.jpg',
                    'mime_type': 'image/jpeg',
                    'category': 'image',
                    'icon': 'file-image',
                    'max_size': 5242880,  # 5MB
                    'is_active': True
                },
                {
                    'id': 'ft-006',
                    'name': 'PNG Image',
                    'extension': '.png',
                    'mime_type': 'image/png',
                    'category': 'image',
                    'icon': 'file-image',
                    'max_size': 5242880,
                    'is_active': True
                },
                {
                    'id': 'ft-007',
                    'name': 'Text File',
                    'extension': '.txt',
                    'mime_type': 'text/plain',
                    'category': 'document',
                    'icon': 'file-text',
                    'max_size': 1048576,  # 1MB
                    'is_active': True
                },
                {
                    'id': 'ft-008',
                    'name': 'ZIP Archive',
                    'extension': '.zip',
                    'mime_type': 'application/zip',
                    'category': 'archive',
                    'icon': 'file-archive',
                    'max_size': 52428800,  # 50MB
                    'is_active': True
                }
            ]
            
            # Add file types to database
            for ft_data in file_types:
                try:
                    file_type = FileType(**ft_data)
                    self.db.add(file_type)
                    self.db.commit()
                    file_type_count += 1
                except IntegrityError as e:
                    self.db.rollback()
                    logger.warning(f"File type {ft_data['name']} already exists, skipping")
                    continue
            
            logger.info(f"Created {file_type_count} file types")
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error seeding file types: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error seeding file types: {str(e)}")
        
        return {"file_types": file_type_count}
    
    def _seed_documents(self) -> Dict[str, int]:
        """
        Seed vault documents, notes, tasks, and alerts
        """
        document_count = 0
        note_count = 0
        task_count = 0
        alert_count = 0
        
        try:
            # Get clients, advisors, and plans
            clients = self.db.query(Client).all()
            if not clients:
                raise HTTPException(status_code=400, detail="No clients found. Please seed clients first.")
            
            advisors = self.db.query(User).join(User.roles).filter(Role.name == "Advisor").all()
            if not advisors:
                raise HTTPException(status_code=400, detail="No advisors found. Please seed users first.")
            
            # Create documents, notes, tasks, and alerts
            documents = []
            notes = []
            tasks = []
            alerts = []
            
            for client in clients:
                # Get client's owning advisor
                advisor = self.db.query(User).filter(User.id == client.owning_advisor).first()
                if not advisor:
                    advisor = random.choice(advisors)
                
                # Create documents (3-7 per client)
                num_documents = random.randint(3, 7)
                for i in range(num_documents):
                    document_types = [
                        {"name": "Financial Plan", "file_type": ".pdf", "size": random.randint(1, 5) * 1000000},
                        {"name": "Investment Policy Statement", "file_type": ".docx", "size": random.randint(100, 500) * 1000},
                        {"name": "Tax Return", "file_type": ".pdf", "size": random.randint(1, 3) * 1000000},
                        {"name": "Estate Planning Documents", "file_type": ".pdf", "size": random.randint(2, 8) * 1000000},
                        {"name": "Insurance Policies", "file_type": ".pdf", "size": random.randint(1, 3) * 1000000},
                        {"name": "Budget Worksheet", "file_type": ".xlsx", "size": random.randint(50, 200) * 1000},
                        {"name": "Retirement Analysis", "file_type": ".pdf", "size": random.randint(1, 3) * 1000000},
                        {"name": "College Planning", "file_type": ".pdf", "size": random.randint(500, 1500) * 1000},
                        {"name": "Client Agreement", "file_type": ".pdf", "size": random.randint(200, 500) * 1000}
                    ]
                    
                    document_type = random.choice(document_types)
                    
                    document = VaultDocument(
                        id=f"doc-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        name=f"{document_type['name']} {fake.date_this_year().year}",
                        description=f"{document_type['name']} for {client.first_name} {client.last_name}",
                        file_name=f"{document_type['name'].lower().replace(' ', '_')}_{fake.date_this_year().year}{document_type['file_type']}",
                        file_type=document_type['file_type'],  # Now uses extension like ".pdf"
                        file_size=document_type['size'],
                        mime_type=self._get_mime_type(document_type['file_type']),
                        content=None,
                        created_by=advisor.id,
                        created_at=fake.date_time_between(start_date="-1y", end_date="now")
                    )
                    documents.append(document)
                
                # Create notes (3-10 per client)
                num_notes = random.randint(3, 10)
                for i in range(num_notes):
                    note_titles = [
                        "Initial Meeting",
                        "Portfolio Review",
                        "Risk Assessment",
                        "Goal Planning",
                        "Tax Planning",
                        "Estate Planning",
                        "Insurance Review",
                        "Retirement Planning",
                        "College Planning",
                        "Investment Strategy",
                        "Client Concerns",
                        "Market Outlook Discussion",
                        "Annual Review"
                    ]
                    
                    note_title = random.choice(note_titles)
                    
                    note = Note(
                        id=f"note-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        title=note_title,
                        content=fake.paragraph(nb_sentences=5),
                        created_by=advisor.id,
                        created_at=fake.date_time_between(start_date="-1y", end_date="now")
                    )
                    notes.append(note)
                
                # Create tasks (2-5 per client)
                num_tasks = random.randint(2, 5)
                for i in range(num_tasks):
                    task_titles = [
                        "Update Risk Tolerance",
                        "Portfolio Rebalancing",
                        "Required Minimum Distribution",
                        "Insurance Review",
                        "Tax Planning Session",
                        "Estate Plan Update",
                        "College Funding Strategy",
                        "Beneficiary Review",
                        "Investment Strategy Review",
                        "Budget Review",
                        "Debt Reduction Plan",
                        "Social Security Analysis",
                        "Annual Review Meeting"
                    ]
                    
                    task_title = random.choice(task_titles)
                    due_date = fake.date_between(start_date="today", end_date="+3m")
                    priority = random.choice(["High", "Medium", "Low"])
                    status = random.choice(["Open", "In Progress", "Completed"])
                    assigned_to = advisor.id
                    
                    task = Task(
                        id=f"task-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        title=task_title,
                        description=fake.paragraph(nb_sentences=2),
                        due_date=due_date,
                        priority=priority,
                        status=status,
                        assigned_to=assigned_to,
                        created_by=advisor.id,
                        created_at=fake.date_time_between(start_date="-3m", end_date="now")
                    )
                    tasks.append(task)
                
                # Create client alerts (0-2 per client)
                num_alerts = random.randint(0, 2)
                for i in range(num_alerts):
                    alert_titles = [
                        "Required Minimum Distribution Due",
                        "Portfolio Drift",
                        "Review Meeting Overdue",
                        "Cash Balance High",
                        "Market Volatility Impact",
                        "Goal Progress Warning",
                        "Document Update Needed",
                        "Beneficiary Update Required",
                        "Tax Strategy Opportunity",
                        "Insurance Coverage Gap"
                    ]
                    
                    alert_title = random.choice(alert_titles)
                    
                    alert = Alert(
                        id=f"alert-{uuid.uuid4().hex[:8]}",
                        client_id=client.id,
                        title=alert_title,
                        description=fake.paragraph(nb_sentences=1),
                        type="Client",
                        severity=random.choice(["Info", "Warning", "Critical"]),
                        status="Active",
                        created_at=fake.date_time_between(start_date="-1m", end_date="now")
                    )
                    alerts.append(alert)
            
            # Create system alerts (2-5)
            num_system_alerts = random.randint(2, 5)
            for i in range(num_system_alerts):
                system_alert_titles = [
                    "System Maintenance",
                    "New Feature Available",
                    "Security Update",
                    "Regulatory Change Notice",
                    "API Update Scheduled",
                    "Data Backup Completed",
                    "Performance Optimization",
                    "User Interface Update"
                ]
                
                alert_title = random.choice(system_alert_titles)
                
                alert = Alert(
                    id=f"alert-system-{uuid.uuid4().hex[:8]}",
                    client_id=None,
                    title=alert_title,
                    description=fake.paragraph(nb_sentences=2),
                    type="System",
                    severity="Info",
                    status="Active",
                    created_at=fake.date_time_between(start_date="-1m", end_date="now")
                )
                alerts.append(alert)
            
            # Add to database
            for document in documents:
                self.db.add(document)
            
            self.db.commit()
            document_count = len(documents)
            
            for note in notes:
                self.db.add(note)
            
            self.db.commit()
            note_count = len(notes)
            
            for task in tasks:
                self.db.add(task)
            
            self.db.commit()
            task_count = len(tasks)
            
            for alert in alerts:
                self.db.add(alert)
            
            self.db.commit()
            alert_count = len(alerts)
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error seeding documents: {str(e)}")
        
        return {
            "vault_documents": document_count,
            "notes": note_count,
            "tasks": task_count,
            "alerts": alert_count
        }
    
    def _get_mime_type(self, file_type: str) -> str:
        """
        Get MIME type for file type extension
        """
        # Remove dot if present for lookup
        ext = file_type.lower().replace('.', '').upper()
        
        mime_types = {
            "PDF": "application/pdf",
            "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "PPTX": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "JPG": "image/jpeg",
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "ZIP": "application/zip",
            "TXT": "text/plain"
        }
        
        return mime_types.get(ext, "application/octet-stream")
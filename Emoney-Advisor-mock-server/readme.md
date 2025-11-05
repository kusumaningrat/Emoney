# eMoney Advisor Mock Server

A FastAPI-based mock implementation of eMoney Advisor APIs with clean architecture using factory pattern and base handler classes, designed for financial planning and wealth management functionality.

## 🏗️ Architecture

```
emoney-mock-server/
├── main.py                    # FastAPI application entry point
├── database.py                # SQLAlchemy models with all entity types
├── dependencies.py            # Authentication validation
├── seeder.py                  # Sample data generator with Faker
├── docker-compose.yml         # PostgreSQL + FastAPI services
├── Dockerfile                 # Container configuration
├── handlers/
│   ├── __init__.py            # Handler exports
│   ├── base_handler.py        # Abstract base handler class
│   ├── entity_factory.py      # Factory function for handlers
│   │
│   ├── # Client & Relationship Management Service (Port 4731)
│   ├── client_handler.py      # Client entity handler
│   ├── contact_handler.py     # Contact entity handler
│   ├── household_handler.py   # Household entity handler
│   ├── relationship_handler.py # Relationship entity handler
│   │
│   ├── # Financial Planning Service (Port 4732)
│   ├── financial_plan_handler.py # FinancialPlan entity handler
│   ├── goal_handler.py        # Goal entity handler
│   ├── scenario_handler.py    # Scenario entity handler
│   ├── cash_flow_handler.py   # CashFlow entity handler
│   │
│   ├── # Account Management Service (Port 4733)
│   ├── account_handler.py     # Account entity handler
│   ├── account_type_handler.py # AccountType entity handler
│   ├── investment_handler.py  # Investment entity handler
│   ├── liability_handler.py   # Liability entity handler
│   │
│   ├── # Asset Management Service (Port 4734)
│   ├── asset_handler.py       # Asset entity handler
│   ├── asset_class_handler.py # AssetClass entity handler
│   ├── allocation_handler.py  # Allocation entity handler
│   ├── security_handler.py    # Security entity handler
│   │
│   ├── # Spending & Budget Management Service (Port 4735)
│   ├── spending_handler.py    # Spending entity handler
│   ├── budget_handler.py      # Budget entity handler
│   ├── expense_handler.py     # Expense entity handler
│   ├── income_handler.py      # Income entity handler
│   │
│   ├── # Estate Planning Service (Port 4736)
│   ├── estate_handler.py      # Estate entity handler
│   ├── will_handler.py        # Will entity handler
│   ├── trust_handler.py       # Trust entity handler
│   ├── beneficiary_handler.py # Beneficiary entity handler
│   │
│   ├── # Retirement Planning Service (Port 4737)
│   ├── retirement_plan_handler.py # RetirementPlan entity handler
│   ├── pension_handler.py     # Pension entity handler
│   ├── social_security_handler.py # SocialSecurity entity handler
│   ├── rmd_handler.py         # RMD entity handler
│   │
│   ├── # Insurance Planning Service (Port 4738)
│   ├── insurance_handler.py   # Insurance entity handler
│   ├── policy_handler.py      # Policy entity handler
│   ├── coverage_handler.py    # Coverage entity handler
│   ├── premium_handler.py     # Premium entity handler
│   │
│   ├── # Tax Planning Service (Port 4739)
│   ├── tax_plan_handler.py    # TaxPlan entity handler
│   ├── tax_bracket_handler.py # TaxBracket entity handler
│   ├── deduction_handler.py   # Deduction entity handler
│   ├── credit_handler.py      # Credit entity handler
│   │
│   ├── # Document Management Service (Port 4708)
│   ├── document_handler.py    # Document entity handler
│   ├── vault_handler.py       # Vault entity handler
│   ├── file_type_handler.py   # FileType entity handler
│   ├── attachment_handler.py  # Attachment entity handler
│   │
│   └── # User & Access Management Service (Port 4709)
│       ├── user_handler.py    # User entity handler
│       ├── role_handler.py    # Role entity handler
│       ├── permission_handler.py # Permission entity handler
│       ├── advisor_handler.py # Advisor entity handler
│       └── firm_handler.py    # Firm entity handler
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Start with sample data
docker-compose up -d

# Or rebuild and start fresh
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Option 2: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set database URL (optional - defaults to SQLite)
export DATABASE_URL="postgresql://emoney:postgres@localhost:5432/emoney_mock"

# Run the server
python main.py

# Generate sample data
python seeder.py --clear
```

Server starts on `http://localhost:6100`

### 3. Test the API
```bash
# Test with curl
curl -X GET "http://localhost:6100/v1/entities?type=Client" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Health check
curl -X GET "http://localhost:6100/health"
```

## 📡 API Endpoint

### GET /v1/entities

**Description:** Retrieve entities with filtering and pagination support.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | No | Entity type (see supported types below) |
| `q` | string | No | Query filter (e.g., `status==active`) |
| `limit` | integer | No | Number of results (default: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |
| `options` | string | No | Response options (`count` for count only) |
| `firm_id` | string | No | Filter by firm identifier |

**Required Headers:**
```
X-API-Key: your-api-key
X-API-Secret: your-api-secret
```

## 🎯 Supported Entity Types

### Client & Relationship Management Service (Port 4731)
- **Client** - Primary client record with demographics and status
- **Contact** - Contact information and communication preferences
- **Household** - Household grouping and relationships
- **Relationship** - Client relationships and dependencies

### Financial Planning Service (Port 4732)
- **FinancialPlan** - Comprehensive financial planning data
- **Goal** - Financial goals and objectives
- **Scenario** - Planning scenarios and what-if analysis
- **CashFlow** - Cash flow projections and analysis

### Account Management Service (Port 4733)
- **Account** - Financial account information
- **AccountType** - Account classification and types
- **Investment** - Investment holdings and positions
- **Liability** - Debt and liability tracking

### Asset Management Service (Port 4734)
- **Asset** - Asset inventory and valuation
- **AssetClass** - Asset classification structure
- **Allocation** - Portfolio allocation strategies
- **Security** - Security master data and pricing

### Spending & Budget Management Service (Port 4735)
- **Spending** - Spending transactions and patterns
- **Budget** - Budget planning and tracking
- **Expense** - Expense categorization and management
- **Income** - Income sources and tracking

### Estate Planning Service (Port 4736)
- **Estate** - Estate planning overview
- **Will** - Will documentation and directives
- **Trust** - Trust structures and beneficiaries
- **Beneficiary** - Beneficiary designations

### Retirement Planning Service (Port 4737)
- **RetirementPlan** - Retirement planning scenarios
- **Pension** - Pension benefits and projections
- **SocialSecurity** - Social Security benefit calculations
- **RMD** - Required minimum distribution tracking

### Insurance Planning Service (Port 4738)
- **Insurance** - Insurance portfolio overview
- **Policy** - Insurance policy details
- **Coverage** - Coverage amounts and types
- **Premium** - Premium payment tracking

### Tax Planning Service (Port 4739)
- **TaxPlan** - Tax planning strategies
- **TaxBracket** - Tax bracket analysis
- **Deduction** - Tax deduction tracking
- **Credit** - Tax credit management

### Document Management Service (Port 4708)
- **Document** - Document storage and metadata
- **Vault** - Secure document vault
- **FileType** - Document classification
- **Attachment** - File attachments and links

### User & Access Management Service (Port 4709)
- **User** - System users and authentication
- **Role** - Role-based access control
- **Permission** - Permission definitions
- **Advisor** - Financial advisor profiles
- **Firm** - Firm/organization management

## 📝 API Examples

### Client & Relationship Management
```bash
# Get all active clients
curl -X GET "http://localhost:6100/v1/entities?type=Client&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get household members
curl -X GET "http://localhost:6100/v1/entities?type=Household&q=household_id==HH001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get client contacts
curl -X GET "http://localhost:6100/v1/entities?type=Contact&q=client_id==CLIENT001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Financial Planning
```bash
# Get financial plans by status
curl -X GET "http://localhost:6100/v1/entities?type=FinancialPlan&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get retirement goals
curl -X GET "http://localhost:6100/v1/entities?type=Goal&q=goal_type==retirement" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get planning scenarios
curl -X GET "http://localhost:6100/v1/entities?type=Scenario&q=plan_id==PLAN001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Account Management
```bash
# Get investment accounts
curl -X GET "http://localhost:6100/v1/entities?type=Account&q=account_type==investment" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get active liabilities
curl -X GET "http://localhost:6100/v1/entities?type=Liability&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get investment holdings
curl -X GET "http://localhost:6100/v1/entities?type=Investment&q=account_id==ACC001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Asset Management
```bash
# Get asset allocation
curl -X GET "http://localhost:6100/v1/entities?type=Allocation&q=portfolio_id==PORT001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get equity securities
curl -X GET "http://localhost:6100/v1/entities?type=Security&q=security_type==equity" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get real estate assets
curl -X GET "http://localhost:6100/v1/entities?type=Asset&q=asset_class==real_estate" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Spending & Budget Management
```bash
# Get monthly expenses
curl -X GET "http://localhost:6100/v1/entities?type=Expense&q=frequency==monthly" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get annual budget
curl -X GET "http://localhost:6100/v1/entities?type=Budget&q=budget_year==2024" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get income sources
curl -X GET "http://localhost:6100/v1/entities?type=Income&q=income_type==salary" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Estate Planning
```bash
# Get trust beneficiaries
curl -X GET "http://localhost:6100/v1/entities?type=Beneficiary&q=trust_id==TRUST001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get estate plans
curl -X GET "http://localhost:6100/v1/entities?type=Estate&q=status==complete" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get wills by client
curl -X GET "http://localhost:6100/v1/entities?type=Will&q=client_id==CLIENT001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Retirement Planning
```bash
# Get retirement plans by age
curl -X GET "http://localhost:6100/v1/entities?type=RetirementPlan&q=retirement_age>=65" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get social security benefits
curl -X GET "http://localhost:6100/v1/entities?type=SocialSecurity&q=benefit_type==retirement" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get RMD calculations
curl -X GET "http://localhost:6100/v1/entities?type=RMD&q=year==2024" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Insurance Planning
```bash
# Get life insurance policies
curl -X GET "http://localhost:6100/v1/entities?type=Policy&q=policy_type==life" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get active coverage
curl -X GET "http://localhost:6100/v1/entities?type=Coverage&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get premium payments
curl -X GET "http://localhost:6100/v1/entities?type=Premium&q=frequency==annual" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Tax Planning
```bash
# Get current year tax plan
curl -X GET "http://localhost:6100/v1/entities?type=TaxPlan&q=tax_year==2024" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get tax deductions
curl -X GET "http://localhost:6100/v1/entities?type=Deduction&q=deduction_type==itemized" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get tax credits
curl -X GET "http://localhost:6100/v1/entities?type=Credit&q=credit_type==child_care" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Document Management
```bash
# Get client documents
curl -X GET "http://localhost:6100/v1/entities?type=Document&q=client_id==CLIENT001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get vault documents
curl -X GET "http://localhost:6100/v1/entities?type=Vault&q=security_level==high" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get document attachments
curl -X GET "http://localhost:6100/v1/entities?type=Attachment&q=document_id==DOC001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### User & Access Management
```bash
# Get active advisors
curl -X GET "http://localhost:6100/v1/entities?type=Advisor&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get user roles
curl -X GET "http://localhost:6100/v1/entities?type=Role&q=role_type==advisor" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get firm users
curl -X GET "http://localhost:6100/v1/entities?type=User&q=firm_id==FIRM001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

### Advanced Filtering
```bash
# Multiple filters
curl -X GET "http://localhost:6100/v1/entities?type=Client&q=status==active,client_type==individual" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Count entities
curl -X GET "http://localhost:6100/v1/entities?type=Account&options=count" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Pagination with firm filter
curl -X GET "http://localhost:6100/v1/entities?type=Client&limit=50&offset=100&firm_id=FIRM001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
```

## 🛠️ Development Architecture

### Factory Pattern
The server uses a factory pattern to handle different entity types:

```python
def get_entity_handler(entity_type: str, db: Session):
    handlers = {
        # Client & Relationship Management Service
        "Client": lambda: ClientHandler(db),
        "Contact": lambda: ContactHandler(db),
        "Household": lambda: HouseholdHandler(db),
        "Relationship": lambda: RelationshipHandler(db),
        
        # Financial Planning Service
        "FinancialPlan": lambda: FinancialPlanHandler(db),
        "Goal": lambda: GoalHandler(db),
        "Scenario": lambda: ScenarioHandler(db),
        "CashFlow": lambda: CashFlowHandler(db),
        
        # Account Management Service
        "Account": lambda: AccountHandler(db),
        "AccountType": lambda: AccountTypeHandler(db),
        "Investment": lambda: InvestmentHandler(db),
        "Liability": lambda: LiabilityHandler(db),
        
        # Asset Management Service
        "Asset": lambda: AssetHandler(db),
        "AssetClass": lambda: AssetClassHandler(db),
        "Allocation": lambda: AllocationHandler(db),
        "Security": lambda: SecurityHandler(db),
        
        # Spending & Budget Management Service
        "Spending": lambda: SpendingHandler(db),
        "Budget": lambda: BudgetHandler(db),
        "Expense": lambda: ExpenseHandler(db),
        "Income": lambda: IncomeHandler(db),
        
        # Estate Planning Service
        "Estate": lambda: EstateHandler(db),
        "Will": lambda: WillHandler(db),
        "Trust": lambda: TrustHandler(db),
        "Beneficiary": lambda: BeneficiaryHandler(db),
        
        # Retirement Planning Service
        "RetirementPlan": lambda: RetirementPlanHandler(db),
        "Pension": lambda: PensionHandler(db),
        "SocialSecurity": lambda: SocialSecurityHandler(db),
        "RMD": lambda: RMDHandler(db),
        
        # Insurance Planning Service
        "Insurance": lambda: InsuranceHandler(db),
        "Policy": lambda: PolicyHandler(db),
        "Coverage": lambda: CoverageHandler(db),
        "Premium": lambda: PremiumHandler(db),
        
        # Tax Planning Service
        "TaxPlan": lambda: TaxPlanHandler(db),
        "TaxBracket": lambda: TaxBracketHandler(db),
        "Deduction": lambda: DeductionHandler(db),
        "Credit": lambda: CreditHandler(db),
        
        # Document Management Service
        "Document": lambda: DocumentHandler(db),
        "Vault": lambda: VaultHandler(db),
        "FileType": lambda: FileTypeHandler(db),
        "Attachment": lambda: AttachmentHandler(db),
        
        # User & Access Management Service
        "User": lambda: UserHandler(db),
        "Role": lambda: RoleHandler(db),
        "Permission": lambda: PermissionHandler(db),
        "Advisor": lambda: AdvisorHandler(db),
        "Firm": lambda: FirmHandler(db),
    }
    return handlers.get(entity_type)
```

### Base Handler Class
All entity handlers extend `BaseEntityHandler`:

```python
class BaseEntityHandler(ABC):
    @abstractmethod
    def get_model(self):
        """Return SQLAlchemy model"""
        pass
    
    @abstractmethod
    def get_entity_type(self) -> str:
        """Return entity type name"""
        pass
    
    def get_entities(self, q, limit, offset, options, firm_id):
        """Common logic for all handlers"""
        # Shared implementation
```

### Adding New Entity Types

1. **Create SQLAlchemy Model** in `database.py`:
```python
class NewEntity(Base):
    __tablename__ = "new_entities"
    # ... model definition
    
    def to_emoney_entity(self):
        # Convert to eMoney format
        return {...}
```

2. **Create Handler** in `handlers/new_entity_handler.py`:
```python
class NewEntityHandler(BaseEntityHandler):
    def get_model(self):
        return NewEntity
    
    def get_entity_type(self) -> str:
        return "NewEntity"
    
    def _apply_filters(self, query, q, firm_id):
        # Entity-specific filtering logic
        if firm_id:
            query = query.filter(NewEntity.firm_id == firm_id)
        return query
```

3. **Add to Factory** in `handlers/entity_factory.py`:
```python
"NewEntity": lambda: NewEntityHandler(db),  # Add this line
```

4. **Update Exports** in `handlers/__init__.py`:
```python
from .new_entity_handler import NewEntityHandler
__all__ = [..., 'NewEntityHandler']
```

## 🗄️ Database

- **Engine:** PostgreSQL (production) / SQLite (development)
- **ORM:** SQLAlchemy 2.0
- **Auto-creation:** Tables created on startup
- **Seeding:** Faker-based sample data generation

### Entity Relationships
- **Firm** → Advisors, Users, Clients
- **Client** → Contacts, Households, Financial Plans, Accounts
- **FinancialPlan** → Goals, Scenarios, Cash Flows
- **Account** → Investments, Liabilities, Asset Allocations
- **Household** → Clients, Relationships, Budget
- **Advisor** → Clients, Financial Plans

### Database Schema Summary

- **Client & Relationship Management Service:** Client, Contact, Household, Relationship
- **Financial Planning Service:** FinancialPlan, Goal, Scenario, CashFlow
- **Account Management Service:** Account, AccountType, Investment, Liability
- **Asset Management Service:** Asset, AssetClass, Allocation, Security
- **Spending & Budget Management Service:** Spending, Budget, Expense, Income
- **Estate Planning Service:** Estate, Will, Trust, Beneficiary
- **Retirement Planning Service:** RetirementPlan, Pension, SocialSecurity, RMD
- **Insurance Planning Service:** Insurance, Policy, Coverage, Premium
- **Tax Planning Service:** TaxPlan, TaxBracket, Deduction, Credit
- **Document Management Service:** Document, Vault, FileType, Attachment
- **User & Access Management Service:** User, Role, Permission, Advisor, Firm

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL="postgresql://emoney:postgres@localhost:5432/emoney_mock"  # PostgreSQL
DATABASE_URL="sqlite:///./emoney_mock.db"  # SQLite (default)
BATCH_SIZE=100  # Default batch size for data extraction
```

### Docker Configuration
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: emoney_mock
      POSTGRES_USER: emoney
      POSTGRES_PASSWORD: postgres

  emoney-mock:
    build: .
    environment:
      - DATABASE_URL=postgresql://emoney:postgres@postgres:5432/emoney_mock
      - BATCH_SIZE=100
    ports:
      - "6100:6100"
```

## 🧪 Testing

### Docker Testing
```bash
# Full integration test
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Test all entity types
curl -X GET "http://localhost:6100/v1/entities?type=Client" \
  -H "X-API-Key: test" -H "X-API-Secret: test"
curl -X GET "http://localhost:6100/v1/entities?type=FinancialPlan" \
  -H "X-API-Key: test" -H "X-API-Secret: test"
curl -X GET "http://localhost:6100/v1/entities?type=Account" \
  -H "X-API-Key: test" -H "X-API-Secret: test"
curl -X GET "http://localhost:6100/v1/entities?type=Asset" \
  -H "X-API-Key: test" -H "X-API-Secret: test"
curl -X GET "http://localhost:6100/v1/entities?type=RetirementPlan" \
  -H "X-API-Key: test" -H "X-API-Secret: test"
```

### Sample Data Generation
```bash
# Generate fresh sample data
python seeder.py --clear

# Add data without clearing
python seeder.py
```

### Health Check
```bash
curl -X GET "http://localhost:6100/health"
```

## 🚦 Authentication

Currently uses simple API Key + Secret validation for development. Any non-empty headers are accepted.

For production, integrate with:
- OAuth2 with API Key/Secret
- JWT tokens with refresh mechanism
- Rate limiting per API key
- IP whitelisting

## 📊 Sample Data

The seeder generates realistic financial planning sample data using Faker:

- **3 Firms** with different sizes and specialties
- **10 Advisors** across firms with credentials
- **50 Clients** with diverse demographics and net worth
- **100 Contacts** with communication preferences
- **30 Households** with family structures
- **Financial Plans** with goals, scenarios, and projections
- **Accounts** including investment, retirement, and liability accounts
- **Asset Allocations** with equities, bonds, and alternatives
- **Budget & Spending** with income and expense tracking
- **Estate Plans** with wills, trusts, and beneficiaries
- **Retirement Plans** with social security and RMD calculations
- **Insurance Policies** covering life, health, and property
- **Tax Plans** with deductions and credits
- **Documents** in secure vaults with metadata

## 📋 Current Features and Implementation Status

### ✅ Core Infrastructure
- Factory pattern architecture with base handlers
- PostgreSQL/SQLite database support
- Docker containerization
- Health checks and monitoring
- Batch processing support

### ✅ Client & Relationship Management Service (Port 4731)
- Client, Contact, Household, Relationship entities
- Client lifecycle and status tracking
- Household grouping and dependencies

### ✅ Financial Planning Service (Port 4732)
- FinancialPlan, Goal, Scenario, CashFlow entities
- Multi-goal planning support
- What-if scenario analysis

### ✅ Account Management Service (Port 4733)
- Account, AccountType, Investment, Liability entities
- Multi-account aggregation
- Investment position tracking

### 🔄 Asset Management Service (Port 4734) - In Development
- Asset, AssetClass, Allocation, Security entities
- Portfolio rebalancing logic
- Performance analytics

### 🔄 Spending & Budget Management Service (Port 4735) - In Development
- Spending, Budget, Expense, Income entities
- Cash flow forecasting
- Budget variance analysis

### ✅ Estate Planning Service (Port 4736)
- Estate, Will, Trust, Beneficiary entities
- Estate tax calculations
- Beneficiary designations

### ✅ Retirement Planning Service (Port 4737)
- RetirementPlan, Pension, SocialSecurity, RMD entities
- Retirement income projections
- Social Security optimization

### ✅ Insurance Planning Service (Port 4738)
- Insurance, Policy, Coverage, Premium entities
- Coverage gap analysis
- Premium tracking

### ✅ Tax Planning Service (Port 4739)
- TaxPlan, TaxBracket, Deduction, Credit entities
- Tax projection scenarios
- Deduction optimization

### ✅ Document Management Service (Port 4708)
- Document, Vault, FileType, Attachment entities
- Secure document storage
- Version control

### ✅ User & Access Management Service (Port 4709)
- User, Role, Permission, Advisor, Firm entities
- Role-based access control
- Multi-firm support

### ✅ Development Tools
- Comprehensive seeder with realistic financial data
- Docker compose for easy development setup
- Extensible architecture for adding new entities

## 🚀 Future Enhancements

- [ ] Complete implementation of Asset Management analytics
- [ ] Complete implementation of Spending forecasting
- [ ] Add POST/PUT/DELETE endpoints for full CRUD operations
- [ ] Implement complex financial calculations (IRR, XIRR, Monte Carlo)
- [ ] Add proper OAuth2 authentication with API keys
- [ ] Add real-time data updates via WebSockets
- [ ] Add multi-firm isolation with firm_id enforcement
- [ ] Add comprehensive logging and audit trails
- [ ] Add unit and integration tests
- [ ] Add data export/import functionality (CSV, Excel, JSON)
- [ ] Add financial report generation
- [ ] Add regulatory compliance reporting (ADV, 1099, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-entity`)
3. Follow the architecture patterns (Base handler, Factory pattern)
4. Add comprehensive filtering and sample data
5. Update documentation for new entities
6. Test with Docker and sample data
7. Submit pull request


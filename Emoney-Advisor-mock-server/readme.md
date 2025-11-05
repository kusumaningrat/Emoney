eMoney Advisor Mock Server
A FastAPI-based mock implementation of eMoney Advisor APIs with clean architecture using factory pattern and base handler classes, designed for financial planning and wealth management functionality.
Features

Complete mock implementation of eMoney Advisor API services
Factory pattern architecture with entity-specific services
PostgreSQL/SQLite database support using SQLAlchemy ORM
Multiple service domains covering all financial planning aspects
Authentication using API key and secret
Realistic financial data generation using Faker
Docker containerization
Health check endpoints for monitoring

Project Structure
├── app.py                  # Main application entry point
├── database.py             # Database connection and session management
├── auth/                   # Authentication components
│   ├── __init__.py
│   └── dependencies.py     # Auth middlewares and helpers
├── model/                  # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── client.py           # Client & relationship models
│   ├── financial.py        # Financial planning models
│   ├── account.py          # Account management models
│   ├── asset.py            # Asset management models
│   ├── spending.py         # Spending & budget models
│   ├── estate.py           # Estate planning models
│   ├── retirement.py       # Retirement planning models
│   ├── insurance.py        # Insurance planning models
│   ├── tax.py              # Tax planning models
│   ├── document.py         # Document management models
│   └── identity.py         # User & access management models
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── entity.py           # Main entity endpoints
│   ├── admin.py            # Admin endpoints for database management
│   └── health.py           # Health check endpoints
├── schema/                 # Pydantic validation schemas
│   ├── __init__.py
│   ├── client.py           # Client & relationship schemas
│   ├── financial.py        # Financial planning schemas
│   ├── account.py          # Account management schemas
│   ├── asset.py            # Asset management schemas
│   ├── spending.py         # Spending & budget schemas
│   ├── estate.py           # Estate planning schemas
│   ├── retirement.py       # Retirement planning schemas
│   ├── insurance.py        # Insurance planning schemas
│   ├── tax.py              # Tax planning schemas
│   ├── document.py         # Document management schemas
│   └── identity.py         # User & access management schemas
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── entity_factory.py   # Factory function for entity services
│   ├── base_service.py     # Abstract base service class
│   ├── client.py           # Client & relationship services
│   ├── financial.py        # Financial planning services
│   ├── account.py          # Account management services
│   ├── asset.py            # Asset management services
│   ├── spending.py         # Spending & budget services
│   ├── estate.py           # Estate planning services
│   ├── retirement.py       # Retirement planning services
│   ├── insurance.py        # Insurance planning services
│   ├── tax.py              # Tax planning services
│   ├── document.py         # Document management services
│   ├── identity.py         # User & access management services
│   └── admin.py            # Admin service implementation
├── seeders/                # Data seed scripts
│   ├── __init__.py
│   ├── client_seeder.py    # Client & relationship seeders
│   ├── financial_seeder.py # Financial planning seeders
│   ├── account_seeder.py   # Account management seeders
│   ├── asset_seeder.py     # Asset management seeders
│   ├── spending_seeder.py  # Spending & budget seeders
│   ├── estate_seeder.py    # Estate planning seeders
│   ├── retirement_seeder.py # Retirement planning seeders
│   ├── insurance_seeder.py # Insurance planning seeders
│   ├── tax_seeder.py       # Tax planning seeders
│   ├── document_seeder.py  # Document management seeders
│   └── identity_seeder.py  # User & access management seeders
├── migrations/             # Alembic database migrations
├── alembic.ini             # Alembic configuration
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # This documentation
Getting Started
Prerequisites

Docker and Docker Compose

Running with Docker

Clone the repository
Build and start the containers:

bash   docker-compose up -d
```
3. Access the API at http://localhost:6100
4. Access the Swagger UI documentation at http://localhost:6100/docs
5. Access pgAdmin at http://localhost:6101 (credentials: admin@example.com / admin)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://emoney:postgres@postgres:5432/emoney_mock |
| API_KEY | API key for admin endpoints | test-api-key |
| API_SECRET | API secret for admin endpoints | test-api-secret |
| AUTO_SEED | Auto-seed database on startup | false |

## API Endpoints

### Entity Management Endpoints

- `GET /v1/entities` - Get entities with filtering and pagination support

### Admin Endpoints

- `POST /v1/admin/seed` - Seed the database with test data
- `POST /v1/admin/reset` - Reset the database by dropping and recreating tables
- `GET /v1/admin/status` - Get database status information

## Authentication

All endpoints require authentication using API key and secret headers:
```
X-API-Key: your-api-key
X-API-Secret: your-api-secret
Example:
bashcurl -X GET "http://localhost:6100/v1/entities?type=Client" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
Multi-Firm Support
The API supports multi-firm environments through the firm_id parameter:
bashcurl -X GET "http://localhost:6100/v1/entities?type=Client&firm_id=FIRM001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
Database Seeding
You can seed the database using the admin API. The seeding process creates:

3 Firms with different sizes and specialties
10 Advisors across firms with credentials
50 Clients with diverse demographics and net worth
100 Contacts with communication preferences
30 Households with family structures
Financial Plans with goals, scenarios, and projections
Accounts including investment, retirement, and liability accounts
Asset Allocations with equities, bonds, and alternatives
Budget & Spending with income and expense tracking
Estate Plans with wills, trusts, and beneficiaries
Retirement Plans with social security and RMD calculations
Insurance Policies covering life, health, and property
Tax Plans with deductions and credits
Documents in secure vaults with metadata

Example seeding command:
bash# Seed everything
curl -X POST -H "X-API-Key: test-api-key" -H "X-API-Secret: test-api-secret" \
  "http://localhost:6100/v1/admin/seed?entity_type=all"

# Seed specific entity types
curl -X POST -H "X-API-Key: test-api-key" -H "X-API-Secret: test-api-secret" \
  "http://localhost:6100/v1/admin/seed?entity_type=clients"
curl -X POST -H "X-API-Key: test-api-key" -H "X-API-Secret: test-api-secret" \
  "http://localhost:6100/v1/admin/seed?entity_type=accounts"
curl -X POST -H "X-API-Key: test-api-key" -H "X-API-Secret: test-api-secret" \
  "http://localhost:6100/v1/admin/seed?entity_type=financial_plans"
```

## Query Parameters

Most endpoints support filtering, pagination, and sorting:
```
GET /v1/entities?type=Client&q=status==active&limit=10&offset=0&options=count&firm_id=FIRM001
ParameterTypeRequiredDescriptiontypestringNoEntity type (e.g., Client, Account, Goal)qstringNoQuery filter (e.g., status==active)limitintegerNoNumber of results (default: 100)offsetintegerNoPagination offset (default: 0)optionsstringNoResponse options (count for count only)firm_idstringNoFilter by firm identifier
Supported Entity Types
Client & Relationship Management Service

Client - Primary client record with demographics and status
Contact - Contact information and communication preferences
Household - Household grouping and relationships
Relationship - Client relationships and dependencies

Financial Planning Service

FinancialPlan - Comprehensive financial planning data
Goal - Financial goals and objectives
Scenario - Planning scenarios and what-if analysis
CashFlow - Cash flow projections and analysis

Account Management Service

Account - Financial account information
AccountType - Account classification and types
Investment - Investment holdings and positions
Liability - Debt and liability tracking

Asset Management Service

Asset - Asset inventory and valuation
AssetClass - Asset classification structure
Allocation - Portfolio allocation strategies
Security - Security master data and pricing

Spending & Budget Management Service

Spending - Spending transactions and patterns
Budget - Budget planning and tracking
Expense - Expense categorization and management
Income - Income sources and tracking

Estate Planning Service

Estate - Estate planning overview
Will - Will documentation and directives
Trust - Trust structures and beneficiaries
Beneficiary - Beneficiary designations

Retirement Planning Service

RetirementPlan - Retirement planning scenarios
Pension - Pension benefits and projections
SocialSecurity - Social Security benefit calculations
RMD - Required minimum distribution tracking

Insurance Planning Service

Insurance - Insurance portfolio overview
Policy - Insurance policy details
Coverage - Coverage amounts and types
Premium - Premium payment tracking

Tax Planning Service

TaxPlan - Tax planning strategies
TaxBracket - Tax bracket analysis
Deduction - Tax deduction tracking
Credit - Tax credit management

Document Management Service

Document - Document storage and metadata
Vault - Secure document vault
FileType - Document classification
Attachment - File attachments and links

User & Access Management Service

User - System users and authentication
Role - Role-based access control
Permission - Permission definitions
Advisor - Financial advisor profiles
Firm - Firm/organization management

API Examples
Client & Relationship Management
bash# Get all active clients
curl -X GET "http://localhost:6100/v1/entities?type=Client&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get household members
curl -X GET "http://localhost:6100/v1/entities?type=Household&q=household_id==HH001" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
Financial Planning
bash# Get financial plans by status
curl -X GET "http://localhost:6100/v1/entities?type=FinancialPlan&q=status==active" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"

# Get retirement goals
curl -X GET "http://localhost:6100/v1/entities?type=Goal&q=goal_type==retirement" \
  -H "X-API-Key: test-api-key" \
  -H "X-API-Secret: test-api-secret"
Extending the API
To add more entity types or endpoints, follow this pattern:

Create model definitions in a new file under model/
Create schemas in a new file under schema/
Create service implementations in a new file under services/
Create routes in a new file under routes/ (if needed)
Create seeders in a new file under seeders/
Include the new routes in app.py

Development Architecture
Factory Pattern
The server uses a factory pattern to handle different entity types:
pythondef get_entity_service(entity_type: str, db: Session):
    services = {
        # Client & Relationship Management Service
        "Client": lambda: ClientService(db),
        "Contact": lambda: ContactService(db),
        # Additional services...
    }
    return services.get(entity_type)
Base Service Class
All entity services extend BaseEntityService:
pythonclass BaseEntityService(ABC):
    @abstractmethod
    def get_model(self):
        """Return SQLAlchemy model"""
        pass
    
    @abstractmethod
    def get_entity_type(self) -> str:
        """Return entity type name"""
        pass
    
    def get_entities(self, q, limit, offset, options, firm_id):
        """Common logic for all services"""
        # Shared implementation
Implementation Status
✅ Core Infrastructure

Factory pattern architecture with base services
PostgreSQL/SQLite database support
Docker containerization
Health checks and monitoring
Batch processing support

✅ Client & Relationship Management Service

Client, Contact, Household, Relationship entities
Client lifecycle and status tracking
Household grouping and dependencies

✅ Financial Planning Service

FinancialPlan, Goal, Scenario, CashFlow entities
Multi-goal planning support
What-if scenario analysis

✅ Account Management Service

Account, AccountType, Investment, Liability entities
Multi-account aggregation
Investment position tracking

🔄 Asset Management Service - In Development

Asset, AssetClass, Allocation, Security entities
Portfolio rebalancing logic
Performance analytics

🔄 Spending & Budget Management Service - In Development

Spending, Budget, Expense, Income entities
Cash flow forecasting
Budget variance analysis

✅ Estate Planning Service

Estate, Will, Trust, Beneficiary entities
Estate tax calculations
Beneficiary designations

✅ Retirement Planning Service

RetirementPlan, Pension, SocialSecurity, RMD entities
Retirement income projections
Social Security optimization

✅ Insurance Planning Service

Insurance, Policy, Coverage, Premium entities
Coverage gap analysis
Premium tracking

✅ Tax Planning Service

TaxPlan, TaxBracket, Deduction, Credit entities
Tax projection scenarios
Deduction optimization

✅ Document Management Service

Document, Vault, FileType, Attachment entities
Secure document storage
Version control

✅ User & Access Management Service

User, Role, Permission, Advisor, Firm entities
Role-based access control
Multi-firm support

Future Enhancements

 Complete implementation of Asset Management analytics
 Complete implementation of Spending forecasting
 Add POST/PUT/DELETE endpoints for full CRUD operations
 Implement complex financial calculations (IRR, XIRR, Monte Carlo)
 Add proper OAuth2 authentication with API keys
 Add real-time data updates via WebSockets
 Add multi-firm isolation with firm_id enforcement
 Add comprehensive logging and audit trails
 Add unit and integration tests
 Add data export/import functionality (CSV, Excel, JSON)
 Add financial report generation
 Add regulatory compliance reporting (ADV, 1099, etc.)

Development Notes
Using Alembic for Migrations
bash# Initialize migrations
alembic init migrations

# Generate a migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head

# Revert migrations
alembic downgrade -1
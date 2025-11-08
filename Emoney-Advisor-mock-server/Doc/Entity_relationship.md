Entity Relationships
Client & Relationship Management
Primary Entities

Client: Core entity representing clients in the system
Contact: Contact information for clients
Household: Groups of related clients/individuals
Relationship: Connections between clients (family, professional, etc.)

Relationship Details

A Client can have multiple Contact records (different addresses, phone numbers, etc.)
A Client can belong to one or more Household groups
Household can contain multiple Client members
Relationship connects two Client entities with a specific relationship type
A Client can have multiple Relationship connections to other clients

Financial Planning
Primary Entities

FinancialPlan: Overall financial strategy for a client
Goal: Financial objectives within a plan
Scenario: Alternative planning scenarios
CashFlow: Income and expense projections

Relationship Details

A Client can have multiple FinancialPlan records
A FinancialPlan contains multiple Goal entities
A FinancialPlan can model multiple Scenario alternatives
Each FinancialPlan has CashFlow projections
Goal entities belong to a specific FinancialPlan

Account Management
Primary Entities

Account: Financial accounts owned by clients
AccountType: Classification of account (checking, retirement, etc.)
Investment: Holdings within accounts
Liability: Debts and obligations

Relationship Details

A Client owns multiple Account records
Each Account has one AccountType
An Account can contain multiple Investment holdings
A Client can have multiple Liability records
Liability records are associated with a Client, sometimes linked to an Account

Asset Management
Primary Entities

Asset: Valuable items owned by clients
AssetClass: Classification of assets (equity, fixed income, etc.)
Allocation: Target distribution of investments
Security: Financial instruments for investment

Relationship Details

A Client owns multiple Asset entities
Each Asset belongs to an AssetClass
Allocation defines target distribution across AssetClass categories
Security represents investment vehicles available within Investment records

Spending & Budget Management
Primary Entities

Spending: Client spending records
Budget: Planned expenditure limits
Expense: Individual spending transactions
Income: Sources of client income

Relationship Details

A Client has Spending records that track overall expenditures
Each Client can have a Budget with multiple categories
Expense records track individual spending items linked to Spending
Income sources are associated with a Client and feed into CashFlow

Estate Planning
Primary Entities

Estate: Overall estate plan for a client
Will: Legal will document
Trust: Trust arrangements
Beneficiary: Recipients of estate assets

Relationship Details

A Client has one Estate record
An Estate can include one Will
An Estate can have multiple Trust arrangements
Beneficiary records are linked to Estate, Will, or Trust entities

Retirement Planning
Primary Entities

RetirementPlan: Retirement strategy
Pension: Pension benefits
SocialSecurity: Social security benefits
RMD: Required minimum distributions

Relationship Details

A Client can have one or more RetirementPlan records
A RetirementPlan can include multiple Pension benefits
A RetirementPlan includes SocialSecurity benefit projections
RMD calculations are linked to retirement accounts and the RetirementPlan

Insurance Planning
Primary Entities

Insurance: Overall insurance portfolio
Policy: Individual insurance policies
Coverage: Specific coverage details
Premium: Payment records for policies

Relationship Details

A Client has one Insurance portfolio record
An Insurance portfolio contains multiple Policy records
Each Policy has multiple Coverage details
Premium payments are linked to specific Policy records

Tax Planning
Primary Entities

TaxPlan: Overall tax strategy
TaxBracket: Tax rate information
Deduction: Tax deductions
Credit: Tax credits

Relationship Details

A Client can have multiple TaxPlan records (typically one per year)
TaxPlan references applicable TaxBracket information
A TaxPlan includes multiple Deduction records
A TaxPlan includes multiple Credit records

Cross-Service Relationships

FinancialPlan references Account, Asset, and RetirementPlan data
RetirementPlan may reference Account data for retirement accounts
TaxPlan may reference Income, Deduction, and financial account information
Estate planning references Asset, Account, and Beneficiary information
All entities are ultimately associated with Client records

This structure enables a comprehensive financial advisory system where multiple specialized services can work together to provide a complete picture of a client's financial situation and strategies.
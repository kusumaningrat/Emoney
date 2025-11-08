# enums.py
import enum

class AccountType(str, enum.Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"
    BROKERAGE = "Brokerage"
    RETIREMENT = "Retirement"
    COLLEGE = "College Savings"
    HSA = "Health Savings"
    MORTGAGE = "Mortgage"
    LOAN = "Loan"
    CREDIT_CARD = "Credit Card"
    OTHER = "Other"

class OwnershipType(str, enum.Enum):
    CLIENT = "Client"
    SPOUSE = "Spouse"
    JOINT = "Joint"
    TRUST = "Trust"
    BUSINESS = "Business"
    OTHER = "Other"

class TaxStatus(str, enum.Enum):
    TAXABLE = "Taxable"
    TAX_DEFERRED = "Tax-Deferred"
    TAX_FREE = "Tax-Free"

class LiabilityType(str, enum.Enum):
    MORTGAGE = "Mortgage"
    LOAN = "Loan"
    CREDIT_CARD = "Credit Card"
    LINE_OF_CREDIT = "Line of Credit"
    OTHER = "Other"

class PaymentFrequency(str, enum.Enum):
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"

class AssetType(str, enum.Enum):
    REAL_ESTATE = "Real Estate"
    RETIREMENT = "Retirement"
    INVESTMENT = "Investment"
    CASH = "Cash"
    VEHICLE = "Vehicle"
    BUSINESS = "Business"
    PERSONAL = "Personal Property"
    OTHER = "Other"

class MaritalStatus(str, enum.Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"

class ClientStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    FORMER = "Former"

class PlanType(str, enum.Enum):
    BASE = "Base Facts"
    SCENARIO = "Advanced Planning Scenario"
    WHAT_IF = "What-If"

class DocumentType(str, enum.Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    JPG = "JPG"
    PNG = "PNG"
    ZIP = "ZIP"
    TXT = "TXT"
    OTHER = "OTHER"

class AlertSeverity(str, enum.Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

class AlertType(str, enum.Enum):
    SYSTEM = "System"
    CLIENT = "Client"
    PLAN = "Plan"

class AlertStatus(str, enum.Enum):
    ACTIVE = "Active"
    DISMISSED = "Dismissed"

class TaskPriority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TaskStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class EstateDocumentType(str, enum.Enum):
    WILL = "Will"
    TRUST = "Trust"
    POWER_OF_ATTORNEY = "Power of Attorney"
    HEALTHCARE_DIRECTIVE = "Healthcare Directive"
    BENEFICIARY_DESIGNATION = "Beneficiary Designation"
    DEED = "Deed"
    OTHER = "Other"

class EstateStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    ARCHIVED = "Archived"
    EXECUTED = "Executed"

class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"

class LogonStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    LOCKED = "Locked"

class InsuranceType(str, enum.Enum):
    LIFE = "Life"
    HEALTH = "Health"
    DISABILITY = "Disability"
    LONG_TERM_CARE = "Long-Term Care"
    PROPERTY = "Property"
    OTHER = "Other"

class InsuranceStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"

class RetirementPlanStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PLANNING = "Planning"
    EXECUTED = "Executed"

class IncomeType(str, enum.Enum):
    SALARY = "Salary"
    BONUS = "Bonus"
    SELF_EMPLOYMENT = "Self-Employment"
    RENTAL = "Rental"
    INVESTMENT = "Investment"
    PENSION = "Pension"
    SOCIAL_SECURITY = "Social Security"
    OTHER = "Other"

class ExpenseCategory(str, enum.Enum):
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    FOOD = "Food"
    HEALTHCARE = "Healthcare"
    ENTERTAINMENT = "Entertainment"
    DEBT = "Debt"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    INSURANCE = "Insurance"
    PERSONAL = "Personal"
    UTILITIES = "Utilities"
    GIFTS = "Gifts & Donations"
    OTHER = "Other"

class FrequencyType(str, enum.Enum):
    ANNUAL = "Annual"
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"
    ONE_TIME = "One-time"

class TaxDocumentType(str, enum.Enum):
    W2 = "W-2"
    TEN99 = "1099"
    TEN98 = "1098"
    FIVE_HUNDRED = "Schedule 500"
    TAX_RETURN = "Tax Return"
    EXTENSION = "Filing Extension"
    PROPERTY_TAX = "Property Tax"
    OTHER = "Other"

class TaxFilingStatus(str, enum.Enum):
    SINGLE = "Single"
    MARRIED_JOINT = "Married Filing Jointly"
    MARRIED_SEPARATE = "Married Filing Separately"
    HEAD_HOUSEHOLD = "Head of Household"
    QUALIFYING_WIDOW = "Qualifying Widow(er)"
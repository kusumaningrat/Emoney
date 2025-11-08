from enum import Enum


class AccountType(str, Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"
    BROKERAGE = "Brokerage"
    RETIREMENT = "Retirement"
    COLLEGE = "College Savings"
    HSA = "Health Savings"
    OTHER = "Other"


class OwnershipType(str, Enum):
    CLIENT = "Client"
    SPOUSE = "Spouse"
    JOINT = "Joint"
    TRUST = "Trust"
    BUSINESS = "Business"
    OTHER = "Other"


class TaxStatus(str, Enum):
    TAXABLE = "Taxable"
    TAX_DEFERRED = "Tax-Deferred"
    TAX_FREE = "Tax-Free"


class LiabilityType(str, Enum):
    MORTGAGE = "Mortgage"
    LOAN = "Loan"
    CREDIT_CARD = "Credit Card"
    LINE_OF_CREDIT = "Line of Credit"
    OTHER = "Other"


class PaymentFrequency(str, Enum):
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"


class AssetType(str, Enum):
    REAL_ESTATE = "Real Estate"
    RETIREMENT = "Retirement"
    INVESTMENT = "Investment"
    CASH = "Cash"
    VEHICLE = "Vehicle"
    BUSINESS = "Business"
    PERSONAL = "Personal Property"
    OTHER = "Other"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"


class ClientStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    FORMER = "Former"


class DocumentType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    JPG = "JPG"
    PNG = "PNG"
    ZIP = "ZIP"
    TXT = "TXT"
    OTHER = "OTHER"


class AlertSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertType(str, Enum):
    SYSTEM = "System"
    CLIENT = "Client"
    PLAN = "Plan"


class AlertStatus(str, Enum):
    ACTIVE = "Active"
    DISMISSED = "Dismissed"


class TaskPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class EstateStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    ARCHIVED = "Archived"
    EXECUTED = "Executed"


class InsuranceStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class RetirementPlanStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PLANNING = "Planning"
    EXECUTED = "Executed"


class IncomeType(str, Enum):
    SALARY = "Salary"
    BONUS = "Bonus"
    SELF_EMPLOYMENT = "Self-Employment"
    RENTAL = "Rental"
    INVESTMENT = "Investment"
    PENSION = "Pension"
    SOCIAL_SECURITY = "Social Security"
    OTHER = "Other"


class ExpenseCategory(str, Enum):
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


class FrequencyType(str, Enum):
    ANNUAL = "Annual"
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"
    ONE_TIME = "One-time"
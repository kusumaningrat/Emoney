# services/entity_factory.py

from sqlalchemy.orm import Session

from .service_base import BaseService
from .client_service import ClientService
from .account_service import AccountService
from .asset_service import AssetService
from .financial_service import FinancialPlanService
from .estate_service import EstateService
from .insurance_service import InsuranceService
from .retirement_service import RetirementService
from .spending_service import SpendingService
from .tax_service import TaxService
from .user_service import UserService
from .document_service import DocumentService

def get_entity_service(entity_type: str, db: Session):
    """
    Factory function to get the appropriate service based on entity type
    """
    # Convert to title case to handle case-insensitivity
    entity_type = entity_type.title()
    
    services = {
        # Client & Relationship Management Services
        "Client": lambda: ClientService(db),
        "Spouse": lambda: SpouseService(db),
        "Contact": lambda: ContactService(db),
        "Household": lambda: HouseholdService(db),
        "Householdmember": lambda: HouseholdMemberService(db),
        "Household_member": lambda: HouseholdMemberService(db),
        "Household Member": lambda: HouseholdMemberService(db),
        
        # Account Management Services
        "Account": lambda: AccountService(db),
        "Liability": lambda: LiabilityService(db),
        "Accounttype": lambda: AccountTypeService(db),
        "Account_type": lambda: AccountTypeService(db),
        "Account Type": lambda: AccountTypeService(db),
        
        # Asset Management Services
        "Asset": lambda: AssetService(db),
        "Assetclass": lambda: AssetClassService(db),
        "Asset_class": lambda: AssetClassService(db),
        "Asset Class": lambda: AssetClassService(db),
        "Allocation": lambda: AllocationService(db),
        "Security": lambda: SecurityService(db),
        "Holding": lambda: HoldingService(db),
        
        # Financial Planning Services
        "Financialplan": lambda: FinancialPlanService(db),
        "Financial_plan": lambda: FinancialPlanService(db), 
        "Financial Plan": lambda: FinancialPlanService(db),
        "Financial": lambda: FinancialPlanService(db),
        "Goal": lambda: GoalService(db),
        "Montecarlo": lambda: MonteCarloService(db), 
        "Monte_carlo": lambda: MonteCarloService(db),
        "Monte Carlo": lambda: MonteCarloService(db),
        "Projection": lambda: ProjectionService(db),
        "Cashflow": lambda: CashFlowService(db),
        "Cash_flow": lambda: CashFlowService(db),
        "Cash Flow": lambda: CashFlowService(db),
        "Planincome": lambda: PlanIncomeService(db),
        "Plan_income": lambda: PlanIncomeService(db),
        "Plan Income": lambda: PlanIncomeService(db),
        "Taxplan": lambda: TaxPlanService(db),
        "Tax_plan": lambda: TaxPlanService(db),
        "Tax Plan": lambda: TaxPlanService(db),
        "Taxdeduction": lambda: TaxDeductionService(db),
        "Tax_deduction": lambda: TaxDeductionService(db),
        "Tax Deduction": lambda: TaxDeductionService(db),
        "Taxcredit": lambda: TaxCreditService(db),
        "Tax_credit": lambda: TaxCreditService(db),
        "Tax Credit": lambda: TaxCreditService(db),
        "Insuranceplan": lambda: InsurancePlanService(db),
        "Insurance_plan": lambda: InsurancePlanService(db),
        "Insurance Plan": lambda: InsurancePlanService(db),
        "Policy": lambda: PolicyService(db),
        
        # Estate Planning Services
        "Estate": lambda: EstateService(db),
        "Will": lambda: WillService(db),
        "Trust": lambda: TrustService(db),
        "Beneficiary": lambda: BeneficiaryService(db),
        
        # Insurance Services
        "Insurance": lambda: InsuranceService(db),
        "Insurancepolicy": lambda: InsurancePolicyService(db),
        "Insurance_policy": lambda: InsurancePolicyService(db),
        "Insurance Policy": lambda: InsurancePolicyService(db),
        "Coverage": lambda: CoverageService(db),
        "Premium": lambda: PremiumService(db),
        
        # Retirement Planning Services
        "Retirementplan": lambda: RetirementService(db),
        "Retirement_plan": lambda: RetirementService(db),
        "Retirement Plan": lambda: RetirementService(db),
        "Retirement": lambda: RetirementService(db),
        "Pension": lambda: PensionService(db),
        "Socialsecurity": lambda: SocialSecurityService(db),
        "Social_security": lambda: SocialSecurityService(db),
        "Social Security": lambda: SocialSecurityService(db),
        "Rmd": lambda: RMDService(db),
        
        # Spending Services
        "Spending": lambda: SpendingService(db),
        "Budget": lambda: BudgetService(db),
        "Income": lambda: IncomeService(db),
        "Expense": lambda: ExpenseService(db),
        "Budgetcategory": lambda: BudgetCategoryService(db),
        "Budget_category": lambda: BudgetCategoryService(db),
        "Budget Category": lambda: BudgetCategoryService(db),
        
        # Tax Services
        "Tax": lambda: TaxService(db),
        "Taxdocument": lambda: TaxDocumentService(db),
        "Tax_document": lambda: TaxDocumentService(db),
        "Tax Document": lambda: TaxDocumentService(db),
        "Taxpayment": lambda: TaxPaymentService(db),
        "Tax_payment": lambda: TaxPaymentService(db),
        "Tax Payment": lambda: TaxPaymentService(db),
        "Taxdeduction": lambda: TaxDeductionService(db),
        "Tax_deduction": lambda: TaxDeductionService(db),
        "Tax Deduction": lambda: TaxDeductionService(db),
        
        # User & Access Management Services
        "User": lambda: UserService(db),
        "Role": lambda: RoleService(db),
        "Permission": lambda: PermissionService(db),
        "Firm": lambda: FirmService(db),
        "Logon": lambda: LogonService(db),
        
        # Document Management Services
        "Vaultdocument": lambda: DocumentService(db),
        "Vault_document": lambda: DocumentService(db),
        "Vault Document": lambda: DocumentService(db),
        "Document": lambda: DocumentService(db),
        "Note": lambda: NoteService(db),
        "Task": lambda: TaskService(db),
        "Alert": lambda: AlertService(db),
    }
    
    service_creator = services.get(entity_type)
    if service_creator:
        return service_creator()
    else:
        raise ValueError(f"No service found for entity type: {entity_type}")

class ServiceFactory:
    """
    Factory class to manage service instances
    """
    def __init__(self, db: Session):
        self.db = db
        self._services = {}
    
    def get_service(self, entity_type: str):
        """
        Get service instance for the given entity type
        Caches service instances to avoid creating duplicates
        """
        entity_type = entity_type.title()
        
        if entity_type not in self._services:
            self._services[entity_type] = get_entity_service(entity_type, self.db)
            
        return self._services[entity_type]

# Helper functions for each service type
def get_client_service(db: Session):
    return ClientService(db)

def get_spouse_service(db: Session):
    return SpouseService(db)

def get_account_service(db: Session):
    return AccountService(db)

def get_asset_service(db: Session):
    return AssetService(db)

def get_financial_plan_service(db: Session):
    return FinancialPlanService(db)

def get_estate_service(db: Session):
    return EstateService(db)

def get_insurance_service(db: Session):
    return InsuranceService(db)

def get_retirement_service(db: Session):
    return RetirementService(db)

def get_spending_service(db: Session):
    return SpendingService(db)

def get_tax_service(db: Session):
    return TaxService(db)

def get_user_service(db: Session):
    return UserService(db)

def get_document_service(db: Session):
    return DocumentService(db)
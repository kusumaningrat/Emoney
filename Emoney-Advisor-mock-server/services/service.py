# services/service.py

from sqlalchemy.orm import Session

from .client_service import ClientService
from .account_service import AccountService
from .asset_service import AssetService
from .financial_plan_service import FinancialPlanService
from .estate_service import EstateService
from .insurance_service import InsuranceService
from .retirement_service import RetirementService
from .spending_service import SpendingService
from .tax_service import TaxService
from .user_service import UserService, FirmService, RoleService
from .document_service import DocumentService, NoteService, TaskService, AlertService

class Service:
    """
    Main service class that provides access to all services
    """
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize all services
        self.client = ClientService(db)
        self.account = AccountService(db)
        self.asset = AssetService(db)
        self.financial_plan = FinancialPlanService(db)
        self.estate = EstateService(db)
        self.insurance = InsuranceService(db)
        self.retirement = RetirementService(db)
        self.spending = SpendingService(db)
        self.tax = TaxService(db)
        self.user = UserService(db)
        self.firm = FirmService(db)
        self.role = RoleService(db)
        self.document = DocumentService(db)
        self.note = NoteService(db)
        self.task = TaskService(db)
        self.alert = AlertService(db)